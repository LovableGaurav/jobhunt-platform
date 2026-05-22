from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from apps.api.controllers import applications, auth, dashboard, jobs, users
from apps.api.core.config import get_settings

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="JobHunt API",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_prefix = settings.api_prefix
app.include_router(auth.router, prefix=api_prefix)
app.include_router(users.router, prefix=api_prefix)
app.include_router(jobs.router, prefix=api_prefix)
app.include_router(applications.router, prefix=api_prefix)
app.include_router(dashboard.router, prefix=api_prefix)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
