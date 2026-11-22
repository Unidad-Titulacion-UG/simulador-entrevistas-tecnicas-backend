from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.modules.auth import service
from app.modules.auth.schemas import LoginRequest, TokenResponse, EmailVerificationRequest, PasswordRecoveryRequest, PasswordResetRequest
from app.modules.auth.dependencies import get_current_user
from app.modules.users.models import User

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=TokenResponse)
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    try:
        access_token = service.authenticate_user(
            db,
            credentials.username,
            credentials.password,
        )
        return TokenResponse(access_token=access_token)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(error),
            headers={"WWW-Authenticate": "Bearer"},
        ) from error

@router.get("/me")
def get_authenticated_user(
    current_user: User = Depends(get_current_user),
):
    return {
        "id": current_user.id,
        "name": current_user.name,
        "last_name": current_user.last_name,
        "username": current_user.username,
        "email": current_user.email,
        "role": current_user.role,
    }

@router.post("/verify-email")
def verify_email(
    verification_data: EmailVerificationRequest,
    db: Session = Depends(get_db),
):
    try:
        service.verify_user_email(db, verification_data.token)

        return {
            "message": "Correo electrónico confirmado correctamente"
        }

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error

@router.post("/forgot-password")
def forgot_password(
    recovery_data: PasswordRecoveryRequest,
    db: Session = Depends(get_db),
):
    service.request_password_recovery(db, recovery_data.email)

    return {
        "message": (
            "Si el correo está registrado y verificado, "
            "recibirás instrucciones para recuperar tu contraseña."
        )
    }

@router.post("/reset-password")
def reset_password(
    reset_data: PasswordResetRequest,
    db: Session = Depends(get_db),
):
    try:
        service.reset_password(
            db,
            reset_data.token,
            reset_data.new_password,
        )

        return {
            "message": "Contraseña restablecida correctamente"
        }

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error
