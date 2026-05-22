import json
from typing import Optional

from openai import AsyncOpenAI

from apps.api.core.config import get_settings
from apps.api.models.application import Application
from apps.api.models.job_posting import JobPosting
from apps.api.models.user import User

settings = get_settings()

TAILOR_SYSTEM = """You tailor resumes and cover letters for job applications.
Rules:
- NEVER invent employers, degrees, skills, or years of experience not in the resume.
- Only rephrase, reorder, and emphasize existing facts to match the job description.
- Output valid JSON only."""


class AITailorService:
    def __init__(self):
        self._client: Optional[AsyncOpenAI] = None

    @property
    def client(self) -> AsyncOpenAI:
        if self._client is None:
            self._client = AsyncOpenAI(api_key=settings.openai_api_key or None)
        return self._client

    async def tailor(
        self,
        user: User,
        job: JobPosting,
    ) -> dict[str, str]:
        if not user.resume_text:
            return {
                "tailored_resume": user.resume_text or "",
                "cover_letter": "",
            }
        if not settings.openai_api_key:
            return {
                "tailored_resume": user.resume_text,
                "cover_letter": f"I am excited to apply for {job.title} at {job.company}.",
            }

        prompt = f"""Resume:
{user.resume_text[:6000]}

Job title: {job.title}
Company: {job.company}
Description:
{job.description[:4000]}

Return JSON:
{{"tailored_resume": "...", "cover_letter": "..."}}"""

        response = await self.client.chat.completions.create(
            model=settings.openai_chat_model,
            messages=[
                {"role": "system", "content": TAILOR_SYSTEM},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.3,
        )
        content = response.choices[0].message.content or "{}"
        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            data = {}
        return {
            "tailored_resume": data.get("tailored_resume", user.resume_text),
            "cover_letter": data.get(
                "cover_letter",
                f"I am excited to apply for {job.title} at {job.company}.",
            ),
        }

    async def apply_to_application(
        self,
        user: User,
        job: JobPosting,
        application: Application,
    ) -> Application:
        result = await self.tailor(user, job)
        application.cover_letter = result["cover_letter"]
        return application
