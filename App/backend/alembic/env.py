#!/usr/bin/env python
# -*- coding: utf-8 -*-

import importlib
import pkgutil
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine, pool


def clear_backend_import_cache():
    roots = ("core.database", "models")
    prefixes = tuple(f"{root}." for root in roots)
    for module_name in list(sys.modules):
        if module_name in roots or module_name.startswith(prefixes):
            sys.modules.pop(module_name, None)
    importlib.invalidate_caches()


clear_backend_import_cache()
from core.database import Base
import models

# Automatically import all ORM models under Models
for _, module_name, _ in pkgutil.iter_modules(models.__path__):
    importlib.import_module(f"{models.__name__}.{module_name}")

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def alembic_include_object(object, name, type_, reflected, compare_to):
    if type_ == "table" and name in ["sessions"]:
        return False
    return True


def run_migrations_online():
    connectable = create_engine(config.get_main_option("sqlalchemy.url"), poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
            include_object=alembic_include_object,
        )
        with connection.begin():
            context.run_migrations()
    connectable.dispose()


run_migrations_online()