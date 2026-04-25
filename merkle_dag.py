import hashlib
import json


def hash_data(data: str) -> str:
    return hashlib.sha256(data.encode()).hexdigest()


def build_sample_dag():
    # base layer (like transactions / data chunks)
    a = Node("A", level=0)
    b = Node("B", level=0)
    c = Node("C", level=1)

    # second layer
    d = Node("D", parents=[a, b], level=1)
    e = Node("E", parents=[b, c], level=1)

    # root
    root = Node("ROOT", parents=[d, e], level=2)

    return root, [a, b, c, d, e]
    
class Node:
    def __init__(self, data, parents=None, level=0):
        self.data = data
        self.parents = parents or []
        self.level = level

        self.hash = self.compute_hash()

    def compute_hash(self):
        parent_hashes = [p.hash for p in self.parents]
        payload = {
            "data": self.data,
            "parents": parent_hashes,
            "level": self.level
        }
        return hash_data(json.dumps(payload, sort_keys=True))

    def __repr__(self):
        return f"Node(hash={self.hash[:10]}, level={self.level})"