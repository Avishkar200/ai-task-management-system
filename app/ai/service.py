from openai import APIError, OpenAI

from app.config import get_settings


class AIServiceError(Exception):
    pass


def _generate(prompt: str) -> str:
    settings = get_settings()
    if not settings.openai_api_key:
        raise AIServiceError("AI service is not configured; set OPENAI_API_KEY")
    try:
        response = OpenAI(api_key=settings.openai_api_key).chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": "You are a concise, practical task-planning assistant. Return only the requested text."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.4,
        )
        text = response.choices[0].message.content
        if not text or not text.strip():
            raise AIServiceError("AI provider returned an empty response")
        return text.strip()
    except APIError as exc:
        raise AIServiceError("AI provider request failed") from exc


def generate_description(title: str) -> str:
    return _generate(f"Write a useful task description in 2-4 sentences for this task: {title}")


def summarize_task(title: str, description: str) -> str:
    return _generate(f"Summarize this task in one concise sentence.\nTitle: {title}\nDescription: {description}")