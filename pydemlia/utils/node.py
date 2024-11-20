from functools import total_ordering
from pydemlia.utils.uid import UID

@total_ordering
class Node:
    def __init__(self, id: UID, ip, port):
        self.id = id
        self.ip = ip
        self.port = port
        self.last_seen = 0  # Example timestamp; set it properly in your application
        self.stale_count = 0

    def distance_to(self, key: UID) -> int:
        """Calculate the XOR distance using UID."""
        return self.id.get_distance(key)

    def set_seen(self):
        """Mark the node as seen."""
        self.last_seen = self.current_time()

    def get_stale(self) -> int:
        """Get the number of times this node has been marked stale."""
        return self.stale_count

    def mark_stale(self):
        """Mark node stale once by incrementing the stale count by 1"""
        self.stale_count += 1

    def get_uid(self):
        """Returns the Node's UID"""
        return self.id

    def has_queried(self, now: int) -> bool:
        """Check if the node has been queried recently."""
        return now - self.last_seen < 5000

    def verify(self, other_node: 'Node') -> bool:
        """Verify the node (e.g., based on ID)."""
        return self.id == other_node.id

    @staticmethod
    def current_time() -> int:
        """Utility to get the current time in milliseconds."""
        import time
        return int(time.time() * 1000)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Node) and self.id == other.id

    def __lt__(self, other: 'Node') -> bool:
        """Less-than comparator for sorting nodes based on last_seen."""
        return self.last_seen < other.last_seen

    def __repr__(self):
        return f"Node({self.id}, {self.ip}, {self.port})"
