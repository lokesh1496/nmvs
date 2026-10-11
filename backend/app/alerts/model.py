from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from database.database import Base


class Alert(Base):
    """
    Persisted alert generated when network devices connect, disconnect,
    experience high latency, or encounter network anomalies.
    """
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)

    device_id = Column(
        Integer,
        ForeignKey("devices.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    device_name = Column(String, nullable=True)
    device_ip = Column(String, nullable=False, index=True)

    title = Column(
        String,
        nullable=True,
        default="Device Alert"
    )

    alert_type = Column(
        String,
        nullable=False,
        default="DISCONNECTED",
        index=True
    )  # DISCONNECTED, CONNECTED, HIGH_LATENCY, NEW_DEVICE, SYSTEM_ALERT

    severity = Column(
        String,
        nullable=False,
        default="warning",
        index=True
    )  # critical, warning, info

    message = Column(String, nullable=False)

    status = Column(
        String,
        nullable=False,
        default="active",
        index=True
    )  # active, acknowledged, resolved

    created_at = Column(
        DateTime,
        default=datetime.now,
        nullable=False,
        index=True
    )
    resolved_at = Column(DateTime, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "device_id": self.device_id,
            "device_name": self.device_name,
            "device_ip": self.device_ip,
            "title": self.title,
            "alert_type": self.alert_type,
            "severity": self.severity,
            "message": self.message,
            "status": self.status,
            "created_at": self.created_at,
            "resolved_at": self.resolved_at
        }
