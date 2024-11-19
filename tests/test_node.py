import unittest
from unittest.mock import patch, MagicMock
from pydemlia.utils.uid import UID
from pydemlia.utils.node import Node

class TestNode(unittest.TestCase):

    def setUp(self):
        # Create a UID for testing
        self.uid = UID(key="1" * 40)  # A 160-bit UID
        self.node = Node(id=self.uid, ip="127.0.0.1", port=12345)

    def test_node_initialization(self):
        # Test that the node is initialized correctly
        self.assertEqual(self.node.id, self.uid)
        self.assertEqual(self.node.ip, "127.0.0.1")
        self.assertEqual(self.node.port, 12345)
        self.assertEqual(self.node.last_seen, 0)
        self.assertEqual(self.node.stale_count, 0)

    def test_distance_to(self):
        # Test distance calculation
        other_uid = UID(key="2" * 40)  # Another UID
        distance = self.node.distance_to(other_uid)
        self.assertEqual(distance, self.uid.get_distance(other_uid))

    def test_set_seen(self):
        # Test the set_seen method
        current_time = 1234567890  # Simulated current time
        with patch('pydemlia.utils.node.Node.current_time', return_value=current_time):
            self.node.set_seen()
            self.assertEqual(self.node.last_seen, current_time)

    def test_get_stale(self):
        # Test the get_stale method
        self.node.stale_count = 5
        self.assertEqual(self.node.get_stale(), 5)

    def test_has_queried(self):
        # Test if a node has been queried recently
        self.node.last_seen = 1234560000  # A time 1000ms before
        self.assertTrue(self.node.has_queried(1234561000))  # 1000ms later
        self.assertFalse(self.node.has_queried(1234566000))  # More than 5000ms later

    def test_node_inequality(self):
        # Test equality comparison
        other_node = Node(id=UID(key="3" * 40), ip="127.0.0.3", port=12345)
        self.assertNotEqual(self.node, other_node)

    def test_node_comparison(self):
        # Test the less-than comparison (for sorting)
        other_node = Node(id=UID(key="2" * 40), ip="127.0.0.2", port=7777)
        self.assertTrue(self.node > other_node)

if __name__ == '__main__':
    unittest.main()
