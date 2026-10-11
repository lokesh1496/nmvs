from datetime import datetime

from sqlalchemy.exc import IntegrityError

from database.database import SessionLocal

from .model import Device


def create_device(
    name: str,
    ip: str,
    device_type: str | None = None
):

    db = SessionLocal()

    try:

        now = datetime.now()
        device = Device(
            name=name.strip(),
            ip=ip.strip(),
            device_type=(device_type.strip() if device_type else "Unknown Device"),
            created_at=now,
            updated_at=now
        )

        db.add(device)

        db.commit()

        db.refresh(device)

        return device

    except IntegrityError:

        db.rollback()

        raise ValueError(
            "A device with this IP address already exists"
        )

    finally:

        db.close()


def get_all_devices():

    db = SessionLocal()

    try:

        return (
            db.query(Device)
            .order_by(Device.id.desc())
            .all()
        )

    finally:

        db.close()


def get_device_by_id(
    device_id: int
):

    db = SessionLocal()

    try:

        return (
            db.query(Device)
            .filter(Device.id == device_id)
            .first()
        )

    finally:

        db.close()


def get_device_by_ip(
    ip: str
):

    db = SessionLocal()

    try:

        return (
            db.query(Device)
            .filter(Device.ip == ip)
            .first()
        )

    finally:

        db.close()


def update_device(
    device_id: int,
    name: str | None = None,
    ip: str | None = None,
    device_type: str | None = None
):

    db = SessionLocal()

    try:

        device = (
            db.query(Device)
            .filter(Device.id == device_id)
            .first()
        )

        if device is None:
            return None

        if name is not None:
            device.name = name.strip()

        if ip is not None:
            device.ip = ip.strip()

        if device_type is not None:
            device.device_type = device_type.strip()

        device.updated_at = datetime.now()

        db.commit()

        db.refresh(device)

        return device

    except IntegrityError:

        db.rollback()

        raise ValueError(
            "A device with this IP address already exists"
        )

    finally:

        db.close()


def delete_device(
    device_id: int
):

    db = SessionLocal()

    try:

        device = (
            db.query(Device)
            .filter(Device.id == device_id)
            .first()
        )

        if device is None:
            return None

        db.delete(device)

        db.commit()

        return True

    finally:

        db.close()


def delete_all_devices():
    db = SessionLocal()
    try:
        count = db.query(Device).delete()
        db.commit()
        return count
    finally:
        db.close()