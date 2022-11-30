from collections import OrderedDict


class LRUCache:

    # initialising capacity
    def __init__(self, capacity: int):
        self.cache = dict()
        self.capacity = capacity

    def is_present(self, key: int) -> int:
        return key in self.cache

    def put(self, key: str) -> None:
        if (len(self.cache) == self.capacity):
            first_el = next(iter(self.cache))
            del self.cache[first_el]

        self.cache[key] = None
