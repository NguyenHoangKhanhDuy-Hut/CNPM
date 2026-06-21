import logging
from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException, Query

from services.openfda import OpenFDAService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/openfda", tags=["openfda"])


@router.get("/label")
async def get_drug_label(
    search: str = Query(..., description="Search query for drug label"),
    limit: int = Query(10, ge=1, le=100),
    skip: int = Query(0, ge=0),
):
    service = OpenFDAService()
    result = await service.search_drug_label(search=search, limit=limit, skip=skip)
    if result.get("error"):
        raise HTTPException(status_code=result.get("status", 500), detail=result.get("detail", "openFDA API error"))
    return result


@router.get("/events")
async def get_drug_events(
    search: str = Query(..., description="Search query for adverse events"),
    limit: int = Query(10, ge=1, le=100),
    skip: int = Query(0, ge=0),
):
    service = OpenFDAService()
    result = await service.search_drug_events(search=search, limit=limit, skip=skip)
    if result.get("error"):
        raise HTTPException(status_code=result.get("status", 500), detail=result.get("detail", "openFDA API error"))
    return result


@router.get("/recalls")
async def get_drug_recalls(
    search: str = Query("", description="Search query for drug recalls"),
    limit: int = Query(10, ge=1, le=100),
    skip: int = Query(0, ge=0),
):
    service = OpenFDAService()
    result = await service.search_drug_recalls(search=search, limit=limit, skip=skip)
    if result.get("error"):
        raise HTTPException(status_code=result.get("status", 500), detail=result.get("detail", "openFDA API error"))
    return result


@router.get("/ndc")
async def get_ndc(
    search: str = Query(..., description="Search query for NDC directory"),
    limit: int = Query(10, ge=1, le=100),
    skip: int = Query(0, ge=0),
):
    service = OpenFDAService()
    result = await service.search_ndc(search=search, limit=limit, skip=skip)
    if result.get("error"):
        raise HTTPException(status_code=result.get("status", 500), detail=result.get("detail", "openFDA API error"))
    return result


@router.get("/enrich")
async def enrich_drug(
    brand_name: str = Query("", description="Brand name of the drug"),
    generic_name: str = Query("", description="Generic name of the drug"),
):
    if not brand_name and not generic_name:
        raise HTTPException(status_code=400, detail="Either brand_name or generic_name is required")
    service = OpenFDAService()
    result = await service.enrich_drug_info(brand_name=brand_name, generic_name=generic_name)
    return result
