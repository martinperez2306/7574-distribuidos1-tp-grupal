
import pathlib


STORAGE_PATH = "./storage/"
FILE_SEPARATOR = "_"
ELEMENT_SEPARATOR = ","

class ResultRepository():
    def __init__(self):
        self.items = {}
        self._init_items()

    def _init_items(self):
        for path in pathlib.Path(STORAGE_PATH).iterdir():
            if path.is_file():
                with open(path) as tag_unique_file:
                    lines = tag_unique_file.readlines()
                    for item_str in lines:
                        self._load_item_from_file(item_str)
                    
    def _load_item_from_file(self, item_str: str):
        item_split = item_str.strip().split(ELEMENT_SEPARATOR)
        client_id = item_split[0]
        video_id = item_split[1]
        title = item_split[2]
        category = item_split[3]
        item = (video_id, title, category)
        if not self.check_element(client_id, item):
            self.add_element(client_id, item, False)

    def add_element(self, client_id, element, persist):
        self.items[client_id].add(element)
        if persist:
            self._persist_element(client_id, element)

    def check_element(self, client_id, element):
        self.items.setdefault(client_id, set())
        return element in self.items[client_id]

    def _persist_element(self, client_id, element):
        item_str = str(client_id) + ELEMENT_SEPARATOR + ELEMENT_SEPARATOR.join(element) + "\n"
        file_path = STORAGE_PATH + "tag_unique_backup"
        with open(file_path, 'a+') as tag_unique_file:
            tag_unique_file.write(item_str)
