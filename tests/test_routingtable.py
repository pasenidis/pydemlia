import unittest
from pydemlia.utils.uid import UID
from pydemlia.utils.node import Node
from pydemlia.routing.table import RoutingTable
from pydemlia.routing.bucket import KBucket

class TestRoutingTable(unittest.TestCase):
    def setUp(self):
        """
        Create a RoutingTable with a local node ID for testing.
        """
        self.local_uid = UID(key="1" * 40)
        self.routing_table = RoutingTable(local_id=self.local_uid)

    def test_initialization(self):
        """
        Test that the routing table initializes correctly.
        """
        self.assertEqual(len(self.routing_table.kbuckets), self.local_uid.ID_LENGTH * 8)
        self.assertTrue(all(len(bucket.get_all_nodes()) == 0 for bucket in self.routing_table.kbuckets))

    def test_insert_node(self):
        """
        Test inserting a node into the routing table.
        """
        node = Node(UID(key="1" * 40), ip="127.0.0.1", port=1337)
        self.routing_table.insert_node(node)
        bucket_index = self.routing_table._get_bucket_index(node.get_uid())
        self.assertIn(node, self.routing_table.kbuckets[bucket_index].get_all_nodes())

    def test_find_closest_nodes(self):
        """
        Test finding the closest nodes to a given target.
        """
        node1 = Node(UID(key="12" * 20), ip="127.0.0.2", port=1337)
        node2 = Node(UID(key="34" * 20), ip="127.0.0.3", port=1337)
        node3 = Node(UID(key="56" * 20), ip="127.0.0.4", port=1337)
        
        self.routing_table.insert_node(node1)
        self.routing_table.insert_node(node2)
        self.routing_table.insert_node(node3)

        target_uid = UID(key="1" * 40)
        closest_nodes = self.routing_table.find_closest_nodes(target_id=target_uid, n=2)

        self.assertEqual(len(closest_nodes), 2)
        self.assertEqual(closest_nodes[0], node1)
        self.assertEqual(closest_nodes[1], node2)

    def test_remove_node(self):
        """
        Test removing a node from the routing table.
        """
        node = Node(UID(key="1" * 40), ip="127.0.0.1", port=1337)
        self.routing_table.insert_node(node)
        bucket_index = self.routing_table._get_bucket_index(node.get_uid())
        self.assertIn(node, self.routing_table.kbuckets[bucket_index].get_all_nodes())

        self.routing_table.remove_node(node)
        self.assertNotIn(node, self.routing_table.kbuckets[bucket_index].get_all_nodes())

    def test_insert_duplicate_node(self):
        """
        Test inserting a duplicate node.
        """
        node = Node(UID(key="1" * 40), ip="127.0.0.1", port=1337)
        self.routing_table.insert_node(node)
        self.routing_table.insert_node(node)

        bucket_index = self.routing_table._get_bucket_index(node.get_uid())
        self.assertEqual(len(self.routing_table.kbuckets[bucket_index].get_all_nodes()), 1)

    def test_overflow_handling(self):
        """
        Test handling more nodes than the bucket size.
        """
        for i in range(10):  # Insert 10 nodes, exceeding the bucket size
            uid = UID(key=f"{i:040x}")
            node = Node(uid, ip="127.0.0.5", port=1337)
            self.routing_table.insert_node(node)

        # Check the number of nodes in the bucket (should not exceed MAX_BUCKET_SIZE)
        bucket_index = self.routing_table._get_bucket_index(Node(UID(key="2" * 40), ip="127.0.0.1", port=1337).get_uid())
        self.assertLessEqual(len(self.routing_table.kbuckets[bucket_index].get_all_nodes()), KBucket.MAX_BUCKET_SIZE)

    def test_find_closest_nodes_with_empty_table(self):
        """
        Test finding closest nodes in an empty routing table.
        """
        target_uid = UID(key="77" * 20)
        closest_nodes = self.routing_table.find_closest_nodes(target_id=target_uid, n=2)
        self.assertEqual(len(closest_nodes), 0)
        
if __name__ == '__main__':
    unittest.main()
