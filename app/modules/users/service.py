from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.email import create_email_html, send_email
from app.core.security import create_email_verification_token, hash_password
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

    token = create_email_verification_token(user.id)

    verification_url = (
        f"{settings.FRONTEND_URL}/verify-email?token={token}"
    )

    send_email(
        to_email=user.email,
        subject="Confirma tu correo electrónico",
        body=(
            f"Hola, {user.name}:\n\n"
            "Gracias por registrarte en Simulador de Entrevistas Técnicas.\n\n"
            "Para confirmar tu dirección de correo electrónico, "
            "ingresa al siguiente enlace:\n\n"
            f"{verification_url}\n\n"
            "Este enlace expirará en 24 horas.\n\n"
            "Si no realizaste este registro, puedes ignorar este mensaje."
        ),
        html_body=create_email_html(
            title="Confirma tu correo electrónico",
            greeting=user.name,
            message=(
                "Gracias por registrarte. Confirma tu dirección de "
                "correo electrónico para completar tu registro."
            ),
            button_text="Confirmar correo electrónico",
            button_url=verification_url,
            expiration="Este enlace expirará en 24 horas.",
            notice=(
                "Si no realizaste este registro, puedes ignorar "
                "este mensaje."
            ),
        ),
    )

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
