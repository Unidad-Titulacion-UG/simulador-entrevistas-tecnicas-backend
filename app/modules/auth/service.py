import hmac
from datetime import UTC, datetime
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.email import create_email_html, send_email
from app.core.security import create_access_token, create_password_reset_token, hash_password, hash_reset_token, verify_email_verification_token, verify_password, verify_password_reset_token
from app.modules.users import repository

def authenticate_user(db: Session, username: str, password: str) -> str:
    if "@" in username:
        user = repository.get_user_by_email(db, username)
    else:
        user = repository.get_user_by_username(db, username)

    if not user or not verify_password(password, user.password_hash):
        raise ValueError("Credenciales incorrectas")

    if not user.is_email_verified:
        raise ValueError("Debes verificar tu correo electrónico")

    user.last_login_at = datetime.now(UTC)
    db.commit()

    return create_access_token(str(user.id))

def verify_user_email(db: Session, token: str) -> None:
    user_id = verify_email_verification_token(token)
    user = repository.get_user_by_id(db, user_id)

    if not user:
        raise ValueError("Usuario no encontrado")

    if user.is_email_verified:
        raise ValueError("El correo electrónico ya está confirmado")

    user.is_email_verified = True
    db.commit()

def request_password_recovery(db: Session, email: str) -> None:
    user = repository.get_user_by_email(db, email)

    if not user or not user.is_email_verified:
        return

    token = create_password_reset_token(user.id)
    user.password_reset_token_hash = hash_reset_token(token)
    db.commit()

    recovery_url = (
        f"{settings.FRONTEND_URL}/reset-password?token={token}"
    )

    send_email(
        to_email=user.email,
        subject="Recuperación de contraseña",
        body=(
            f"Hola, {user.name}:\n\n"
            "Recibimos una solicitud para restablecer tu contraseña.\n\n"
            "Para establecer una nueva contraseña, ingresa al siguiente enlace:\n\n"
            f"{recovery_url}\n\n"
            "Este enlace expirará en 1 hora.\n\n"
            "Si no solicitaste este cambio, puedes ignorar este mensaje."
        ),
        html_body=create_email_html(
            title="Recuperación de contraseña",
            greeting=user.name,
            message=(
                "Recibimos una solicitud para restablecer la contraseña "
                "de tu cuenta. Utiliza el siguiente botón para establecer "
                "una nueva contraseña."
            ),
            button_text="Restablecer contraseña",
            button_url=recovery_url,
            expiration="Este enlace expirará en 1 hora.",
            notice=(
                "Si no solicitaste este cambio, puedes ignorar "
                "este mensaje. Tu contraseña actual permanecerá sin cambios."
            ),
        ),
    )

def reset_password(
    db: Session,
    token: str,
    new_password: str,
) -> None:
    user_id = verify_password_reset_token(token)
    user = repository.get_user_by_id(db, user_id)

    if not user:
        raise ValueError("Usuario no encontrado")

    token_hash = hash_reset_token(token)

    if (
        not user.password_reset_token_hash
        or not hmac.compare_digest(
            token_hash,
            user.password_reset_token_hash,
        )
    ):
        raise ValueError("El enlace de recuperación es inválido o ya fue utilizado")

    user.password_hash = hash_password(new_password)
    user.password_reset_token_hash = None
    db.commit()
