import json
import logging
from typing import List, Optional

from datetime import datetime, date

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from core.database import get_db
from services.diseases import DiseasesService

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/entities/diseases", tags=["diseases"])


# ---------- Pydantic Schemas ----------
class DiseasesData(BaseModel):
    """Entity data schema (for create/update)"""
    name: str
    group_name: str
    risk_level: str
    icon: str = None
    description: str
    symptoms: str = None
    causes: str = None
    diagnosis: str = None
    treatment: str = None


class DiseasesUpdateData(BaseModel):
    """Update entity data (partial updates allowed)"""
    name: Optional[str] = None
    group_name: Optional[str] = None
    risk_level: Optional[str] = None
    icon: Optional[str] = None
    description: Optional[str] = None
    symptoms: Optional[str] = None
    causes: Optional[str] = None
    diagnosis: Optional[str] = None
    treatment: Optional[str] = None


class DiseasesResponse(BaseModel):
    """Entity response schema"""
    id: int
    name: str
    group_name: str
    risk_level: str
    icon: Optional[str] = None
    description: str
    symptoms: Optional[str] = None
    causes: Optional[str] = None
    diagnosis: Optional[str] = None
    treatment: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DiseasesListResponse(BaseModel):
    """List response schema"""
    items: List[DiseasesResponse]
    total: int
    skip: int
    limit: int


class DiseasesBatchCreateRequest(BaseModel):
    """Batch create request"""
    items: List[DiseasesData]


class DiseasesBatchUpdateItem(BaseModel):
    """Batch update item"""
    id: int
    updates: DiseasesUpdateData


class DiseasesBatchUpdateRequest(BaseModel):
    """Batch update request"""
    items: List[DiseasesBatchUpdateItem]


class DiseasesBatchDeleteRequest(BaseModel):
    """Batch delete request"""
    ids: List[int]


# ---------- Routes ----------
@router.get("", response_model=DiseasesListResponse)
def query_diseasess(
    query: str = Query(None, description="Query conditions (JSON string)"),
    sort: str = Query(None, description="Sort field (prefix with '-' for descending)"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=2000, description="Max number of records to return"),
    fields: str = Query(None, description="Comma-separated list of fields to return"),
    db: Session = Depends(get_db),
):
    """Query diseasess with filtering, sorting, and pagination"""
    logger.debug(f"Querying diseasess: query={query}, sort={sort}, skip={skip}, limit={limit}, fields={fields}")
    
    service = DiseasesService(db)
    try:
        # Parse query JSON if provided
        query_dict = None
        if query:
            try:
                query_dict = json.loads(query)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid query JSON format")
        
        result = service.get_list(
            skip=skip, 
            limit=limit,
            query_dict=query_dict,
            sort=sort,
        )
        logger.debug(f"Found {result['total']} diseasess")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error querying diseasess: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/all", response_model=DiseasesListResponse)
def query_diseasess_all(
    query: str = Query(None, description="Query conditions (JSON string)"),
    sort: str = Query(None, description="Sort field (prefix with '-' for descending)"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=2000, description="Max number of records to return"),
    fields: str = Query(None, description="Comma-separated list of fields to return"),
    db: Session = Depends(get_db),
):
    # Query diseasess with filtering, sorting, and pagination without user limitation
    logger.debug(f"Querying diseasess: query={query}, sort={sort}, skip={skip}, limit={limit}, fields={fields}")

    service = DiseasesService(db)
    try:
        # Parse query JSON if provided
        query_dict = None
        if query:
            try:
                query_dict = json.loads(query)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid query JSON format")

        result = service.get_list(
            skip=skip,
            limit=limit,
            query_dict=query_dict,
            sort=sort
        )
        logger.debug(f"Found {result['total']} diseasess")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error querying diseasess: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{id}", response_model=DiseasesResponse)
