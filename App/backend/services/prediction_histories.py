import logging
from typing import Optional, Dict, Any, List

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from models.prediction_histories import Prediction_histories

logger = logging.getLogger(__name__)


# ------------------ Service Layer ------------------
class Prediction_historiesService:
    """Service layer for Prediction_histories operations"""

    def __init__(self, db: Session):
        self.db = db

    def create(self, data: Dict[str, Any], user_id: Optional[str] = None) -> Optional[Prediction_histories]:
        """Create a new prediction_histories"""
        try:
            if user_id:
                data['user_id'] = user_id
            obj = Prediction_histories(**data)
            self.db.add(obj)
            self.db.commit()
            self.db.refresh(obj)
            logger.info(f"Created prediction_histories with id: {obj.id}")
            return obj
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating prediction_histories: {str(e)}")
            raise

    def check_ownership(self, obj_id: int, user_id: str) -> bool:
        """Check if user owns this record"""
        try:
            obj = self.get_by_id(obj_id, user_id=user_id)
            return obj is not None
        except Exception as e:
            logger.error(f"Error checking ownership for prediction_histories {obj_id}: {str(e)}")
            return False

    def get_by_id(self, obj_id: int, user_id: Optional[str] = None) -> Optional[Prediction_histories]:
        """Get prediction_histories by ID (user can only see their own records)"""
        try:
            query = select(Prediction_histories).where(Prediction_histories.id == obj_id)
            if user_id:
                query = query.where(Prediction_histories.user_id == user_id)
            result = self.db.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error fetching prediction_histories {obj_id}: {str(e)}")
            raise

    def get_list(
        self, 
        skip: int = 0, 
        limit: int = 20, 
        user_id: Optional[str] = None,
        query_dict: Optional[Dict[str, Any]] = None,
        sort: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get paginated list of prediction_historiess (user can only see their own records)"""
        try:
            query = select(Prediction_histories)
            count_query = select(func.count(Prediction_histories.id))
            
            if user_id:
                query = query.where(Prediction_histories.user_id == user_id)
                count_query = count_query.where(Prediction_histories.user_id == user_id)
            
            if query_dict:
                for field, value in query_dict.items():
                    if hasattr(Prediction_histories, field):
                        query = query.where(getattr(Prediction_histories, field) == value)
                        count_query = count_query.where(getattr(Prediction_histories, field) == value)
            
            count_result = self.db.execute(count_query)
            total = count_result.scalar()

            if sort:
                if sort.startswith('-'):
                    field_name = sort[1:]
                    if hasattr(Prediction_histories, field_name):
                        query = query.order_by(getattr(Prediction_histories, field_name).desc())
                else:
                    if hasattr(Prediction_histories, sort):
                        query = query.order_by(getattr(Prediction_histories, sort))
            else:
                query = query.order_by(Prediction_histories.id.desc())

            result = self.db.execute(query.offset(skip).limit(limit))
            items = result.scalars().all()

            return {
                "items": items,
                "total": total,
                "skip": skip,
                "limit": limit,
            }
        except Exception as e:
            logger.error(f"Error fetching prediction_histories list: {str(e)}")
            raise

    def update(self, obj_id: int, update_data: Dict[str, Any], user_id: Optional[str] = None) -> Optional[Prediction_histories]:
        """Update prediction_histories (requires ownership)"""
        try:
            obj = self.get_by_id(obj_id, user_id=user_id)
            if not obj:
                logger.warning(f"Prediction_histories {obj_id} not found for update")
                return None
            for key, value in update_data.items():
                if hasattr(obj, key) and key != 'user_id':
                    setattr(obj, key, value)

            self.db.commit()
            self.db.refresh(obj)
            logger.info(f"Updated prediction_histories {obj_id}")
            return obj
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating prediction_histories {obj_id}: {str(e)}")
            raise

    def delete(self, obj_id: int, user_id: Optional[str] = None) -> bool:
        """Delete prediction_histories (requires ownership)"""
        try:
            obj = self.get_by_id(obj_id, user_id=user_id)
            if not obj:
                logger.warning(f"Prediction_histories {obj_id} not found for deletion")
                return False
            self.db.delete(obj)
            self.db.commit()
            logger.info(f"Deleted prediction_histories {obj_id}")
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting prediction_histories {obj_id}: {str(e)}")
            raise

    def get_by_field(self, field_name: str, field_value: Any) -> Optional[Prediction_histories]:
        """Get prediction_histories by any field"""
        try:
            if not hasattr(Prediction_histories, field_name):
                raise ValueError(f"Field {field_name} does not exist on Prediction_histories")
            result = self.db.execute(
                select(Prediction_histories).where(getattr(Prediction_histories, field_name) == field_value)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error fetching prediction_histories by {field_name}: {str(e)}")
            raise

    def list_by_field(
        self, field_name: str, field_value: Any, skip: int = 0, limit: int = 20
    ) -> List[Prediction_histories]:
        """Get list of prediction_historiess filtered by field"""
        try:
            if not hasattr(Prediction_histories, field_name):
                raise ValueError(f"Field {field_name} does not exist on Prediction_histories")
            result = self.db.execute(
                select(Prediction_histories)
                .where(getattr(Prediction_histories, field_name) == field_value)
                .offset(skip)
                .limit(limit)
                .order_by(Prediction_histories.id.desc())
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error fetching prediction_historiess by {field_name}: {str(e)}")
            raise