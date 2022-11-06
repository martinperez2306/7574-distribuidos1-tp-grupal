
import os
from src.hierarchy_middleware import HierarchyMiddlware

WATCHER_GROUP = "watcher"

class HierarchyWorker:
    def __init__(self) -> None:
        self.master = None
        self.id = os.environ['HOSTNAME']
        self.hyerarchy_id = os.environ['INSTANCE_ID']
        self.hyerarchy_instances = os.environ['TOTAL_INSTANCES']
        self.hierarchy_middleware = HierarchyMiddlware(WATCHER_GROUP, self.hyerarchy_id, self.hyerarchy_instances)

    def im_master(self) -> bool:
        return self.master == self.hyerarchy_id 

    def start(self):
        self.hierarchy_middleware.run()
