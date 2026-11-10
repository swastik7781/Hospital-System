from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.config import settings
from app.models.user import UserRole
from app.schemas.user import (
    UserCreate,
    UserOut,
    LoginRequest,
    Token,
    RefreshTokenRequest,
    PasswordResetRequest,
    PasswordResetConfirm,
)
from app.schemas.common import MessageResponse, ErrorResponse
from app.crud.user import get_user_by_email, create_user, update_user
from app.auth.password import verify_password, get_password_hash
from app.auth.jwt import create_access_token, create_refresh_token, decode_token
from app.utils.rate_limiter import limiter

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    responses={409: {"model": ErrorResponse}},
)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    existing = await get_user_by_email(db, user_in.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists",
        )
    user = await create_user(db, user_in)

    # If role is patient, automatically create and link their EHR clinical profile
    if user.role == UserRole.PATIENT:
        from app.models.patient import Patient
        from datetime import date
        from sqlalchemy import select, or_

        # Check if an existing unlinked patient record with this email or phone exists
        stmt = select(Patient).where(
            or_(Patient.email == user.email, Patient.phone == user.phone),
            Patient.is_deleted.is_(False),
        )
        existing_pat = (await db.execute(stmt)).scalars().first()
        if existing_pat:
            existing_pat.user_id = user.id
            if not existing_pat.email:
                existing_pat.email = user.email
            db.add(existing_pat)
            await db.commit()
        else:
            new_pat = Patient(
                full_name=user.full_name,
                date_of_birth=date(1995, 1, 1),
                gender="Male",
                phone=user.phone or "+91 94370 00000",
                email=user.email,
                address="Bhubaneswar, Odisha",
                blood_group="O+",
                allergies="None",
                user_id=user.id,
            )
            db.add(new_pat)
            await db.commit()
            await db.refresh(new_pat)

    return user


@router.post(
    "/login",
    response_model=Token,
    responses={401: {"model": ErrorResponse}},
)
@limiter.limit(settings.RATE_LIMIT_AUTH)
async def login(
    request: Request,
    credentials: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    user = await get_user_by_email(db, credentials.email)
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User account is deactivated",
        )

    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role.value}
    )
    refresh_token = create_refresh_token(
        data={"sub": str(user.id), "role": user.role.value}
    )

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user=UserOut.model_validate(user),
    )


@router.post(
    "/refresh",
    response_model=Token,
    responses={401: {"model": ErrorResponse}},
)
async def refresh_token(
    payload_in: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
):
    token_payload = decode_token(payload_in.refresh_token)
    if not token_payload.sub or token_payload.type != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    user = await get_user_by_email(db, token_payload.sub)
    if not user:
        from app.crud.user import get_user_by_id
        user = await get_user_by_id(db, int(token_payload.sub))

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    new_access = create_access_token(data={"sub": str(user.id), "role": user.role.value})
    new_refresh = create_refresh_token(data={"sub": str(user.id), "role": user.role.value})

    return Token(
        access_token=new_access,
        refresh_token=new_refresh,
        token_type="bearer",
        user=UserOut.model_validate(user),
    )


@router.post("/password-reset-request", response_model=MessageResponse)
async def request_password_reset(
    req: PasswordResetRequest,
    db: AsyncSession = Depends(get_db),
):
    user = await get_user_by_email(db, req.email)
    if user:
        # Generate temporary reset token (valid 1 hour)
        reset_token = create_access_token(
            data={"sub": str(user.id), "purpose": "reset"},
            expires_delta=timedelta(hours=1),
        )
        # Stub email dispatch
        return MessageResponse(
            message="If your email is registered, a password reset link has been dispatched.",
            detail=f"STUB: Reset token for testing: {reset_token}",
        )
    return MessageResponse(
        message="If your email is registered, a password reset link has been dispatched."
    )


@router.post("/password-reset-confirm", response_model=MessageResponse)
async def confirm_password_reset(
    req: PasswordResetConfirm,
    db: AsyncSession = Depends(get_db),
):
    token_payload = decode_token(req.token)
    if not token_payload.sub:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        )
    from app.crud.user import get_user_by_id
    user = await get_user_by_id(db, int(token_payload.sub))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user.hashed_password = get_password_hash(req.new_password)
    db.add(user)
    await db.commit()
    return MessageResponse(message="Password successfully reset. You may now login.")
