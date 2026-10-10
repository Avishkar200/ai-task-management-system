# AI-Powered Task Management System

A FastAPI backend for managing user-owned tasks with JWT authentication, role-aware permissions, and AI-powered task assistance.

## Project overview

This project provides:

- User registration and JWT-based login
- Role-based access control for normal users and admins
- CRUD APIs for tasks
- Status management controlled by admins
- AI task description generation and task summarization
- SQLite for local development and PostgreSQL-compatible configuration for production

## Python version

- Python 3.10+

## Setup instructions

1. Create and activate a virtual environment.
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Copy the environment file and configure values:

   ```bash
   copy .env.example .env
   ```

4. Start the app:

   ```bash
   uvicorn app.main:app --reload
   ```

5. Open the API docs at:

   ```text
   http://127.0.0.1:8000/docs
   ```

## Database configuration

The app reads its database settings from the `DATABASE_URL` value in `.env`.

Example:

```env
DATABASE_URL=postgresql+psycopg://task_user:task_password@localhost:5432/task_manager
```

For local development, SQLite also works with the default config if you do not want to set up Postgres.

## Environment variables

The app expects the following variables in `.env`:

```env
DATABASE_URL=postgresql+psycopg://task_user:task_password@localhost:5432/task_manager
JWT_SECRET_KEY=replace-with-a-long-random-secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini
ADMIN_NAME=Task Admin
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=ChangeMe123!
```

## AI configuration

The AI integration uses the OpenAI-compatible client.

- Set `OPENAI_API_KEY` in the environment.
- You may optionally change `OPENAI_MODEL`.
- The implementation is kept in `app/ai/service.py` and raises a clean `503` error if the service is not configured.

## How to run the application

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API endpoints

### Authentication

- `POST /api/auth/register`
- `POST /api/auth/login`

### Tasks

- `POST /api/tasks`
- `GET /api/tasks`
- `GET /api/tasks/{task_id}`
- `PATCH /api/tasks/{task_id}`
- `PATCH /api/tasks/{task_id}/status`
- `DELETE /api/tasks/{task_id}`

### AI endpoints

- `POST /api/tasks/generate-description`
- `POST /api/tasks/{id}/summarize`

### Admin endpoints

- `GET /api/admin/tasks`
- `GET /api/admin/users`

## Test credentials

Seeded example users are:

- Admin: `admin@example.com` / `AdminPass123!`
- Alice: `alice@example.com` / `AlicePass123!`
- Bob: `bob@example.com` / `BobPass123!`

## AI feature implemented

The app implements the description-generation flow:

- `POST /api/tasks/generate-description`
- Accepts a title and returns a generated description from the configured AI provider
- Returns a `503` error if the API key is missing or the provider fails

## Notes

- The project does not commit `.env` or API keys.
- The sample environment file is tracked as `.env.example`.
- Permissions are enforced at the API layer.
- Tasks are limited to the task owner for regular users.
