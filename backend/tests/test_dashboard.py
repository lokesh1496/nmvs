import unittest
from app.dashboard import service
from app.dashboard.schema import (
    DashboardOverviewResponse,
    DashboardStats,
    DeviceTypeDistribution,
    RecentActivity,
    RecentSpeedTest
)


class TestDashboardSchemas(unittest.TestCase):
    def test_dashboard_stats_defaults(self):
        stats = DashboardStats()
        self.assertEqual(stats.total_devices, 0)
        self.assertEqual(stats.online_devices, 0)
        self.assertEqual(stats.offline_devices, 0)
        self.assertEqual(stats.network_health_score, 100.0)

    def test_device_type_distribution(self):
        dist = DeviceTypeDistribution(device_type="Router", count=3)
        self.assertEqual(dist.device_type, "Router")
        self.assertEqual(dist.count, 3)


class TestDashboardService(unittest.TestCase):
    def test_get_dashboard_overview(self):
        overview = service.get_dashboard_overview()
        self.assertIsInstance(overview, DashboardOverviewResponse)
        self.assertIsInstance(overview.stats, DashboardStats)
        self.assertIsInstance(overview.device_types, list)
        self.assertIsInstance(overview.recent_monitoring, list)
        self.assertIsInstance(overview.recent_speed_tests, list)
        self.assertIsNotNone(overview.generated_at)

    def test_get_dashboard_stats(self):
        stats = service.get_dashboard_stats()
        self.assertIsInstance(stats, DashboardStats)
        self.assertGreaterEqual(stats.total_devices, 0)
        self.assertGreaterEqual(stats.network_health_score, 0.0)


if __name__ == "__main__":
    unittest.main()
