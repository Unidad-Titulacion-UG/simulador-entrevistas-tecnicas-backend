from datetime import UTC, datetime
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.modules.users.models import User

def get_user_by_id(db: Session, user_id: int) -> User | None:
    statement = select(User).where(
        User.id == user_id,
        User.deleted_at.is_(None),
    )
    return db.scalar(statement)

def get_user_by_username(db: Session, username: str) -> User | None:
    statement = select(User).where(
        User.username == username,
        User.deleted_at.is_(None),
    )
    return db.scalar(statement)

def get_user_by_email(db: Session, email: str) -> User | None:
    statement = select(User).where(
        User.email == email,
        User.deleted_at.is_(None),
    )
    return db.scalar(statement)

def get_users(db: Session) -> list[User]:
    statement = (
        select(User)
        .where(User.deleted_at.is_(None))
        .order_by(User.id)
    )
    return list(db.scalars(statement).all())

def create_user(db: Session, user_data: dict) -> User:
    user = User(**user_data)
    db.add(user)
    db.flush()
    db.refresh(user)
    return user

def update_user(db: Session, user: User, user_data: dict) -> User:
    for field, value in user_data.items():
        setattr(user, field, value)

    db.flush()
    db.refresh(user)
    return user

def soft_delete_user(db: Session, user: User) -> None:
    user.deleted_at = datetime.now(UTC)
    db.flush()