def get_diseases(
    id: int,
    fields: str = Query(None, description="Comma-separated list of fields to return"),
    db: Session = Depends(get_db),
):
    """Get a single diseases by ID"""
    logger.debug(f"Fetching diseases with id: {id}, fields={fields}")
    
    service = DiseasesService(db)
    try:
        result = service.get_by_id(id)
        if not result:
            logger.warning(f"Diseases with id {id} not found")
            raise HTTPException(status_code=404, detail="Diseases not found")
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching diseases {id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("", response_model=DiseasesResponse, status_code=201)
def create_diseases(
    data: DiseasesData,
    db: Session = Depends(get_db),
):
    """Create a new diseases"""
    logger.debug(f"Creating new diseases with data: {data}")
    
    service = DiseasesService(db)
    try:
        result = service.create(data.model_dump())
        if not result:
            raise HTTPException(status_code=400, detail="Failed to create diseases")
        
        logger.info(f"Diseases created successfully with id: {result.id}")
        return result
    except ValueError as e:
        logger.error(f"Validation error creating diseases: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating diseases: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/batch", response_model=List[DiseasesResponse], status_code=201)
def create_diseasess_batch(
    request: DiseasesBatchCreateRequest,
    db: Session = Depends(get_db),
):
    """Create multiple diseasess in a single request"""
    logger.debug(f"Batch creating {len(request.items)} diseasess")
    
    service = DiseasesService(db)
    results = []
    
    try:
        for item_data in request.items:
            result = service.create(item_data.model_dump())
            if result:
                results.append(result)
        
        logger.info(f"Batch created {len(results)} diseasess successfully")
        return results
    except Exception as e:
        db.rollback()
        logger.error(f"Error in batch create: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Batch create failed: {str(e)}")


@router.put("/batch", response_model=List[DiseasesResponse])
def update_diseasess_batch(
    request: DiseasesBatchUpdateRequest,
    db: Session = Depends(get_db),
):
    """Update multiple diseasess in a single request"""
    logger.debug(f"Batch updating {len(request.items)} diseasess")
    
    service = DiseasesService(db)
    results = []
    
    try:
        for item in request.items:
            # Only include non-None values for partial updates
            update_dict = {k: v for k, v in item.updates.model_dump().items() if v is not None}
            result = service.update(item.id, update_dict)
            if result:
                results.append(result)
        
        logger.info(f"Batch updated {len(results)} diseasess successfully")
        return results
    except Exception as e:
        db.rollback()
        logger.error(f"Error in batch update: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Batch update failed: {str(e)}")


@router.put("/{id}", response_model=DiseasesResponse)
def update_diseases(
    id: int,
    data: DiseasesUpdateData,
    db: Session = Depends(get_db),
):
    """Update an existing diseases"""
    logger.debug(f"Updating diseases {id} with data: {data}")

    service = DiseasesService(db)
    try:
        # Only include non-None values for partial updates
        update_dict = {k: v for k, v in data.model_dump().items() if v is not None}
        result = service.update(id, update_dict)
        if not result:
            logger.warning(f"Diseases with id {id} not found for update")
            raise HTTPException(status_code=404, detail="Diseases not found")
        
        logger.info(f"Diseases {id} updated successfully")
        return result
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Validation error updating diseases {id}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating diseases {id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.delete("/batch")
def delete_diseasess_batch(
    request: DiseasesBatchDeleteRequest,
    db: Session = Depends(get_db),
):
    """Delete multiple diseasess by their IDs"""
    logger.debug(f"Batch deleting {len(request.ids)} diseasess")
    
    service = DiseasesService(db)
    deleted_count = 0
    
    try:
        for item_id in request.ids:
            success = service.delete(item_id)
            if success:
                deleted_count += 1
        
        logger.info(f"Batch deleted {deleted_count} diseasess successfully")
        return {"message": f"Successfully deleted {deleted_count} diseasess", "deleted_count": deleted_count}
    except Exception as e:
        db.rollback()
        logger.error(f"Error in batch delete: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Batch delete failed: {str(e)}")


@router.delete("/{id}")
def delete_diseases(
    id: int,
    db: Session = Depends(get_db),
):
    """Delete a single diseases by ID"""
    logger.debug(f"Deleting diseases with id: {id}")
    
    service = DiseasesService(db)
    try:
        success = service.delete(id)
        if not success:
            logger.warning(f"Diseases with id {id} not found for deletion")
            raise HTTPException(status_code=404, detail="Diseases not found")
        
        logger.info(f"Diseases {id} deleted successfully")
        return {"message": "Diseases deleted successfully", "id": id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting diseases {id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")