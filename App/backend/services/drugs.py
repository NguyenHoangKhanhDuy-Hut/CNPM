import logging
from typing import Optional, Dict, Any, List

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from models.drugs import Drugs

logger = logging.getLogger(__name__)


# ------------------ Service Layer ------------------
class DrugsService:
    """Service layer for Drugs operations"""

    def __init__(self, db: Session):
        self.db = db

    def create(self, data: Dict[str, Any]) -> Optional[Drugs]:
        """Create a new drugs"""
        try:
            obj = Drugs(**data)
            self.db.add(obj)
            self.db.commit()
            self.db.refresh(obj)
            logger.info(f"Created drugs with id: {obj.id}")
            return obj
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating drugs: {str(e)}")
            raise

    def get_by_id(self, obj_id: int) -> Optional[Drugs]:
        """Get drugs by ID"""
        try:
            query = select(Drugs).where(Drugs.id == obj_id)
            result = self.db.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error fetching drugs {obj_id}: {str(e)}")
            raise

    def get_list(
        self, 
        skip: int = 0, 
        limit: int = 20, 
        query_dict: Optional[Dict[str, Any]] = None,
        sort: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get paginated list of drugss"""
        try:
            query = select(Drugs)
            count_query = select(func.count(Drugs.id))
            
            if query_dict:
                for field, value in query_dict.items():
                    if hasattr(Drugs, field):
                        query = query.where(getattr(Drugs, field) == value)
                        count_query = count_query.where(getattr(Drugs, field) == value)
            
            count_result = self.db.execute(count_query)
            total = count_result.scalar()

            if sort:
                if sort.startswith('-'):
                    field_name = sort[1:]
                    if hasattr(Drugs, field_name):
                        query = query.order_by(getattr(Drugs, field_name).desc())
                else:
                    if hasattr(Drugs, sort):
                        query = query.order_by(getattr(Drugs, sort))
            else:
                query = query.order_by(Drugs.id.desc())

            result = self.db.execute(query.offset(skip).limit(limit))
            items = result.scalars().all()

            return {
                "items": items,
                "total": total,
                "skip": skip,
                "limit": limit,
            }
        except Exception as e:
            logger.error(f"Error fetching drugs list: {str(e)}")
            raise

    def update(self, obj_id: int, update_data: Dict[str, Any]) -> Optional[Drugs]:
        """Update drugs"""
        try:
            obj = self.get_by_id(obj_id)
            if not obj:
                logger.warning(f"Drugs {obj_id} not found for update")
                return None
            for key, value in update_data.items():
                if hasattr(obj, key):
                    setattr(obj, key, value)

            self.db.commit()
            self.db.refresh(obj)
            logger.info(f"Updated drugs {obj_id}")
            return obj
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating drugs {obj_id}: {str(e)}")
            raise

    def delete(self, obj_id: int) -> bool:
        """Delete drugs"""
        try:
            obj = self.get_by_id(obj_id)
            if not obj:
                logger.warning(f"Drugs {obj_id} not found for deletion")
                return False
            self.db.delete(obj)
            self.db.commit()
            logger.info(f"Deleted drugs {obj_id}")
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting drugs {obj_id}: {str(e)}")
            raise

    def get_by_field(self, field_name: str, field_value: Any) -> Optional[Drugs]:
        """Get drugs by any field"""
        try:
            if not hasattr(Drugs, field_name):
                raise ValueError(f"Field {field_name} does not exist on Drugs")
            result = self.db.execute(
                select(Drugs).where(getattr(Drugs, field_name) == field_value)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error fetching drugs by {field_name}: {str(e)}")
            raise

    def list_by_field(
        self, field_name: str, field_value: Any, skip: int = 0, limit: int = 20
    ) -> List[Drugs]:
        """Get list of drugss filtered by field"""
        try:
            if not hasattr(Drugs, field_name):
                raise ValueError(f"Field {field_name} does not exist on Drugs")
            result = self.db.execute(
                select(Drugs)
                .where(getattr(Drugs, field_name) == field_value)
                .offset(skip)
                .limit(limit)
                .order_by(Drugs.id.desc())
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error fetching drugss by {field_name}: {str(e)}")
            raise