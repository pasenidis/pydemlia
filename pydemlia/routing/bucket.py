from threading import Lock
from typing import List, Optional
from pydemlia.utils.node import Node

class KBucket:
    MAX_BUCKET_SIZE = 5
    MAX_STALE_COUNT = 1

    def __init__(self):
        self.nodes = []  # List of active nodes
        self.cache = []  # List of cached nodes
        self.lock = Lock()

    def insert(self, node: Node):
        with self.lock:
            if node in self.nodes:
                # Update existing node
                existing_node = self.nodes[self.nodes.index(node)]
                existing_node.set_seen()
                self.nodes.sort()
            elif len(self.nodes) >= KBucket.MAX_BUCKET_SIZE:
                # Bucket is full
                if node in self.cache:
                    # Update existing node in cache
                    existing_node = self.cache[self.cache.index(node)]
                    existing_node.set_seen()
                elif len(self.cache) >= KBucket.MAX_BUCKET_SIZE:
                    # Cache is also full, remove a stale node
                    stale = max((n for n in self.cache if n.get_stale() >= KBucket.MAX_STALE_COUNT), 
                                key=lambda n: n.get_stale(), default=None)
                    if stale:
                        self.cache.remove(stale)
                        self.cache.append(node)
                else:
                    # Add new node to cache
                    self.cache.append(node)
            else:
                # Add new node to active list
                self.nodes.append(node)
                self.nodes.sort()

    def contains_ip(self, node: Node) -> bool:
        with self.lock:
            return node in self.nodes or node in self.cache

    def contains_uid(self, node: Node) -> bool:
        with self.lock:
            return any(n.verify(node) for n in self.nodes) or any(n.verify(node) for n in self.cache)

    def has_queried(self, node: Node, now: int) -> bool:
        with self.lock:
            for n in self.nodes:
                if n == node:
                    return n.has_queried(now)
            return False

    def get_all_nodes(self) -> List[Node]:
        with self.lock:
            return list(self.nodes)

    def get_unqueried_nodes(self, now: int) -> List[Node]:
        with self.lock:
            return [n for n in self.nodes if not n.has_queried(now)]

    def size(self) -> int:
        with self.lock:
            return len(self.nodes)

    def csize(self) -> int:
        with self.lock:
            return len(self.cache)
