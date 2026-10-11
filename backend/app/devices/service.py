from . import crud
from .detector import detect_device_info, detect_device_type


def create_device(
    name: str,
    ip: str,
    device_type: str | None = None
):

    existing_device = crud.get_device_by_ip(ip)

    if existing_device is not None:

        raise ValueError(
            "A device with this IP address already exists"
        )

    # Automated detection if device_type is not provided
    if not device_type or not device_type.strip():
        device_type = detect_device_type(ip)

    return crud.create_device(
        name=name,
        ip=ip,
        device_type=device_type
    )


def get_devices():
    devices = crud.get_all_devices()
    if not devices:
        return []

    try:
        from database.database import SessionLocal
        from app.monitoring.model import MonitoringHistory

        db = SessionLocal()
        try:
            recent_monitoring = (
                db.query(MonitoringHistory)
                .order_by(MonitoringHistory.checked_at.desc())
                .limit(len(devices) * 4 if devices else 50)
                .all()
            )
            statuses = {}
            times = {}
            for rec in recent_monitoring:
                if rec.ip not in statuses:
                    statuses[rec.ip] = rec.status
                    times[rec.ip] = rec.checked_at.strftime("%Y-%m-%d %H:%M:%S")

            for dev in devices:
                dev.status = statuses.get(dev.ip, "Online")
                dev.last_seen = times.get(
                    dev.ip,
                    dev.updated_at.strftime("%Y-%m-%d %H:%M:%S") if dev.updated_at else "Recently"
                )
        finally:
            db.close()
    except Exception as e:
        print(f"Notice attaching device statuses: {e}")
        for dev in devices:
            dev.status = "Online"
            dev.last_seen = "Recently"

    return devices


def get_device(
    device_id: int
):
    device = crud.get_device_by_id(
        device_id
    )
    if device is None:
        return None

    try:
        from database.database import SessionLocal
        from app.monitoring.model import MonitoringHistory

        db = SessionLocal()
        try:
            rec = (
                db.query(MonitoringHistory)
                .filter(MonitoringHistory.ip == device.ip)
                .order_by(MonitoringHistory.checked_at.desc())
                .first()
            )
            if rec:
                device.status = rec.status
                device.last_seen = rec.checked_at.strftime("%Y-%m-%d %H:%M:%S")
            else:
                device.status = "Online"
                device.last_seen = device.updated_at.strftime("%Y-%m-%d %H:%M:%S") if device.updated_at else "Recently"
        finally:
            db.close()
    except Exception:
        device.status = "Online"
        device.last_seen = "Recently"

    return device


def update_device(
    device_id: int,
    name: str | None = None,
    ip: str | None = None,
    device_type: str | None = None
):

    if ip is not None:

        existing = crud.get_device_by_ip(ip)

        if (
            existing is not None
            and existing.id != device_id
        ):

            raise ValueError(
                "A device with this IP address already exists"
            )

        # Re-detect device type if IP changed and no manual device_type is provided
        if not device_type or not device_type.strip():
            device_type = detect_device_type(ip)

    return crud.update_device(
        device_id=device_id,
        name=name,
        ip=ip,
        device_type=device_type
    )


def redetect_device(
    device_id: int
):
    device = crud.get_device_by_id(device_id)

    if device is None:
        return None

    detected_type = detect_device_type(device.ip)

    return crud.update_device(
        device_id=device_id,
        device_type=detected_type
    )


def detect_ip(
    ip: str
):
    return detect_device_info(ip)


def delete_device(
    device_id: int
):

    return crud.delete_device(
        device_id
    )


def delete_all_devices():
    return crud.delete_all_devices()