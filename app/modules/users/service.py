from sqlalchemy.orm import Session
from app.core.security import hash_password
from app.modules.users import repository
from app.modules.users.models import User
from app.modules.users.schemas import UserCreate, UserUpdate

def create_user(db: Session, user_data: UserCreate) -> User:
    if repository.get_user_by_username(db, user_data.username):
        raise ValueError("El nombre de usuario ya está registrado")

    if repository.get_user_by_email(db, user_data.email):
        raise ValueError("El correo electrónico ya está registrado")

    user = repository.create_user(
        db,
        {
            **user_data.model_dump(exclude={"password"}),
            "password_hash": hash_password(user_data.password),
        },
    )

    db.commit()
    db.refresh(user)

    return user

def get_user(db: Session, user_id: int) -> User:
    user = repository.get_user_by_id(db, user_id)

    if not user:
        raise ValueError("Usuario no encontrado")

    return user

def get_users(db: Session) -> list[User]:
    return repository.get_users(db)

def update_user(
    db: Session,
    user_id: int,
    user_data: UserUpdate,
) -> User:
    user = get_user(db, user_id)
    changes = user_data.model_dump(exclude_unset=True)

    if "username" in changes:
        existing_user = repository.get_user_by_username(db, changes["username"])

        if existing_user and existing_user.id != user.id:
            raise ValueError("El nombre de usuario ya está registrado")

    updated_user = repository.update_user(db, user, changes)

    db.commit()
    db.refresh(updated_user)

    return updated_user

def delete_user(db: Session, user_id: int) -> None:
    user = get_user(db, user_id)

    repository.soft_delete_user(db, user)
    db.commit()
