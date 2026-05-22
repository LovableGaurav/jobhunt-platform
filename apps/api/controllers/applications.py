from typing import List
import uuid

from fastapi import APIRouter, HTTPException, status

from apps.api.core.dependencies import CurrentUser, DbSession
from apps.api.repositories.application_repo import ApplicationRepository
from apps.api.schemas.application import ApplicationCreate, ApplicationResponse
from apps.api.services.application_bot import ApplicationBotService

router = APIRouter(prefix="/applications", tags=["applications"])


def _to_response(app) -> ApplicationResponse:
    data = ApplicationResponse.model_validate(app)
    return data


@router.get("", response_model=List[ApplicationResponse])
async def list_applications(
    db: DbSession,
    current_user: CurrentUser,
) -> List[ApplicationResponse]:
    apps = await ApplicationRepository(db).list_for_user(current_user.id)
    return [_to_response(a) for a in apps]


@router.post("", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
async def create_application(
    body: ApplicationCreate,
    db: DbSession,
    current_user: CurrentUser,
) -> ApplicationResponse:
    bot = ApplicationBotService(db)
    try:
        application = await bot.create_application(current_user.id, body.job_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    loaded = await ApplicationRepository(db).get_for_user(
        application.id, current_user.id
    )
    return _to_response(loaded or application)


@router.get("/{application_id}", response_model=ApplicationResponse)
async def get_application(
    application_id: uuid.UUID,
    db: DbSession,
    current_user: CurrentUser,
) -> ApplicationResponse:
    app = await ApplicationRepository(db).get_for_user(
        application_id, current_user.id
    )
    if not app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )
    return _to_response(app)
