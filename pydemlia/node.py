import hashlib
import random

class Node:
    def __init__(self):
        self.id = self.generate_id()
        self.routing_table = []
        self.store = {}

    def generate_id(self):
        return hashlib.sha1(str(random.getrandbits(160)).encode()).hexdigest()

    def bootstrap(self, bootstrap_node):
        closest_nodes = self.find_closest_nodes(bootstrap_node)
        self.routing_table.append(bootstrap_node)

        for node in closest_nodes:
            if self.ping(node):
                self.routing_table.append(node)

    def find_closest_nodes(self, target_id):
        # Logic to find closest nodes to target_id
        pass

    def ping(self, node):
        pass
