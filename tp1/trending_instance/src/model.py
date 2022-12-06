from common.constants import STORAGE_PATH
from common.lru_cache import LRUCache
import os.path
import pathlib

PREFIX = 'data_'
DEFAULT_CAPACITY = 4
# Storage Files
# {
#   [client_id]: file_desc
# }
#


class Grouper():
    def __init__(self):
        self.clients = {}
        self.message_keeper = {}

        self._storage_files = {}
        self._recover_state()

    def add_value(self, client_id, message_id, date, views):

        datem = date.strftime("%Y-%m-%d")
        persist = self._add_raw(client_id, message_id, datem, views)
        if (persist):
            self._persist_value(client_id, message_id, datem, views)
        return

    def _add_raw(self, client_id, message_id, datem, views):
        self.clients.setdefault(client_id, {})
        self.message_keeper.setdefault(client_id, LRUCache(DEFAULT_CAPACITY))
        messages = self.message_keeper[client_id]

        if (messages.is_present(message_id)):
            return False

        messages.put(message_id)
        dates = self.clients[client_id]
        dates.setdefault(datem, 0)
        dates[datem] += views
        return True

    def len(self, client_id):
        return len(self.clients[client_id])

    def get_max(self, client_id):
        max_date = ''
        max_number = 0
        dates = self.clients[client_id]

        for date in dates:
            if (dates[date] > max_number):
                max_number = dates[date]
                max_date = date
        return max_date, max_number

    def _persist_value(self, client_id, message_id, date, views):

        if (self._storage_files.get(client_id) == None):
            self._storage_files[client_id] = open(
                f'{STORAGE_PATH}/{PREFIX}{client_id}', 'a')

        file = self._storage_files[client_id]

        file.write(f'{message_id},{date},{views}\n')
        file.flush()

    def _recover_state(self):
        for path in pathlib.Path(STORAGE_PATH).iterdir():
            if path.is_file() and PREFIX in str(os.path.basename(path)):
                self._load_client_data(path)

    def _extract_client_from_category_file_path(self, path):
        basename = str(os.path.basename(path))
        client_id = basename.replace(PREFIX, '')
        return client_id

    def _load_client_data(self, path):
        client_id = self._extract_client_from_category_file_path(path)

        with open(path) as client_categories_file:
            for line in client_categories_file:
                
                message_id, date, views = line.rstrip().split(',')

                self._add_raw(client_id, message_id, date, int(views))
