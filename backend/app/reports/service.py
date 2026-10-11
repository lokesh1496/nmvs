from app.alerts.model import Alert
from app.devices.model import Device
from app.monitoring.model import MonitoringHistory
from app.speed_monitoring.model import DeviceBandwidthHistory
from database.database import SessionLocal

from .csv_report import generate_devices_csv
from .pdf_report import generate_executive_summary_pdf


def get_devices_report_csv() -> str:
    """Generate and return CSV string of all registered devices."""
    db = SessionLocal()
    try:
        devices = db.query(Device).all()
        return generate_devices_csv(devices)
    finally:
        db.close()


def get_executive_summary_pdf() -> bytes:
    """Generate and return comprehensive executive network health PDF report."""
    db = SessionLocal()
    try:
        devices = db.query(Device).all()
        alerts = db.query(Alert).order_by(Alert.created_at.desc()).limit(20).all()
        bw_records = (
            db.query(DeviceBandwidthHistory)
            .order_by(DeviceBandwidthHistory.tested_at.desc())
            .limit(5)
            .all()
        )

        total_devs = len(devices)
        recent_monitoring = (
            db.query(MonitoringHistory)
            .order_by(MonitoringHistory.checked_at.desc())
            .limit(total_devs * 3 if total_devs else 50)
            .all()
        )
        latest_status = {}
        for m in recent_monitoring:
            if m.ip not in latest_status:
                latest_status[m.ip] = m.status

        online_count = sum(1 for ip in latest_status if latest_status[ip] == "Online")
        health = (online_count / total_devs * 100.0) if total_devs > 0 else 100.0

        return generate_executive_summary_pdf(
            devices=devices,
            alerts=alerts,
            bandwidth_records=bw_records,
            health_score=health
        )
    finally:
        db.close()
