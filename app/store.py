"""Authoritative purchase state. SQLite supports the local demo only.

The production database target is PostgreSQL. Row locks and transaction
semantics must be verified on the chosen managed service before real use.
"""
from __future__ import annotations

from datetime import datetime, timezone
from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text, UniqueConstraint, create_engine, event
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class Purchase(Base):
    __tablename__ = "purchases"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    actor_id: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    intent_key: Mapped[str] = mapped_column(String(100), nullable=False)
    snapshot: Mapped[dict] = mapped_column(JSON, nullable=False)
    snapshot_digest: Mapped[str] = mapped_column(String(64), nullable=False)
    total_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    budget_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="DRAFT")
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    provider_order_id: Mapped[str | None] = mapped_column(String(128))
    provider_capture_id: Mapped[str | None] = mapped_column(String(128))
    approval_url: Mapped[str | None] = mapped_column(Text)
    mock_buyer_approved: Mapped[bool] = mapped_column(default=False, nullable=False)
    last_error: Mapped[str | None] = mapped_column(String(300))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    operations: Mapped[list["PaymentOperation"]] = relationship(back_populates="purchase")
    __table_args__ = (UniqueConstraint("actor_id", "intent_key", name="uq_actor_intent"),)


class PaymentOperation(Base):
    __tablename__ = "payment_operations"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    purchase_id: Mapped[str] = mapped_column(ForeignKey("purchases.id"), nullable=False)
    kind: Mapped[str] = mapped_column(String(16), nullable=False)
    request_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    body_digest: Mapped[str] = mapped_column(String(64), nullable=False)
    state: Mapped[str] = mapped_column(String(24), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    purchase: Mapped[Purchase] = relationship(back_populates="operations")
    __table_args__ = (UniqueConstraint("purchase_id", "kind", name="uq_purchase_operation"),)


class AuditEvent(Base):
    __tablename__ = "audit_events"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    purchase_id: Mapped[str] = mapped_column(ForeignKey("purchases.id"), nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String(48), nullable=False)
    data: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


def make_session_factory(url: str):
    sqlite = url.startswith("sqlite")
    args = {"check_same_thread": False} if sqlite else {}
    engine = create_engine(url, connect_args=args, pool_pre_ping=True)
    if sqlite:
        @event.listens_for(engine, "connect")
        def enable_foreign_keys(connection, _):
            connection.execute("PRAGMA foreign_keys = ON")

    Base.metadata.create_all(engine)
    return sessionmaker(engine, expire_on_commit=False)


def record(db, purchase_id: str, event_type: str, data: dict | None = None) -> None:
    db.add(AuditEvent(purchase_id=purchase_id, event_type=event_type, data=data or {}))
