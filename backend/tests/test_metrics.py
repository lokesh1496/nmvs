import unittest
from app.metrics import service
from app.metrics.schema import DeviceUptimeMetric, NetworkMetricsSummary


class TestMetricsSchemas(unittest.TestCase):
    def test_uptime_metric_schema(self):
        m = DeviceUptimeMetric(
            device_ip="192.168.1.1",
            device_name="Gateway",
            device_type="Router",
            total_checks=100,
            online_checks=98,
            offline_checks=2,
            uptime_percentage=98.0,
            current_status="Online"
        )
        self.assertEqual(m.device_ip, "192.168.1.1")
        self.assertEqual(m.uptime_percentage, 98.0)

    def test_network_metrics_summary_schema(self):
        s = NetworkMetricsSummary(
            overall_network_uptime=99.5,
            average_latency_ms=3.4,
            total_devices_evaluated=5,
            healthy_devices_count=5,
            degraded_devices_count=0
        )
        self.assertEqual(s.overall_network_uptime, 99.5)
        self.assertEqual(s.healthy_devices_count, 5)


class TestMetricsService(unittest.TestCase):
    def test_metrics_summary(self):
        summary = service.get_metrics_summary()
        self.assertIsInstance(summary, NetworkMetricsSummary)
        self.assertGreaterEqual(summary.overall_network_uptime, 0.0)
        self.assertLessEqual(summary.overall_network_uptime, 100.0)

    def test_devices_uptime(self):
        uptime_list = service.get_devices_uptime(hours=24)
        self.assertIsInstance(uptime_list, list)


if __name__ == "__main__":
    unittest.main()
