import json
from typing import Optional
from pydemlia.routing.table import RoutingTable

class DHT:
    def __init__(self, node, network):
        self.node = node
        self.network = network
        self.routing_table = RoutingTable(self.node.get_uid())
        self.data_store = {}  # Dictionary to store key-value pairs

        # Register handlers for different operations
        self.network.register_handler("STORE", self.handle_store)
        self.network.register_handler("FIND_VALUE", self.handle_find_value)
        self.network.register_handler("PING", self.handle_ping)
        self.network.register_handler("FIND_NODE", self.handle_find_node)

    def handle_store(self, message, addr):
        """
        Handler for STORE operation. Stores the key-value pair.
        """
        try:
            key = message['key']
            value = message['value']
            self.data_store[key] = value  # Store locally
            response = {"operation": "STORE_RESPONSE", "status": "SUCCESS", "key": key}
        except KeyError as e:
            response = {"operation": "STORE_RESPONSE", "status": "FAILURE", "error": f"Missing field: {e}"}
        self.network.send(response, addr)

    def handle_find_value(self, message, addr):
        """
        Handler for FIND_VALUE operation. Returns the value if stored locally, or the closest nodes otherwise.
        """
        try:
            key = message['key']
            if key in self.data_store:
                response = {"operation": "FIND_VALUE_RESPONSE", "status": "FOUND", "key": key, "value": self.data_store[key]}
            else:
                # Use routing table to find the closest nodes
                closest_nodes = self.routing_table.find_closest_nodes(key, 2)
                response = {
                    "operation": "FIND_VALUE_RESPONSE",
                    "status": "NOT_FOUND",
                    "key": key,
                    "closest_nodes": [node.serialize() for node in closest_nodes]
                }
        except KeyError as e:
            response = {"operation": "FIND_VALUE_RESPONSE", "status": "FAILURE", "error": f"Missing field: {e}"}
        self.network.send(response, addr)

    def handle_ping(self, message, addr):
        """
        Handler for PING operation. Responds with a PONG message.
        """
        response = {"operation": "PONG"}
        self.network.send(response, addr)

    def handle_find_node(self, message, addr):
        """
        Handler for FIND_NODE operation. Returns the closest nodes to the requested ID.
        """
        try:
            target_id = message['key']
            closest_nodes = self.routing_table.find_closest_nodes(target_id, 2)
            response = {
                "operation": "FIND_NODE_RESPONSE",
                "status": "SUCCESS",
                "key": target_id,
                "closest_nodes": [node.serialize() for node in closest_nodes]
            }
        except KeyError as e:
            response = {"operation": "FIND_NODE_RESPONSE", "status": "FAILURE", "error": f"Missing field: {e}"}
        self.network.send(response, addr)

    def put(self, key, value):
        """
        Stores a key-value pair in the DHT by sending STORE requests to the closest nodes.
        """
        closest_nodes = self.routing_table.find_closest_nodes(key, 2)
        for node in closest_nodes:
            message = {"operation": "STORE", "key": key, "value": value}
            self.network.send(message, (node.ip, node.port))

    def get(self, key):
        """
        Retrieves a value from the DHT by sending FIND_VALUE requests to the closest nodes.
        """
        closest_nodes = self.routing_table.find_closest_nodes(key, 2)
        for node in closest_nodes:
            message = {"operation": "FIND_VALUE", "key": key}
            self.network.send(message, (node.ip, node.port))

    def ping(self, target_node):
        """
        Sends a PING request to a specific node.
        """
        message = {"operation": "PING"}
        self.network.send(message, (target_node.ip, target_node.port))

    def bootstrap(self, bootstrap_node):
        """
        Bootstraps the DHT by finding the closest nodes to itself via a bootstrap node.
        """
        message = {"operation": "FIND_NODE", "key": self.get_uid()}
        self.network.send(message, (bootstrap_node.ip, bootstrap_node.port))
