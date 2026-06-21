import asyncio
import logging
import os
import time
from pathlib import Path

from core.config import settings
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.pool import NullPool

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    pass


def _is_mssql_url(raw_url: str) -> bool:
    """Check if the database URL targets MSSQL."""
    try:
        url = make_url(raw_url)
        return "mssql" in (url.drivername or "")
    except Exception:
        return False


def _build_sqlite_fallback_url() -> str:
    """Build a SQLite URL pointing to a local file in the project root."""
    db_path = Path(__file__).resolve().parent.parent / "medipredict.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    sqlite_url = f"sqlite:///{db_path.as_posix()}"
    logger.info(f"Using SQLite fallback database: {sqlite_url}")
    return sqlite_url


class DatabaseManager:
    """Database manager supporting SQL Server (pymssql) with auto-fallback to SQLite."""

    def __init__(self):
        self.engine = None
        self._initialized = False
        self.session_maker = None
        self._init_lock = asyncio.Lock()
        self._table_creation_lock = asyncio.Lock()
        self._using_sqlite = False

    def _normalize_database_url(self, raw_url: str) -> str:
        """Normalize database URL for SQL Server with pymssql."""
        if not _is_mssql_url(raw_url):
            return raw_url

        try:
            url = make_url(raw_url)
        except Exception as e:
            logger.error(f"Failed to parse database URL: {e}")
            return raw_url

        drivername = url.drivername or ""

        if "+pymssql" in drivername:
            return url.render_as_string(hide_password=False)

        url = url.set(drivername="mssql+pymssql")
        clean_query = {k: v for k, v in url.query.items()
                      if k.lower() not in ("driver", "trustservercertificate")}
        url = url.set(query=clean_query)

        normalized = url.render_as_string(hide_password=False)
        if normalized != raw_url:
            logger.info("Adjusted database URL for pymssql compatibility")
        return normalized

    def _ensure_database_exists(self, raw_url: str) -> bool:
        """Create the SQL Server database if it doesn't exist.

        Returns True if the database exists or was created, False otherwise.
        """
        if not _is_mssql_url(raw_url):
            return True

        url = make_url(raw_url)
        database = url.database
        if not database:
            return True

        master_url = url.set(database="master")
        master_str = master_url.render_as_string(hide_password=False)

        try:
            engine = create_engine(master_str, poolclass=NullPool)
            with engine.connect() as conn:
                conn.execute(
                    text(f"IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = N'{database}') CREATE DATABASE [{database}]")
                )
                conn.commit()
                logger.info(f"Ensured database `{database}` exists")
            engine.dispose()
        except Exception as e:
            logger.warning(f"Could not auto-create database `{database}`: {e}")
            return False

        return True

    def _try_create_engine(self, database_url: str) -> bool:
        """Attempt to create a database engine for the given URL. Returns True on success."""
        try:
            logger.info(f"Creating database engine: {database_url}")
            engine_kwargs = {"echo": settings.debug}

            if _is_mssql_url(database_url):
                is_lambda = bool(
                    os.environ.get("AWS_LAMBDA_FUNCTION_NAME")
                    or os.environ.get("IS_LAMBDA", "").lower() in ("true", "1", "yes")
                )
                if is_lambda:
                    engine_kwargs["poolclass"] = NullPool
                else:
                    engine_kwargs["pool_pre_ping"] = True
                    engine_kwargs["pool_size"] = 10
                    engine_kwargs["max_overflow"] = 20
                    engine_kwargs["pool_recycle"] = 3600
                    engine_kwargs["pool_timeout"] = 30

                # First try connecting to the target database
                self.engine = create_engine(database_url, **engine_kwargs)
                try:
                    with self.engine.connect() as conn:
                        conn.execute(text("SELECT 1"))
                except Exception:
                    # If target database doesn't exist, try creating it via master
                    self.engine.dispose()
                    self.engine = None
                    url = make_url(database_url)
                    database = url.database
                    if database:
                        logger.info(f"Database '{database}' not found, attempting to create it...")
                        master_url = url.set(database="master")
                        master_str = master_url.render_as_string(hide_password=False)
                        try:
                            master_engine = create_engine(
                                master_str,
                                poolclass=NullPool,
                                isolation_level="AUTOCOMMIT",
                            )
                            with master_engine.connect() as conn:
                                conn.execute(
                                    text(f"IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = N'{database}') CREATE DATABASE [{database}]")
                                )
                                logger.info(f"Created database `{database}`")
                            master_engine.dispose()
                        except Exception as create_err:
                            logger.warning(f"Could not create database '{database}': {create_err}")
                    # Retry with target database
                    self.engine = create_engine(database_url, **engine_kwargs)
                    with self.engine.connect() as conn:
                        conn.execute(text("SELECT 1"))
            else:
                # SQLite: use NullPool to avoid threading issues
                engine_kwargs["poolclass"] = NullPool
                self.engine = create_engine(database_url, **engine_kwargs)
                with self.engine.connect() as conn:
                    conn.execute(text("SELECT 1"))

            self.session_maker = sessionmaker(self.engine, expire_on_commit=False)
            logger.info("Database engine and session maker created successfully")
            return True
        except Exception as e:
            logger.warning(f"Failed to create database engine: {e}")
            if self.engine:
                self.engine.dispose()
                self.engine = None
            return False

    async def init_db(self):
        logger.info("Starting database initialization...")

        async with self._init_lock:
            if self.engine is not None:
                logger.info("Database already initialized")
                return

        if not settings.database_url:
            logger.error("No database URL provided. DATABASE_URL environment variable must be set.")
            raise ValueError("DATABASE_URL environment variable is required")

        database_url = self._normalize_database_url(settings.database_url)

        # Try MSSQL first if configured
        if _is_mssql_url(database_url):
            if self._try_create_engine(database_url):
                return
            logger.warning("SQL Server unavailable, falling back to SQLite...")

        # Fallback to SQLite
        sqlite_url = _build_sqlite_fallback_url()
        self._using_sqlite = True
        if not self._try_create_engine(sqlite_url):
            raise RuntimeError("Failed to create any database engine (tried SQL Server and SQLite)")

    async def close_db(self):
        if not self.engine:
            return
        try:
            self.engine.dispose()
            logger.info("Database connection closed and engine disposed")
        except Exception as e:
            logger.warning(f"Error disposing database engine: {e}")
        finally:
            self.engine = None
            self.session_maker = None
            self._initialized = False
            self._using_sqlite = False

    async def create_tables(self):
        start_time = time.time()
        logger.debug("[DB_OP] Starting create_tables")
        await self._table_creation_lock.acquire()
        try:
            if self._initialized:
                logger.info("Tables already initialized")
                return
            if not self.engine:
                logger.error("Database engine not initialized")
                raise RuntimeError("Database engine not initialized")

            try:
                logger.info("Starting table creation...")
                Base.metadata.create_all(self.engine)
                self._initialized = True
                logger.info("Tables initialized successfully")
                logger.debug(f"[DB_OP] Create tables completed in {time.time() - start_time:.4f}s")
            except Exception as e:
                error_str = str(e).lower()
                if "already exists" in error_str or "there is already an object" in error_str:
                    self._initialized = True
                    logger.info(f"Tables already exist, ignored: {e}")
                else:
                    logger.error(f"Failed to create tables: {e}")
                    raise
        finally:
            self._table_creation_lock.release()

    async def ensure_initialized(self):
        if self.session_maker is not None:
            return
        async with self._init_lock:
            if self.session_maker is not None:
                return
            logger.warning("Database not initialized, attempting lazy initialization...")
        try:
            await self.init_db()
            await self.create_tables()
            logger.info("Lazy database initialization completed successfully")
        except Exception as e:
            logger.error(f"Failed to lazy initialize database: {e}", exc_info=True)
            raise


db_manager = DatabaseManager()


def get_db():
    """FastAPI dependency for database session."""
    if not db_manager.session_maker:
        raise RuntimeError("Database not initialized")
    session = db_manager.session_maker()
    try:
        yield session
    except Exception as e:
        session.rollback()
        logger.error(f"Database session error: {e}", exc_info=True)
        raise
    finally:
        session.close()