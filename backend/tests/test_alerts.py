import unittest
from app.alerts import service
from app.alerts.schema import AlertCreate, AlertResponse, AlertsSummary


class TestAlertSchemas(unittest.TestCase):
    def test_alert_create_schema(self):
        data = AlertCreate(
            device_ip="192.168.1.100",
            message="Device disconnected from network",
            severity="critical",
            alert_type="DISCONNECTED"
        )
        self.assertEqual(data.device_ip, "192.168.1.100")
        self.assertEqual(data.alert_type, "DISCONNECTED")
        self.assertEqual(data.severity, "critical")

    def test_alerts_summary_schema(self):
        summary = AlertsSummary(
            total_alerts=5,
            active_alerts=3,
            disconnected_count=2,
            connected_count=1,
            critical_alerts=1,
            warning_alerts=2,
            resolved_alerts=2
        )
        self.assertEqual(summary.total_alerts, 5)
        self.assertEqual(summary.disconnected_count, 2)
        self.assertEqual(summary.connected_count, 1)


class TestAlertsService(unittest.TestCase):
    def test_alert_lifecycle(self):
        # 1. Create DISCONNECTED alert
        alert = service.create_alert(
            device_ip="10.20.30.40",
            message="Device 10.20.30.40 disconnected from network",
            severity="critical",
            alert_type="DISCONNECTED"
        )
        self.assertIsNotNone(alert.id)
        self.assertEqual(alert.status, "active")
        self.assertEqual(alert.alert_type, "DISCONNECTED")
        self.assertEqual(alert.severity, "critical")
        self.assertIn("Disconnected", alert.title)
        alert_id = alert.id

        # 2. Filter by alert_type
        disconnects = service.get_alerts(alert_type="DISCONNECTED")
        self.assertGreaterEqual(len(disconnects), 1)

        # 3. Create CONNECTED alert
        conn_alert = service.create_alert(
            device_ip="10.20.30.40",
            message="Device 10.20.30.40 reconnected",
            severity="info",
            alert_type="CONNECTED"
        )
        self.assertIsNotNone(conn_alert.id)
        self.assertEqual(conn_alert.alert_type, "CONNECTED")
        self.assertIn("Connected", conn_alert.title)

        # 4. Acknowledge alert
        ack = service.acknowledge_alert(alert_id)
        self.assertIsNotNone(ack)
        self.assertEqual(ack.status, "acknowledged")

        # 5. Resolve alert
        resolved = service.resolve_alert(alert_id)
        self.assertIsNotNone(resolved)
        self.assertEqual(resolved.status, "resolved")
        self.assertIsNotNone(resolved.resolved_at)

        # 6. Get summary
        summary = service.get_summary()
        self.assertIsInstance(summary, AlertsSummary)
        self.assertGreaterEqual(summary.total_alerts, 2)
        self.assertGreaterEqual(summary.disconnected_count, 1)
        self.assertGreaterEqual(summary.connected_count, 1)

        # 7. Clean up
        service.delete_alert(alert_id)
        service.delete_alert(conn_alert.id)


if __name__ == "__main__":
    unittest.main()
