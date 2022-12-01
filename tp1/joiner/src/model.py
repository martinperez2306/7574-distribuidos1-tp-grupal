import json
import os.path
import pathlib

from common.constants import CATEGORY_SUBFIX

STORAGE_PATH = "./storage/"
FILE_SEPARATOR = "_"
CATEGORY_PREFIX = "categories_"


class CategoryMapper:
    def __init__(self) -> None:
        self.categories = {}
        self._init_client_categories()

    def _init_client_categories(self):
        for path in pathlib.Path(STORAGE_PATH).iterdir():
            if path.is_file() and self._is_category_file(path):
                client_id = self._extract_client_from_category_file_path(
                    path)
                with open(path) as client_categories_file:
                    client_categories = json.load(client_categories_file)
                    self.categories[client_id] = client_categories

    def _is_category_file(self, path):
        basename = str(os.path.basename(path))
        return CATEGORY_PREFIX in basename

    def _extract_client_from_category_file_path(self, path):
        basename = str(os.path.basename(path))
        split = basename.split(FILE_SEPARATOR)
        return split[len(split) - 1]

    def load_category_file(self, client_id: str, file_name: str, file: json):
        self.categories.setdefault(client_id, {})
        client_categories = self.categories[client_id]

        category = json.loads(file)
        country = file_name.replace(CATEGORY_SUBFIX, '')
        client_categories[country] = {}

        for el in category['items']:
            client_categories[country][el['id']] = el['snippet']['title']

        self._persist_client_categories(client_id, client_categories)

    def _persist_client_categories(self, client_id, client_categories):
        file_path = STORAGE_PATH + CATEGORY_PREFIX + client_id
        with open(file_path, 'w') as client_category_file:
            json.dump(client_categories, client_category_file)

    def len(self, client_id: str):
        return len(self.categories.get(client_id))

    def map_category(self, client_id: str, country: str, categoryId: str) -> str:
        client_categories = self.categories[client_id]
        category_catalog = client_categories[country]
        return category_catalog[categoryId]
