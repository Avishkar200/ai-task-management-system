from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai.service import AIServiceError, generate_description, summarize_task
from app.auth import create_access_token, get_current_user, hash_password, require_admin, verify_password
from app.database import get_db
from app.models import Task, TaskStatus, User, UserRole
from app.schemas import (
    GeneratedText,
    GenerateDescriptionRequest,
    TaskCreate,
    TaskRead,
    TaskStatusUpdate,
    TaskUpdate,
    TokenRead,
    UserCreate,
    UserLogin,
    UserRead,
)


router = APIRouter(prefix="/api")


@router.post("/auth/register", response_model=UserRead, status_code=status.HTTP_201_CREATED, tags=["authentication"])
def register(payload: UserCreate, db: Session = Depends(get_db)):
    email = payload.email.lower()
    if db.scalar(select(User).where(User.email == email)):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email is already registered")
    user = User(name=payload.name.strip(), email=email, password_hash=hash_password(payload.password), role=UserRole.USER.value)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/auth/login", response_model=TokenRead, tags=["authentication"])
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == payload.email.lower()))
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return TokenRead(access_token=create_access_token(user), user=user)


def _get_task(task_id: int, current_user: User, db: Session) -> Task:
    task = db.get(Task, task_id)
    if task is None or (current_user.role != UserRole.ADMIN.value and task.user_id != current_user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


@router.post("/tasks", response_model=TaskRead, status_code=status.HTTP_201_CREATED, tags=["tasks"])
def create_task(payload: TaskCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = Task(user_id=current_user.id, title=payload.title.strip(), description=payload.description.strip())
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.get("/tasks", response_model=list[TaskRead], tags=["tasks"])
def list_tasks(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = select(Task).order_by(Task.created_at.desc(), Task.id.desc())
    if current_user.role != UserRole.ADMIN.value:
        query = query.where(Task.user_id == current_user.id)
    return list(db.scalars(query).all())


@router.get("/tasks/{task_id}", response_model=TaskRead, tags=["tasks"])
def view_task(task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return _get_task(task_id, current_user, db)


@router.patch("/tasks/{task_id}", response_model=TaskRead, tags=["tasks"])
def update_task(
    task_id: int,
    payload: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = _get_task(task_id, current_user, db)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(task, field, value.strip() if value is not None else value)
    db.commit()
    db.refresh(task)
    return task


@router.patch("/tasks/{task_id}/status", response_model=TaskRead, tags=["tasks"])
def update_task_status(
    task_id: int,
    payload: TaskStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    task = _get_task(task_id, current_user, db)
    task.status = payload.status.value
    db.commit()
    db.refresh(task)
    return task


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["tasks"])
def delete_task(task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = _get_task(task_id, current_user, db)
    db.delete(task)
    db.commit()


@router.post("/tasks/generate-description", response_model=GeneratedText, tags=["AI"])
def generate_task_description(
    payload: GenerateDescriptionRequest,
    current_user: User = Depends(get_current_user),
):
    del current_user
    try:
        return GeneratedText(text=generate_description(payload.title))
    except AIServiceError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc


@router.post("/tasks/{task_id}/summarize", response_model=GeneratedText, tags=["AI"])
def summarize_task_description(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = _get_task(task_id, current_user, db)
    try:
        return GeneratedText(text=summarize_task(task.title, task.description))
    except AIServiceError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc


@router.get("/admin/tasks", response_model=list[TaskRead], tags=["admin"])
def admin_list_tasks(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    return list(db.scalars(select(Task).order_by(Task.created_at.desc(), Task.id.desc())).all())


@router.get("/admin/users", response_model=list[UserRead], tags=["admin"])
def admin_list_users(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    return list(db.scalars(select(User).order_by(User.id)).all())