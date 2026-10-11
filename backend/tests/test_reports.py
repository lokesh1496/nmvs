import unittest
from datetime import datetime
from app.devices.model import Device
from app.alerts.model import Alert
from app.speed_monitoring.model import DeviceBandwidthHistory
from app.reports.csv_report import generate_devices_csv
from app.reports.pdf_report import generate_executive_summary_pdf
from app.reports import service


class TestReports(unittest.TestCase):
    def setUp(self):
        now = datetime.now()
        self.devices = [
            Device(id=1, name="Router 1", ip="192.168.1.1", device_type="Router", created_at=now, updated_at=now),
            Device(id=2, name="Switch 1", ip="192.168.1.2", device_type="Switch", created_at=now, updated_at=now)
        ]
        self.alerts = [
            Alert(id=1, device_ip="192.168.1.1", title="Device Disconnected", alert_type="DISCONNECTED", severity="critical", message="Offline", status="active", created_at=now)
        ]
        self.bandwidth = [
            DeviceBandwidthHistory(id=1, ip="192.168.1.1", download_mbps=100.5, upload_mbps=25.2, ping_ms=12.0, tested_at=now)
        ]

    def test_devices_csv_export(self):
        csv_str = generate_devices_csv(self.devices)
        self.assertIn("Device ID", csv_str)
        self.assertIn("192.168.1.1", csv_str)
        self.assertIn("Router 1", csv_str)

    def test_executive_summary_pdf_generation(self):
        pdf_bytes = generate_executive_summary_pdf(
            devices=self.devices,
            alerts=self.alerts,
            bandwidth_records=self.bandwidth,
            health_score=95.0
        )
        self.assertTrue(pdf_bytes.startswith(b"%PDF-1.4"))
        self.assertTrue(pdf_bytes.endswith(b"%%EOF\n"))

    def test_service_calls(self):
        csv_content = service.get_devices_report_csv()
        self.assertIsInstance(csv_content, str)

        pdf_content = service.get_executive_summary_pdf()
        self.assertIsInstance(pdf_content, bytes)
        self.assertTrue(pdf_content.startswith(b"%PDF-1.4"))


if __name__ == "__main__":
    unittest.main()
