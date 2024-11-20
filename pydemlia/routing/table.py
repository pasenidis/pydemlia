from pydemlia.utils.uid import UID
from threading import Lock
from typing import List
from pydemlia.utils.node import Node
from pydemlia.routing.bucket import KBucket


class RoutingTable:
    def __init__(self, local_id: UID, bucket_size: int = KBucket.MAX_BUCKET_SIZE):
        """
        Initialize the Routing Table.
        :param local_id: UID of the local node.
        :param bucket_size: Maximum size of each KBucket.
        """
        self.local_id = local_id
        self.bucket_size = bucket_size
        self.kbuckets = [KBucket() for _ in range(local_id.ID_LENGTH * 8)]  # One KBucket per prefix length
        self.lock = Lock()

    def _get_bucket_index(self, node_id: UID) -> int:
        """
        Determine the index of the KBucket for a given node ID based on XOR distance.
        """
        distance = self.local_id.get_distance(node_id)
        return distance

    def insert_node(self, node: Node):
        """
        Insert a node into the appropriate KBucket.
        """
        with self.lock:
            bucket_index = self._get_bucket_index(node.get_uid())
            self.kbuckets[bucket_index].insert(node)

    def find_closest_nodes(self, target_id: UID, n: int) -> List[Node]:
        """
        Find the n closest nodes to the target ID.
        :param target_id: UID of the target node.
        :param n: Number of closest nodes to return.
        :return: List of Node objects closest to the target.
        """
        with self.lock:
            # Gather all nodes from all buckets
            all_nodes = []
            for bucket in self.kbuckets:
                all_nodes.extend(bucket.get_all_nodes())

            # Sort nodes by XOR distance to the target ID
            sorted_nodes = sorted(all_nodes, key=lambda node: node.get_uid().get_int() ^ target_id.get_int())

            # Return the n closest nodes
            return sorted_nodes[:n]

    def remove_node(self, node: Node):
        """
        Remove a node from the appropriate KBucket.
        """
        with self.lock:
            bucket_index = self._get_bucket_index(node.get_uid())
            self.kbuckets[bucket_index].remove(node)

    def get_all_nodes(self) -> List[Node]:
        """
        Get all nodes across all KBuckets.
        """
        with self.lock:
            all_nodes = []
            for bucket in self.kbuckets:
                all_nodes.extend(bucket.get_all_nodes())
            return all_nodes

    def get_unqueried_nodes(self, now: int) -> List[Node]:
        """
        Get all unqueried nodes across all KBuckets.
        """
        with self.lock:
            unqueried_nodes = []
            for bucket in self.kbuckets:
                unqueried_nodes.extend(bucket.get_unqueried_nodes(now))
            return unqueried_nodes
