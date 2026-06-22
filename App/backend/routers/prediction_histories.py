import json
import logging
from typing import List, Optional

from datetime import datetime, date

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from core.database import get_db
from services.prediction_histories import Prediction_historiesService
from dependencies.auth import get_current_user
from schemas.auth import UserResponse

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/entities/prediction_histories", tags=["prediction_histories"])


# ---------- Pydantic Schemas ----------
class Prediction_historiesData(BaseModel):
    """Entity data schema (for create/update)"""
    symptoms_input: str
    predicted_disease_id: int
    accuracy_score: int
    status: str = None


class Prediction_historiesUpdateData(BaseModel):
    """Update entity data (partial updates allowed)"""
    symptoms_input: Optional[str] = None
    predicted_disease_id: Optional[int] = None
    accuracy_score: Optional[int] = None
    status: Optional[str] = None


class Prediction_historiesResponse(BaseModel):
    """Entity response schema"""
    id: int
    user_id: str
    symptoms_input: str
    predicted_disease_id: int
    accuracy_score: int
    status: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Prediction_historiesListResponse(BaseModel):
    """List response schema"""
    items: List[Prediction_historiesResponse]
    total: int
    skip: int
    limit: int


class Prediction_historiesBatchCreateRequest(BaseModel):
    """Batch create request"""
    items: List[Prediction_historiesData]


class Prediction_historiesBatchUpdateItem(BaseModel):
    """Batch update item"""
    id: int
    updates: Prediction_historiesUpdateData


class Prediction_historiesBatchUpdateRequest(BaseModel):
    """Batch update request"""
    items: List[Prediction_historiesBatchUpdateItem]


class Prediction_historiesBatchDeleteRequest(BaseModel):
    """Batch delete request"""
    ids: List[int]


