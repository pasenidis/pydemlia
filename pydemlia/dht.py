import socket
import pickle
from pydemlia.utils.node import Node

class DHT:
    def __init__(self, node: Node):
        self.node = node

    def send_rpc(self, target_node, message):
        serialized_message = pickle.dumps(message)
        # Assuming target_node is a tuple (IP, port)
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.sendto(serialized_message, (target_node['ip'], target_node['port']))

    def handle_response(self, response):
        if response['operation'] == 'PING':
            self.node.set_seen()

    def put(self, key, value):
        closest_nodes = self.node.routing_table.find_closest_nodes(key)
        for node in closest_nodes:
            message = {
                'operation': 'STORE',
                'key': key,
                'value': value
            }
            self.send_rpc(node, message)

    def get(self, key):
        closest_nodes = self.node.routing_table.find_closest_nodes(key)
        for node in closest_nodes:
            message = {
                'operation': 'FIND_VALUE',
                'key': key
            }
            self.send_rpc(node, message)
            # Assume there's some response handling to process the retrieved value

    def ping(self, target_node):
        message = {
            'operation': 'PING'
        }
        self.send_rpc(target_node, message)

    def bootstrap(self, bootstrap_node):
        message = {
            'operation': 'FIND_NODE',
            'key': self.node.id
        }
        self.send_rpc(bootstrap_node, message)
        # Assuming the response from bootstrap_node contains the closest nodes to join the network
