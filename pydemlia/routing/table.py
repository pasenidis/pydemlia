import random
import struct
import zlib # for CRC32
from pydemlia.utils.uid import UID
from threading import Lock
from typing import List
from pydemlia.utils.node import Node
from pydemlia.utils.collections import TreeSet, LimitedOrderedDict
from pydemlia.routing.bucket import KBucket


V4_MASK = [0xFF, 0xFF, 0x00, 0x00]
V6_MASK = [0xFF, 0xFF, 0xFF, 0xFF, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]

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
        
        self.consensus_ip = str()
        self.origin_pairs = LimitedOrderedDict(64)

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
            tree_set = TreeSet(key=lambda _node: k.get_distance(_node.id))
            for bucket in self.kbuckets:
                tree_set.add_all(bucket.get_all_nodes())

            closest = []
            for count, node in enumerate(tree_set):
                closest.append(node)
                if count == n:
                    break

            return closest


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

    def update_public_consensus(self, source: str, addr: str):
        # if addr is not global_unicast:
        #     return
        with self.lock:
            self.origin_pairs[source] = addr

            if len(self.origin_pairs) > 20 and addr != self.consensus_ip:
                k = self.origin_pairs.values()
                res = 0
                count = 1

                for i in range(len(k)):
                    count =+ 1 if k[i] == k[res] else -1
                    if count == 0:
                        res = i
                        count = 1

                if self.consensus_ip != k[res]:
                    self.consensus_ip = k[res]
                    self.restart()

    def derive_uid(self):
        """
        Derive a unique identifier (UID) for the routing table based on the consensus IP.
        """
        # Convert the IP to bytes and determine its mask
        ip = self.consensus_ip.split(":") if ":" in self.consensus_ip else self.consensus_ip.split(".")
        ip_bytes = bytearray(int(part, 16 if ":" in self.consensus_ip else 10) for part in ip)
        mask = bytearray(V6_MASK if len(ip_bytes) == 16 else V4_MASK)

        # Apply the mask to the IP
        ip_masked = bytearray(ip_byte & mask_byte for ip_byte, mask_byte in zip(ip_bytes, mask))

        # Generate a random number and modify the first byte of the masked IP
        rand = random.randint(0, 255)
        ip_masked[0] |= (rand & 0x7) << 5

        # Calculate CRC32 for the masked IP
        crc = zlib.crc32(ip_masked)

        # Build the UID's `bid`
        bid = bytearray(20)
        bid[0] = (crc >> 24) & 0xFF
        bid[1] = (crc >> 16) & 0xFF
        bid[2] = ((crc >> 8) & 0xF8) | (random.randint(0, 7))
        for i in range(3, 19):
            bid[i] = random.randint(0, 255)
        bid[19] = rand & 0xFF

        # Set the derived UID
        self.uid = UID(bytes(bid))

    def restart(self):
        self.derive_uid()