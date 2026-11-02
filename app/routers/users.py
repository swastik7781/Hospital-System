from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.user import User, UserRole
from app.schemas.user import (
    UserOut,
    UserCreate,
    UserUpdate,
    UserProfileUpdate,
    PasswordChange,
)
from app.schemas.common import PaginatedResponse, MessageResponse, ErrorResponse
from app.auth.dependencies import get_current_active_user, require_roles
from app.auth.password import verify_password, get_password_hash
from app.crud.user import (
    get_user_by_id,
    get_user_by_email,
    create_user,
    update_user,
    get_users_paginated,
)
from app.utils.pagination import paginate

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserOut)
async def get_my_profile(current_user: User = Depends(get_current_active_user)):
    return current_user


@router.patch("/me", response_model=UserOut)
async def update_my_profile(
    profile_in: UserProfileUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    update_dict = profile_in.model_dump(exclude_unset=True)
    for field, val in update_dict.items():
        setattr(current_user, field, val)
    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)
    return current_user


@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    pwd_in: PasswordChange,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    if not verify_password(pwd_in.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password verification failed",
        )
    current_user.hashed_password = get_password_hash(pwd_in.new_password)
    db.add(current_user)
    await db.commit()
    return MessageResponse(message="Password successfully changed")


@router.get(
    "/",
    response_model=PaginatedResponse[UserOut],
    dependencies=[Depends(require_roles([UserRole.ADMIN]))],
)
async def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    role: Optional[UserRole] = None,
    db: AsyncSession = Depends(get_db),
):
    users, total = await get_users_paginated(db, page=page, page_size=page_size, role=role)
    user_outs = [UserOut.model_validate(u) for u in users]
    return paginate(user_outs, total, page, page_size)


@router.post(
    "/",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles([UserRole.ADMIN]))],
)
async def admin_create_user(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    existing = await get_user_by_email(db, user_in.email)
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
    return await create_user(db, user_in)


@router.patch(
    "/{user_id}",
    response_model=UserOut,
    dependencies=[Depends(require_roles([UserRole.ADMIN]))],
)
async def admin_update_user(
    user_id: int,
    user_in: UserUpdate,
    db: AsyncSession = Depends(get_db),
):
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return await update_user(db, user, user_in)
