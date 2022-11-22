import json

from common.constants import CATEGORY_SUBFIX


class CategoryMapper:
    def __init__(self) -> None:
        self.categories = {}

    def load_category_file(self, client_id: str, file_name: str, file: json):
        self.categories.setdefault(client_id, {})
        client_categories = self.categories[client_id]

        category = json.loads(file)
        country = file_name.replace(CATEGORY_SUBFIX, '')
        client_categories[country] = {}

        for el in category['items']:
            client_categories[country][el['id']] = el['snippet']['title']

    def len(self, client_id: str):
        return len(self.categories.get(client_id))

    def map_category(self, client_id:str, country: str, categoryId: str) -> str:
        client_categories = self.categories[client_id]
        category_catalog = client_categories[country]
        return category_catalog[categoryId]
