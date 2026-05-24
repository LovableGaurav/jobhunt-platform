from fastapi import APIRouter

from apps.api.core.config import get_settings
from apps.api.core.dependencies import CurrentUser, DbSession
from apps.api.models.user import User
from apps.api.schemas.user import UserResponse, UserUpdate
from apps.api.services.matcher import MatcherService

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: CurrentUser) -> UserResponse:
    return UserResponse.model_validate(current_user)


@router.put("/me", response_model=UserResponse)
async def update_me(
    body: UserUpdate,
    db: DbSession,
    current_user: CurrentUser,
) -> User:
    if body.full_name is not None:
        current_user.full_name = body.full_name
    if body.target_roles is not None:
        current_user.target_roles = body.target_roles
    if body.years_experience is not None:
        current_user.years_experience = body.years_experience
    if body.resume_text is not None:
        current_user.resume_text = body.resume_text
        settings = get_settings()
        if settings.openai_api_key and "your-key-here" not in settings.openai_api_key:
            try:
                matcher = MatcherService(db)
                await matcher.embed_user_resume(current_user)
            except Exception:
                current_user.resume_embedding = None
        else:
            current_user.resume_embedding = None

    await db.flush()
    await db.refresh(current_user)
    return current_user
