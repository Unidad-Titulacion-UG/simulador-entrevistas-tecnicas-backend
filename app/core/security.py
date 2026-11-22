from datetime import UTC, datetime, timedelta
import jwt
import hashlib
from pwdlib import PasswordHash
from app.core.config import settings
from fastapi import HTTPException, status

password_hash = PasswordHash.recommended()

def hash_password(password: str) -> str:
    return password_hash.hash(password)

def verify_password(password: str, hashed_password: str) -> bool:
    return password_hash.verify(password, hashed_password)

def create_access_token(subject: str) -> str:
    expires_at = datetime.now(UTC) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": subject,
        "type": "access",
        "exp": expires_at,
    }

    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )

def decode_access_token(token: str) -> dict:
    payload = jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
    )

    if payload.get("type") != "access":
        raise jwt.InvalidTokenError("Tipo de token inválido")

    return payload

def get_current_user_id(token: str) -> int:
    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")

        if not user_id:
            raise ValueError("Token sin identificador de usuario")

        return int(user_id)

    except (jwt.InvalidTokenError, ValueError, TypeError) as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        ) from error

def create_email_verification_token(user_id: int) -> str:
    expires_at = datetime.now(UTC) + timedelta(hours=24)

    payload = {
        "sub": str(user_id),
        "purpose": "email_verification",
        "exp": expires_at,
    }

    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )

def verify_email_verification_token(token: str) -> int:
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )

        if payload.get("purpose") != "email_verification":
            raise ValueError("Token de confirmación inválido")

        user_id = payload.get("sub")

        if not user_id:
            raise ValueError("Token sin identificador de usuario")

        return int(user_id)

    except (jwt.InvalidTokenError, ValueError, TypeError) as error:
        raise ValueError("El enlace de confirmación es inválido o ha expirado") from error

def create_password_reset_token(user_id: int) -> str:
    expires_at = datetime.now(UTC) + timedelta(hours=1)

    payload = {
        "sub": str(user_id),
        "purpose": "password_reset",
        "exp": expires_at,
    }

    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )

def verify_password_reset_token(token: str) -> int:
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )

        if payload.get("purpose") != "password_reset":
            raise ValueError("Token de recuperación inválido")

        user_id = payload.get("sub")

        if not user_id:
            raise ValueError("Token sin identificador de usuario")

        return int(user_id)

    except (jwt.InvalidTokenError, ValueError, TypeError) as error:
        raise ValueError(
            "El enlace de recuperación es inválido o ha expirado"
        ) from error

def hash_reset_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()
