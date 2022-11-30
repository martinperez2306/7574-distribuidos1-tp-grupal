import logging
import json
import pathlib

MIN_PERIOD_IN_DAYS = 21
STORAGE_PATH = "./storage/"
FILE_SEPARATOR = "_"

# video_ids
# {
#   [client_id]: {
#       [video_id]: [date1, date2, date3]
#   }
# }

# video_countries
# {
#   [client_id]: {
#       [video_id]: [country1, country2, country3]
#   }
# }

class ThumbnailGrouper:
    def __init__(self):
        self.video_ids = {}
        self.video_countries = {}
        self.country_count = {}
        self.processed = {}

    def _init_client_categories(self):
        for path in pathlib.Path(STORAGE_PATH).iterdir():
            if path.is_file():
                client_id = self._extract_client_from_category_file_path(path)
                if self._is_category_file(path):
                    with open(path) as client_categories_file:
                        client_categories = json.load(client_categories_file)
                        self.categories[client_id] = client_categories

    def add_country_count(self, client_id, country_count):
        self.country_count[client_id] = country_count

    def add_date(self, client_id, video_id, country, trending_date) -> bool:
        country_count = self.country_count[client_id]

        self.processed.setdefault(client_id, set())
        processed = self.processed[client_id]

        self.video_ids.setdefault(client_id, {})
        self.video_countries.setdefault(client_id, {})

        video_ids = self.video_ids[client_id]
        video_ids.setdefault(video_id, [])

        video_countries = self.video_countries[client_id]
        video_countries.setdefault(video_id, [])

        trending_dates = video_ids[video_id]
        trending_countries = video_countries[video_id]

        if (not country in trending_countries):
            trending_countries.append(country)

        if (not trending_date in trending_dates):
            trending_dates.append(trending_date)

        if (len(trending_countries) >= country_count and len(trending_dates) >= MIN_PERIOD_IN_DAYS and video_id not in processed):
            processed.add(video_id)
            return True

        return False

        # # If we have the validated ID we return
        # if (os.path.exists(validated_id)):
        #     return

        # f = open(id, "a+")
        # f.seek(0)
        # lines = f.readlines()

        # # If we have the date then its not unique
        # if trending_date in f.readlines():
        #     return

        # length = len(lines)

        # if (length + 1 == 21):
        #     f.close()
        #     os.rename(id, validated_id)
        #     logging.info(f'Tenemos 21 dias en video: {video_id}')
        #     return

        # f.write(f'{trending_date}\n')
        # f.close()

        # if (video.content['trending_date'] != None and video.content['view_count'] != None):
        #     date = datetime.strptime(
        #         video.content['trending_date'], '%Y-%m-%dT%H:%M:%SZ')

        #     views = int(video.content['view_count'])
        #     self.group_date(date, views)

    def persist_country_count(self):
        data = self.country_count
        file_path = STORAGE_PATH + "thumbnail_country_count_backup"
        with open(file_path, 'w') as thumbnail_file:
            json.dump(data, thumbnail_file)

    def persist_data(self):
        for client_id in self.video_ids:
            client_data = {
                "video_ids": self.video_ids[client_id],
                "video_countries": self.video_countries[client_id],
                "processed": self.processed[client_id]
            }
            file_path = STORAGE_PATH + client_id + FILE_SEPARATOR + "thumbnail_backup"
            with open(file_path, 'w') as thumbnail_file:
                json.dump(client_data, thumbnail_file)