# ---------- Routes ----------
@router.get("", response_model=Prediction_historiesListResponse)
def query_prediction_historiess(
    query: str = Query(None, description="Query conditions (JSON string)"),
    sort: str = Query(None, description="Sort field (prefix with '-' for descending)"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=2000, description="Max number of records to return"),
    fields: str = Query(None, description="Comma-separated list of fields to return"),
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Query prediction_historiess with filtering, sorting, and pagination (user can only see their own records)"""
    logger.debug(f"Querying prediction_historiess: query={query}, sort={sort}, skip={skip}, limit={limit}, fields={fields}")
    
    service = Prediction_historiesService(db)
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
            user_id=str(current_user.id),
        )
        logger.debug(f"Found {result['total']} prediction_historiess")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error querying prediction_historiess: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/all", response_model=Prediction_historiesListResponse)
def query_prediction_historiess_all(
    query: str = Query(None, description="Query conditions (JSON string)"),
    sort: str = Query(None, description="Sort field (prefix with '-' for descending)"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=2000, description="Max number of records to return"),
    fields: str = Query(None, description="Comma-separated list of fields to return"),
    db: Session = Depends(get_db),
):
    # Query prediction_historiess with filtering, sorting, and pagination without user limitation
    logger.debug(f"Querying prediction_historiess: query={query}, sort={sort}, skip={skip}, limit={limit}, fields={fields}")

    service = Prediction_historiesService(db)
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
        logger.debug(f"Found {result['total']} prediction_historiess")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error querying prediction_historiess: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{id}", response_model=Prediction_historiesResponse)
def get_prediction_histories(
    id: int,
    fields: str = Query(None, description="Comma-separated list of fields to return"),
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a single prediction_histories by ID (user can only see their own records)"""
    logger.debug(f"Fetching prediction_histories with id: {id}, fields={fields}")
    
    service = Prediction_historiesService(db)
    try:
        result = service.get_by_id(id, user_id=str(current_user.id))
        if not result:
            logger.warning(f"Prediction_histories with id {id} not found")
            raise HTTPException(status_code=404, detail="Prediction_histories not found")
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching prediction_histories {id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("", response_model=Prediction_historiesResponse, status_code=201)
def create_prediction_histories(
    data: Prediction_historiesData,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new prediction_histories"""
    logger.debug(f"Creating new prediction_histories with data: {data}")
    
    service = Prediction_historiesService(db)
    try:
        result = service.create(data.model_dump(), user_id=str(current_user.id))
        if not result:
            raise HTTPException(status_code=400, detail="Failed to create prediction_histories")
        
        logger.info(f"Prediction_histories created successfully with id: {result.id}")
        return result
    except ValueError as e:
        logger.error(f"Validation error creating prediction_histories: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating prediction_histories: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/batch", response_model=List[Prediction_historiesResponse], status_code=201)
def create_prediction_historiess_batch(
    request: Prediction_historiesBatchCreateRequest,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create multiple prediction_historiess in a single request"""
    logger.debug(f"Batch creating {len(request.items)} prediction_historiess")
    
    service = Prediction_historiesService(db)
    results = []
    
    try:
        for item_data in request.items:
            result = service.create(item_data.model_dump(), user_id=str(current_user.id))
            if result:
                results.append(result)
        
        logger.info(f"Batch created {len(results)} prediction_historiess successfully")
        return results
    except Exception as e:
        db.rollback()
        logger.error(f"Error in batch create: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Batch create failed: {str(e)}")


@router.put("/batch", response_model=List[Prediction_historiesResponse])
def update_prediction_historiess_batch(
    request: Prediction_historiesBatchUpdateRequest,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update multiple prediction_historiess in a single request (requires ownership)"""
    logger.debug(f"Batch updating {len(request.items)} prediction_historiess")
    
    service = Prediction_historiesService(db)
    results = []
    
    try:
        for item in request.items:
            # Only include non-None values for partial updates
            update_dict = {k: v for k, v in item.updates.model_dump().items() if v is not None}
            result = service.update(item.id, update_dict, user_id=str(current_user.id))
            if result:
                results.append(result)
        
        logger.info(f"Batch updated {len(results)} prediction_historiess successfully")
        return results
    except Exception as e:
        db.rollback()
        logger.error(f"Error in batch update: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Batch update failed: {str(e)}")


@router.put("/{id}", response_model=Prediction_historiesResponse)
def update_prediction_histories(
    id: int,
    data: Prediction_historiesUpdateData,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update an existing prediction_histories (requires ownership)"""
    logger.debug(f"Updating prediction_histories {id} with data: {data}")

    service = Prediction_historiesService(db)
    try:
        # Only include non-None values for partial updates
        update_dict = {k: v for k, v in data.model_dump().items() if v is not None}
        result = service.update(id, update_dict, user_id=str(current_user.id))
        if not result:
            logger.warning(f"Prediction_histories with id {id} not found for update")
            raise HTTPException(status_code=404, detail="Prediction_histories not found")
        
        logger.info(f"Prediction_histories {id} updated successfully")
        return result
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Validation error updating prediction_histories {id}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating prediction_histories {id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.delete("/batch")
def delete_prediction_historiess_batch(
    request: Prediction_historiesBatchDeleteRequest,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete multiple prediction_historiess by their IDs (requires ownership)"""
    logger.debug(f"Batch deleting {len(request.ids)} prediction_historiess")
    
    service = Prediction_historiesService(db)
    deleted_count = 0
    
    try:
        for item_id in request.ids:
            success = service.delete(item_id, user_id=str(current_user.id))
            if success:
                deleted_count += 1
        
        logger.info(f"Batch deleted {deleted_count} prediction_historiess successfully")
        return {"message": f"Successfully deleted {deleted_count} prediction_historiess", "deleted_count": deleted_count}
    except Exception as e:
        db.rollback()
        logger.error(f"Error in batch delete: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Batch delete failed: {str(e)}")


@router.delete("/{id}")
def delete_prediction_histories(
    id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a single prediction_histories by ID (requires ownership)"""
    logger.debug(f"Deleting prediction_histories with id: {id}")
    
    service = Prediction_historiesService(db)
    try:
        success = service.delete(id, user_id=str(current_user.id))
        if not success:
            logger.warning(f"Prediction_histories with id {id} not found for deletion")
            raise HTTPException(status_code=404, detail="Prediction_histories not found")
        
        logger.info(f"Prediction_histories {id} deleted successfully")
        return {"message": "Prediction_histories deleted successfully", "id": id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting prediction_histories {id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")