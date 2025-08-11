from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from fastapi import HTTPException, status, Response
from ..models import models


def create(db: Session, order):
    """
    Create a new Order.
    Rolls back on error and surfaces a helpful message to the client.
    """
    try:
        db_order = models.Order(
            customer_name=order.customer_name,
            description=order.description,
        )
        db.add(db_order)
        db.commit()
        db.refresh(db_order)
        return db_order
    except IntegrityError as e:
        db.rollback()
        # Constraint/foreign key/unique/etc.
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Order insert failed (integrity error): {e.orig}")
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Order insert failed: {str(e)}")


def read_all(db: Session):
    return db.query(models.Order).all()


def read_one(db: Session, order_id: int):
    return db.query(models.Order).filter(models.Order.id == order_id).first()


def update(db: Session, order_id: int, order):
    """
    Partial update for an Order.
    Uses model_dump(exclude_unset=True) so only provided fields change.
    """
    try:
        db_order_q = db.query(models.Order).filter(models.Order.id == order_id)
        update_data = order.model_dump(exclude_unset=True)
        db_order_q.update(update_data, synchronize_session=False)
        db.commit()
        return db_order_q.first()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Order update failed (integrity error): {e.orig}")
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Order update failed: {str(e)}")


def delete(db: Session, order_id: int):
    """
    Delete an Order by id. Returns 204 on success.
    """
    try:
        db_order_q = db.query(models.Order).filter(models.Order.id == order_id)
        db_order_q.delete(synchronize_session=False)
        db.commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Order delete failed: {str(e)}")

