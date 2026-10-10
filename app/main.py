from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from app.api.routes import router


app = FastAPI(
    title="AI Task Manager API",
    description="JWT-authenticated task management with role-aware access and AI assistance.",
    version="1.0.0",
)
app.include_router(router)


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")


@app.get("/health", tags=["system"])
def health():
    return {"status": "ok"}