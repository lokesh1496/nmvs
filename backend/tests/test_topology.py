import unittest
from datetime import datetime

from app.devices.model import Device
from app.topology.graph import TopologyGraphBuilder
from app.topology.schema import (
    SubnetInfo,
    TopologyEdge,
    TopologyGraphResponse,
    TopologyNode,
    TopologySummary
)
from app.topology import service


class TestTopologySchemas(unittest.TestCase):
    def test_node_schema_creation(self):
        node = TopologyNode(
            id="device-1",
            device_id=1,
            name="Main Gateway",
            ip="192.168.1.1",
            device_type="Router",
            status="Online",
            role="gateway",
            layer=1,
            subnet="192.168.1.0/24",
            is_gateway=True
        )
        self.assertEqual(node.id, "device-1")
        self.assertEqual(node.ip, "192.168.1.1")
        self.assertTrue(node.is_gateway)
        self.assertEqual(node.layer, 1)

    def test_edge_schema_creation(self):
        edge = TopologyEdge(
            id="edge-1",
            source="device-1",
            target="device-2",
            source_ip="192.168.1.1",
            target_ip="192.168.1.50",
            link_type="ethernet",
            speed_mbps=1000.0,
            status="active"
        )
        self.assertEqual(edge.source, "device-1")
        self.assertEqual(edge.target, "device-2")
        self.assertEqual(edge.speed_mbps, 1000.0)


class TestDynamicTopologyGraph(unittest.TestCase):
    def setUp(self):
        now = datetime.now()
        self.devices = [
            Device(id=1, name="Core Router", ip="192.168.1.1", device_type="Router", created_at=now, updated_at=now),
            Device(id=2, name="Switch Floor 1", ip="192.168.1.2", device_type="Switch", created_at=now, updated_at=now),
            Device(id=3, name="App Server", ip="192.168.1.10", device_type="Server", created_at=now, updated_at=now),
            Device(id=4, name="Staff PC 1", ip="192.168.1.101", device_type="Workstation", created_at=now, updated_at=now),
            Device(id=5, name="Office Printer", ip="192.168.1.200", device_type="Printer", created_at=now, updated_at=now),
        ]
        self.statuses = {
            "192.168.1.1": "Online",
            "192.168.1.2": "Online",
            "192.168.1.10": "Online",
            "192.168.1.101": "Online",
            "192.168.1.200": "Offline",
        }

    def test_graph_builder_inference(self):
        builder = TopologyGraphBuilder(
            devices=self.devices,
            statuses=self.statuses,
            include_wan=True
        )
        graph = builder.build()

        # Check nodes count (5 devices + 1 WAN root = 6 nodes)
        self.assertEqual(len(graph.nodes), 6)

        # Check WAN node
        wan_node = next((n for n in graph.nodes if n.role == "wan"), None)
        self.assertIsNotNone(wan_node)

        # Check gateway node
        gw_node = next((n for n in graph.nodes if n.device_id == 1), None)
        self.assertIsNotNone(gw_node)
        self.assertTrue(gw_node.is_gateway)
        self.assertEqual(gw_node.layer, 1)

        # Check switch node
        sw_node = next((n for n in graph.nodes if n.device_id == 2), None)
        self.assertIsNotNone(sw_node)
        self.assertEqual(sw_node.layer, 2)

        # Check subnets
        self.assertEqual(len(graph.subnets), 1)
        self.assertEqual(graph.subnets[0].subnet, "192.168.1.0/24")
        self.assertEqual(graph.subnets[0].device_count, 5)

        # Check edges exist
        self.assertGreater(len(graph.edges), 0)

        # Summary check
        self.assertEqual(graph.summary.total_nodes, 5)
        self.assertEqual(graph.summary.online_nodes, 4)
        self.assertEqual(graph.summary.offline_nodes, 1)
        self.assertEqual(graph.summary.network_health_score, 80.0)

    def test_connected_only_topology(self):
        """Verify that connected_only=True excludes offline devices and dead edges."""
        builder = TopologyGraphBuilder(
            devices=self.devices,
            statuses=self.statuses,
            include_wan=True,
            connected_only=True
        )
        graph = builder.build()

        # 4 online devices + 1 WAN = 5 nodes (1 offline device excluded)
        self.assertEqual(len(graph.nodes), 5)
        self.assertEqual(graph.summary.total_nodes, 4)
        self.assertEqual(graph.summary.online_nodes, 4)
        self.assertEqual(graph.summary.offline_nodes, 0)
        self.assertEqual(graph.summary.network_health_score, 100.0)

        # Confirm all edges are active and only connect online devices
        self.assertGreater(len(graph.edges), 0)
        for edge in graph.edges:
            self.assertEqual(edge.status, "active")

        # Confirm offline printer is NOT in nodes
        node_ips = [n.ip for n in graph.nodes]
        self.assertNotIn("192.168.1.200", node_ips)

    def test_discovery_topology_from_dict_devices(self):
        """Verify that discovered devices (dicts with no DB IDs) connect into a valid topology."""
        discovered = [
            {"ip": "10.0.0.1", "name": "Gateway-1", "device_type": "Router", "status": "Online", "is_gateway": True},
            {"ip": "10.0.0.50", "name": "Workstation-1", "device_type": "Workstation", "status": "Online", "is_gateway": False},
            {"ip": "10.0.0.100", "name": "Server-1", "device_type": "Server", "status": "Online", "is_gateway": False},
            {"ip": "10.0.0.200", "name": "Dead-Device", "device_type": "Unknown", "status": "Offline", "is_gateway": False}
        ]
        builder = TopologyGraphBuilder(
            devices=discovered,
            include_wan=True,
            connected_only=True
        )
        graph = builder.build()

        # 3 online discovered devices + 1 WAN = 4 nodes
        self.assertEqual(len(graph.nodes), 4)
        self.assertEqual(graph.summary.total_nodes, 3)
        self.assertEqual(graph.summary.online_nodes, 3)
        self.assertEqual(graph.summary.offline_nodes, 0)

        # All edges active
        self.assertGreater(len(graph.edges), 0)
        for edge in graph.edges:
            self.assertEqual(edge.status, "active")

        # Subnet should be 10.0.0.0/24
        self.assertEqual(len(graph.subnets), 1)
        self.assertEqual(graph.subnets[0].subnet, "10.0.0.0/24")

    def test_service_methods(self):
        # Service get_topology_summary returns TopologySummary
        summary = service.get_topology_summary()
        self.assertIsInstance(summary, TopologySummary)

        # Service get_subnets returns list of SubnetInfo
        subnets = service.get_subnets()
        self.assertIsInstance(subnets, list)

        # Service get_topology_graph returns TopologyGraphResponse
        graph_resp = service.get_topology_graph(refresh_status=False, include_wan=True, connected_only=False)
        self.assertIsInstance(graph_resp, TopologyGraphResponse)
        self.assertGreaterEqual(len(graph_resp.nodes), 1)


if __name__ == "__main__":
    unittest.main()

