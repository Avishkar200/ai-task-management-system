from sqlalchemy import select

from app.auth import hash_password
from app.config import get_settings
from app.database import Base, SessionLocal, engine
from app.models import Task, TaskStatus, User, UserRole


def main() -> None:
    Base.metadata.create_all(bind=engine)
    settings = get_settings()
    with SessionLocal() as db:
        admin_email = settings.admin_email.lower()
        admin = db.scalar(select(User).where(User.email == admin_email))
        if admin is None:
            admin = User(
                name=settings.admin_name,
                email=admin_email,
                password_hash=hash_password(settings.admin_password),
                role=UserRole.ADMIN.value,
            )
            db.add(admin)

        demo_email = "demo@example.com"
        demo = db.scalar(select(User).where(User.email == demo_email))
        if demo is None:
            demo = User(
                name="Demo User",
                email=demo_email,
                password_hash=hash_password("DemoPass123!"),
                role=UserRole.USER.value,
            )
            db.add(demo)
            db.flush()
            db.add_all(
                [
                    Task(
                        user_id=demo.id,
                        title="Review project requirements",
                        description="Read the assessment brief and turn it into an implementation checklist.",
                        status=TaskStatus.IN_PROGRESS.value,
                    ),
                    Task(
                        user_id=demo.id,
                        title="Prepare release notes",
                        description="Summarize completed work and list any remaining configuration steps.",
                        status=TaskStatus.PENDING.value,
                    ),
                ]
            )
        db.commit()
    print("Seed data is ready. Change the configured admin password before deployment.")


if __name__ == "__main__":
    main()