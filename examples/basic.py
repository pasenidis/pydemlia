import threading

from pydemlia.utils.node import Node
from pydemlia.utils.uid import UID
from pydemlia.network import Network
from pydemlia.dht import DHT

local_node = Node(UID("1" * 40), ip="127.0.0.1", port=1337)
network = Network(host="127.0.0.1", port=1337)

dht = DHT(node=local_node, network=network)

threading.Thread(target=network.receive).start()

dht.put("test", 123)