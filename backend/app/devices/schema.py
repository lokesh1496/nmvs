from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    IPvAnyAddress,
    Field
)


class DeviceCreate(BaseModel):

    name: str = Field(
        min_length=1,
        max_length=100
    )

    ip: IPvAnyAddress

    device_type: str | None = Field(
        default=None,
        max_length=50
    )

    model_config = ConfigDict(
        extra="ignore"
    )


class DeviceUpdate(BaseModel):

    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100
    )

    ip: IPvAnyAddress | None = None

    device_type: str | None = Field(
        default=None,
        min_length=1,
        max_length=50
    )


class DeviceResponse(BaseModel):

    id: int
    name: str
    ip: str
    device_type: str
    created_at: datetime
    updated_at: datetime
    status: str | None = "Online"
    last_seen: str | None = None

    model_config = ConfigDict(
        from_attributes=True
    )


class DeviceDetectResponse(BaseModel):

    ip: str
    device_type: str
    status: str
    hostname: str | None = None
    open_ports: list[int] = []
    mac_address: str | None = None
    is_gateway: bool = False