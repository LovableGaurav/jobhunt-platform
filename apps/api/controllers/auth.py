from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.core.dependencies import DbSession
from apps.api.core.security import create_access_token, hash_password, verify_password
from apps.api.models.user import User
from apps.api.repositories.user_repo import UserRepository
from apps.api.schemas.user import TokenResponse, UserCreate, UserLogin, UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(body: UserCreate, db: DbSession) -> User:
    repo = UserRepository(db)
    existing = await repo.get_by_email(body.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    user = User(
        email=body.email.lower(),
        hashed_password=hash_password(body.password),
        full_name=body.full_name,
        target_roles=body.target_roles,
        years_experience=body.years_experience,
    )
    return await repo.create(user)


@router.post("/login", response_model=TokenResponse)
async def login(body: UserLogin, db: DbSession) -> TokenResponse:
    repo = UserRepository(db)
    user = await repo.get_by_email(body.email)
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    token = create_access_token(str(user.id))
    return TokenResponse(access_token=token)
