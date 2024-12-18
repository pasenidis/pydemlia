from pydemlia.utils.node import Node
from pydemlia.utils.uid import UID

class KComparator:
    def __init__(self, key):
        """
        Initialize the comparator with a reference key (UID as an integer).
        :param key: A UID object with a method get_int() to retrieve the UID as an integer.
        """
        self.key = key.get_int()

    def compare(self, node_a: Node, node_b: Node) -> int:
        """
        Compare two nodes based on their distance from the key.
        :param node_a: The first Node object.
        :param node_b: The second Node object.
        :return: Negative if node_a is closer, positive if node_b is closer, 0 if equal.
        """
        # Calculate distances using XOR
        dist_a = node_a.get_uid().get_int() ^ self.key
        dist_b = node_b.get_uid().get_int() ^ self.key

        # Compare absolute distances
        return (dist_a > dist_b) - (dist_a < dist_b)
