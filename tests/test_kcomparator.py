import unittest
from pydemlia.utils.node import Node
from pydemlia.utils.uid import UID
from pydemlia.routing.comparator import KComparator

class TestKComparator(unittest.TestCase):
    def setUp(self):
        """
        Create common test objects for all tests.
        """
        # Reference key UID
        self.key_uid = UID(key="1" * 40)

        # Nodes with UIDs
        self.node1 = Node(UID(key="2" * 40), ip="127.0.0.2", port=1337)
        self.node2 = Node(UID(key="3" * 40), ip="127.0.0.3", port=1337)
        self.node3 = Node(UID(key="1" * 40), ip="127.0.0.2", port=1337)  # for edge cases

        # Comparator instance
        self.comparator = KComparator(self.key_uid)

    def test_initialization(self):
        """
        Test that the comparator initializes with the correct key.
        """
        self.assertEqual(self.comparator.key, self.key_uid.get_int())

    def test_closer_node(self):
        """
        Test that the comparator correctly identifies the closer node.
        """
        result = self.comparator.compare(self.node1, self.node2)
        self.assertEqual(result, 1)  # node1 should be closer than node2

    def test_equal_distance(self):
        """
        Test the edge case where two nodes are equidistant from the key.
        """
        # Make both nodes equidistant from the key
        node_a = Node(UID(key="1" * 40), ip="127.0.0.2", port=1337)
        node_b = Node(UID(key="1" * 40), ip="127.0.0.2", port=1337)
        result = self.comparator.compare(node_a, node_b)
        self.assertEqual(result, 0)  # Both nodes are equidistant

    def test_zero_distance(self):
        """
        Test the edge case where one node has a zero distance to the key.
        """
        result = self.comparator.compare(self.node3, self.node1)
        self.assertLess(result, 0)  # node3 (key itself) is closer than node1

    def test_reverse_comparison(self):
        """
        Test that reversing the order of nodes produces the opposite result.
        """
        result1 = self.comparator.compare(self.node1, self.node2)
        result2 = self.comparator.compare(self.node2, self.node1)
        self.assertEqual(result1, -result2)

if __name__ == "__main__":
    unittest.main()
