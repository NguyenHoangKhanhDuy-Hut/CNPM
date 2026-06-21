from typing import Annotated

from core.database import get_db
from fastapi import Depends
from sqlalchemy.orm import Session

# Database session dependency
DbSession = Annotated[Session, Depends(get_db)]
