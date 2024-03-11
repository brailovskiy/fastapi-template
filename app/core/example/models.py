from sqlalchemy import INTEGER, Column, DateTime, func

from app.database import PostgresBase


class BaseOrmModel(PostgresBase):
    __abstract__ = True

    created_at = Column(
        "created_at",
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at = Column(
        "updated_at",
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class Example(BaseOrmModel):
    __tablename__ = "example"

    id = Column("id", INTEGER, primary_key=True)
