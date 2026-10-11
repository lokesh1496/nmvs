from datetime import datetime
from sqlalchemy import Column, DateTime, Float, Integer, String
from database.database import Base


class DeviceBandwidthHistory(Base):
    __tablename__ = "device_bandwidth_history"

    id = Column(Integer, primary_key=True, index=True)
    ip = Column(String, nullable=False, index=True)
    download_mbps = Column(Float, nullable=True)
    upload_mbps = Column(Float, nullable=True)
    ping_ms = Column(Float, nullable=True)
    tested_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    def to_dict(self):
        return {
            "id": self.id,
            "ip": self.ip,
            "download_mbps": self.download_mbps,
            "upload_mbps": self.upload_mbps,
            "ping_ms": self.ping_ms,
            "tested_at": self.tested_at
        }


SpeedTestHistory = DeviceBandwidthHistory