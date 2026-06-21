from fastapi import APIRouter
from services.database import check_database_health

router = APIRouter(prefix="/database", tags=["database"])


@router.get("/health")
def database_health_check():
    """Check database connection health"""
    is_healthy = check_database_health()
    return {"status": "healthy" if is_healthy else "unhealthy", "service": "database"}