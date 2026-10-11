from collections import Counter
from datetime import datetime
import ipaddress

from app.devices.model import Device
from app.monitoring.model import MonitoringHistory
from app.speed_monitoring.model import DeviceBandwidthHistory
from app.users.model import User
from database.database import SessionLocal

from .schema import (
    DashboardOverviewResponse,
    DashboardStats,
    DeviceTypeDistribution,
    RecentActivity,
    RecentSpeedTest
)


def get_dashboard_overview() -> DashboardOverviewResponse:
    """
    Aggregate system metrics, device status breakdown, bandwidth speeds,
    and recent activity into a single unified dashboard payload.
    """
    db = SessionLocal()
    try:
        # 1. Fetch devices
        devices = db.query(Device).all()
        total_devices = len(devices)
        ip_to_name = {d.ip: d.name for d in devices}

        # Device type breakdown
        type_counts = Counter(d.device_type or "Unknown Device" for d in devices)
        device_types = [
            DeviceTypeDistribution(device_type=dtype, count=cnt)
            for dtype, cnt in sorted(type_counts.items(), key=lambda x: x[1], reverse=True)
        ]

        # Subnet counts
        subnets_set = set()
        for d in devices:
            try:
                net = ipaddress.ip_interface(f"{d.ip}/24").network
                subnets_set.add(str(net))
            except Exception:
                pass
        total_subnets = len(subnets_set)

        # 2. Latest status per device from MonitoringHistory
        recent_monitoring_records = (
            db.query(MonitoringHistory)
            .order_by(MonitoringHistory.checked_at.desc())
            .limit(10)
            .all()
        )

        device_statuses: dict[str, str] = {}
        # Fetch sufficient history to know current status of all devices
        all_recent = (
            db.query(MonitoringHistory)
            .order_by(MonitoringHistory.checked_at.desc())
            .limit(total_devices * 5 if total_devices else 50)
            .all()
        )
        for rec in all_recent:
            if rec.ip not in device_statuses:
                device_statuses[rec.ip] = rec.status

        # If a device has never been monitored yet, default to Online
        for d in devices:
            if d.ip not in device_statuses:
                device_statuses[d.ip] = "Online"

        if total_devices > 0:
            reg_ips = {d.ip for d in devices}
            online_devices = sum(1 for ip, st in device_statuses.items() if ip in reg_ips and st == "Online")
            offline_devices = max(0, total_devices - online_devices)
            health_score = (
                round((online_devices / total_devices * 100.0), 1)
            )
        else:
            online_devices = 0
            offline_devices = 0
            health_score = 100.0

        recent_monitoring = [
            RecentActivity(
                id=rec.id,
                ip=rec.ip,
                device_name=ip_to_name.get(rec.ip),
                status=rec.status,
                checked_at=rec.checked_at
            )
            for rec in recent_monitoring_records
        ]

        # 3. Latest bandwidth tests
        recent_speed_records = (
            db.query(DeviceBandwidthHistory)
            .order_by(DeviceBandwidthHistory.tested_at.desc())
            .limit(5)
            .all()
        )
        recent_speed_tests = [
            RecentSpeedTest(
                id=sp.id,
                ip=sp.ip,
                download_mbps=sp.download_mbps,
                upload_mbps=sp.upload_mbps,
                ping_ms=sp.ping_ms,
                tested_at=sp.tested_at
            )
            for sp in recent_speed_records
        ]

        latest_speed = recent_speed_records[0] if recent_speed_records else None
        latest_download = latest_speed.download_mbps if latest_speed else None
        latest_upload = latest_speed.upload_mbps if latest_speed else None
        latest_ping = latest_speed.ping_ms if latest_speed else None

        # 4. User counts
        try:
            total_users = db.query(User).count()
        except Exception:
            total_users = 0

        stats = DashboardStats(
            total_devices=total_devices,
            online_devices=online_devices,
            offline_devices=offline_devices,
            network_health_score=health_score,
            total_subnets=total_subnets,
            total_users=total_users,
            latest_download_mbps=latest_download,
            latest_upload_mbps=latest_upload,
            latest_ping_ms=latest_ping
        )

        return DashboardOverviewResponse(
            stats=stats,
            device_types=device_types,
            recent_monitoring=recent_monitoring,
            recent_speed_tests=recent_speed_tests,
            generated_at=datetime.now()
        )

    finally:
        db.close()


def get_dashboard_stats() -> DashboardStats:
    """Return quick KPI statistics without detailed record lists."""
    overview = get_dashboard_overview()
    return overview.stats
