from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String

from database.database import Base


class MonitoringHistory(Base):
    __tablename__ = "monitoring_history"

    id = Column(Integer, primary_key=True, index=True)
    ip = Column(String, nullable=False, index=True)
    status = Column(String, nullable=False)
    checked_at = Column(
        DateTime,
        default=datetime.now,
        nullable=False
    )