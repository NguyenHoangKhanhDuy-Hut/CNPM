from datetime import datetime
import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select, delete
from sqlalchemy.orm import Session

from core.database import get_db
from dependencies.auth import get_current_user
from models.user_saved_drugs import UserSavedDrug
from schemas.auth import UserResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/user", tags=["user-saved-drugs"])


class SavedDrugResponse(BaseModel):
    id: int
    drug_name: str
    saved_at: Optional[str] = None

    class Config:
        from_attributes = True


class SavedDrugListResponse(BaseModel):
    items: List[SavedDrugResponse]
    total: int


class SaveStatusResponse(BaseModel):
    saved: bool
    message: str


@router.get("/saved-drugs", response_model=SavedDrugListResponse)
def list_saved_drugs(
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = (
        select(UserSavedDrug)
        .where(UserSavedDrug.user_id == current_user.id)
        .order_by(UserSavedDrug.saved_at.desc())
    )
    result = db.execute(query)
    items = result.scalars().all()

    def to_response(item: UserSavedDrug) -> SavedDrugResponse:
        return SavedDrugResponse(
            id=item.id,
            drug_name=item.drug_name,
            saved_at=item.saved_at.isoformat() if item.saved_at else None,
        )

    return SavedDrugListResponse(
        items=[to_response(item) for item in items],
        total=len(items),
    )


@router.post("/saved-drugs/{drug_name:path}", response_model=SaveStatusResponse)
def save_drug(
    drug_name: str,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    existing = db.execute(
        select(UserSavedDrug).where(
            UserSavedDrug.user_id == current_user.id,
            UserSavedDrug.drug_name == drug_name,
        )
    ).scalar_one_or_none()

    if existing:
        return SaveStatusResponse(saved=True, message="Drug already saved")

    saved = UserSavedDrug(
        user_id=current_user.id,
        drug_name=drug_name,
    )
    db.add(saved)
    db.commit()

    return SaveStatusResponse(saved=True, message="Drug saved successfully")


@router.delete("/saved-drugs/{drug_name:path}", response_model=SaveStatusResponse)
def unsave_drug(
    drug_name: str,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    result = db.execute(
        delete(UserSavedDrug).where(
            UserSavedDrug.user_id == current_user.id,
            UserSavedDrug.drug_name == drug_name,
        )
    )

    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Saved drug not found")

    db.commit()

    return SaveStatusResponse(saved=False, message="Drug unsaved successfully")
