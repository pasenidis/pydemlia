class DHT:
    def __init__(self, node):
        self.node = node

    def put(self, key, value):
        closest_nodes = self.node.routing_table.find_closest_nodes(key)
        for node in closest_nodes:
            # Send STORE message to each node
            pass

    def get(self, key):
        closest_nodes = self.node.routing_table.find_closest_nodes(key)
        for node in closest_nodes:
            # Send FIND_VALUE request and handle response
            pass

    def bootstrap(self, bootstrap_node):
        # Send FIND_NODE request to boostrap_node
        pass