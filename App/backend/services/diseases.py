import logging
from typing import Optional, Dict, Any, List

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from models.diseases import Diseases

logger = logging.getLogger(__name__)


# ------------------ Service Layer ------------------
class DiseasesService:
    """Service layer for Diseases operations"""

    def __init__(self, db: Session):
        self.db = db

    def create(self, data: Dict[str, Any]) -> Optional[Diseases]:
        """Create a new diseases"""
        try:
            obj = Diseases(**data)
            self.db.add(obj)
            self.db.commit()
            self.db.refresh(obj)
            logger.info(f"Created diseases with id: {obj.id}")
            return obj
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating diseases: {str(e)}")
            raise

    def get_by_id(self, obj_id: int) -> Optional[Diseases]:
        """Get diseases by ID"""
        try:
            query = select(Diseases).where(Diseases.id == obj_id)
            result = self.db.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error fetching diseases {obj_id}: {str(e)}")
            raise

    def get_list(
        self, 
        skip: int = 0, 
        limit: int = 20, 
        query_dict: Optional[Dict[str, Any]] = None,
        sort: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get paginated list of diseasess"""
        try:
            query = select(Diseases)
            count_query = select(func.count(Diseases.id))
            
            if query_dict:
                for field, value in query_dict.items():
                    if hasattr(Diseases, field):
                        query = query.where(getattr(Diseases, field) == value)
                        count_query = count_query.where(getattr(Diseases, field) == value)
            
            count_result = self.db.execute(count_query)
            total = count_result.scalar()

            if sort:
                if sort.startswith('-'):
                    field_name = sort[1:]
                    if hasattr(Diseases, field_name):
                        query = query.order_by(getattr(Diseases, field_name).desc())
                else:
                    if hasattr(Diseases, sort):
                        query = query.order_by(getattr(Diseases, sort))
            else:
                query = query.order_by(Diseases.id.desc())

            result = self.db.execute(query.offset(skip).limit(limit))
            items = result.scalars().all()

            return {
                "items": items,
                "total": total,
                "skip": skip,
                "limit": limit,
            }
        except Exception as e:
            logger.error(f"Error fetching diseases list: {str(e)}")
            raise

    def update(self, obj_id: int, update_data: Dict[str, Any]) -> Optional[Diseases]:
        """Update diseases"""
        try:
            obj = self.get_by_id(obj_id)
            if not obj:
                logger.warning(f"Diseases {obj_id} not found for update")
                return None
            for key, value in update_data.items():
                if hasattr(obj, key):
                    setattr(obj, key, value)

            self.db.commit()
            self.db.refresh(obj)
            logger.info(f"Updated diseases {obj_id}")
            return obj
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating diseases {obj_id}: {str(e)}")
            raise

    def delete(self, obj_id: int) -> bool:
        """Delete diseases"""
        try:
            obj = self.get_by_id(obj_id)
            if not obj:
                logger.warning(f"Diseases {obj_id} not found for deletion")
                return False
            self.db.delete(obj)
            self.db.commit()
            logger.info(f"Deleted diseases {obj_id}")
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting diseases {obj_id}: {str(e)}")
            raise

    def get_by_field(self, field_name: str, field_value: Any) -> Optional[Diseases]:
        """Get diseases by any field"""
        try:
            if not hasattr(Diseases, field_name):
                raise ValueError(f"Field {field_name} does not exist on Diseases")
            result = self.db.execute(
                select(Diseases).where(getattr(Diseases, field_name) == field_value)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error fetching diseases by {field_name}: {str(e)}")
            raise

    def list_by_field(
        self, field_name: str, field_value: Any, skip: int = 0, limit: int = 20
    ) -> List[Diseases]:
        """Get list of diseasess filtered by field"""
        try:
            if not hasattr(Diseases, field_name):
                raise ValueError(f"Field {field_name} does not exist on Diseases")
            result = self.db.execute(
                select(Diseases)
                .where(getattr(Diseases, field_name) == field_value)
                .offset(skip)
                .limit(limit)
                .order_by(Diseases.id.desc())
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error fetching diseasess by {field_name}: {str(e)}")
            raise