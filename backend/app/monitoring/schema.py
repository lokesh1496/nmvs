from datetime import datetime
from pydantic import BaseModel, ConfigDict


class MonitoringResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ip: str
    status: str
    checked_at: datetime