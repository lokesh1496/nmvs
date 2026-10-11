from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime

from database.database import Base


class Device(Base):
    __tablename__ = "devices"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        index=True
    )

    name = Column(
        String,
        nullable=False,
        index=True
    )

    ip = Column(
        String,
        unique=True,
        nullable=False,
        index=True
    )

    device_type = Column(
        String,
        nullable=False,
        default="Unknown Device",
        index=True
    )

    created_at = Column(
        DateTime,
        default=datetime.now,
        nullable=False
    )

    updated_at = Column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
        nullable=False
    )