from datetime import datetime, timezone, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Boolean, DateTime
from app.extensions import db


class Account(db.Model, UserMixin):
    __tablename__ = "account"

    account_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )

    username: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False
    )

    password_hash: Mapped[str] = mapped_column(
        String(255), nullable=False
    )

    role: Mapped[str] = mapped_column(
        String(20), nullable=False
    )

    active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    last_login_at: Mapped[datetime] = mapped_column(           # ← NEW: tracks last login
        DateTime, default=datetime.utcnow, nullable=False
    )

    # Relationships
    patient = relationship("Patient", back_populates="account", uselist=False)
    doctor = relationship("Doctor", back_populates="account", uselist=False)

    def get_id(self):
        return str(self.account_id)

    @property
    def id(self):
        return self.account_id

    @property
    def is_active(self):
        self._auto_deactivate_if_inactive()                    # ← checks on every access
        return self.active

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    # Auth helpers
    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def is_admin(self) -> bool:
        return self.role == "admin"

    def record_login(self) -> None:
        """Call this on every successful login to update the last login timestamp."""
        self.last_login_at = datetime.utcnow()
        db.session.commit()

    def _auto_deactivate_if_inactive(self) -> None:
        """Deactivates the account if it hasn't logged in for more than 30 days."""
        if self.active:
            cutoff = datetime.utcnow() - timedelta(days=30)
            if self.last_login_at < cutoff:
                self.active = False
                db.session.commit()

    @classmethod
    def deactivate_inactive_accounts(cls) -> int:
        """
        Bulk deactivate all accounts inactive for more than 30 days.
        Returns the number of accounts deactivated.
        Intended for use in a scheduled job (e.g. APScheduler, Celery beat, cron).
        """
        cutoff = datetime.utcnow() - timedelta(days=30)
        updated = (
            db.session.query(cls)
            .filter(cls.active == True, cls.last_login_at < cutoff)
            .update({"active": False}, synchronize_session="fetch")
        )
        db.session.commit()
        return updated