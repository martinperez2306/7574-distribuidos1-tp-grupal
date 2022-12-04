import logging
import json
import os
import pathlib

MIN_PERIOD_IN_DAYS = 21
STORAGE_PATH = "./storage/"
COUNTRY_COUNT_FILE = "country_count"
THUMBNAIL_GROUPER_PREFIX = "data_"

COUNTRY_CODE = 'C'
DATE_CODE = 'D'
PROCESSED_CODE = 'P'

# video_dates
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

# dirty_data:
# {
#   [client_id]: [(CODE, video_id, value)]
# }


class ThumbnailGrouper:
    def __init__(self):
        self.video_dates = {}
        self.video_countries = {}
        self.country_count = {}
        self.processed = {}
        self._dirty_data = {}
        self._init_data()

    def _init_data(self):
        for path in pathlib.Path(STORAGE_PATH).iterdir():
            if path.is_file() and COUNTRY_COUNT_FILE in str(os.path.basename(path)):
                with open(path) as country_count_file:
                    self.country_count = json.load(country_count_file)

            if path.is_file() and THUMBNAIL_GROUPER_PREFIX in str(os.path.basename(path)):
                client_id = self._extract_client(path)
                self.processed.setdefault(client_id, set())

                with open(path) as file:
                    for line in file:
                        try:
                            data = line.rstrip().split(',')
                            code = data[0]
                            video_id = data[1]

                            if (code == PROCESSED_CODE):
                                processed = self.processed[client_id]
                                processed.add(video_id)

                            if (code == DATE_CODE):
                                value = data[2]
                                self._add_date(client_id, video_id, value, False)

                            if (code == COUNTRY_CODE):
                                value = data[2]
                                self._add_country(
                                    client_id, video_id, value, False)
                        except ValueError:
                            logging.error(f'Huge error restoing line: {line}')        

                logging.info(f'Successfully restored data for {client_id}')

    def _extract_client(self, path):
        basename = str(os.path.basename(path))
        client_id = basename.replace(THUMBNAIL_GROUPER_PREFIX, '')
        return client_id

    def add_country_count(self, client_id, country_count):
        self.country_count[client_id] = country_count

    def add_entry(self, client_id, video_id, country, trending_date) -> bool:
        country_count = self.country_count[client_id]

        self.processed.setdefault(client_id, set())
        processed = self.processed[client_id]

        if (video_id in processed):
            return False

        self._add_date(client_id, video_id, trending_date, True)
        self._add_country(client_id, video_id, country, True)

        video_countries = self.video_countries[client_id]
        trending_countries = video_countries[video_id]

        video_dates = self.video_dates[client_id]
        trending_dates = video_dates[video_id]

        if (len(trending_countries) >= country_count and len(trending_dates) >= MIN_PERIOD_IN_DAYS):
            processed.add(video_id)
            self._persist_video_processed(client_id, video_id)
            return True

        return False

    def _add_date(self, client_id, video_id, trending_date, persist):
        self.video_dates.setdefault(client_id, {})
        video_dates = self.video_dates[client_id]

        video_dates.setdefault(video_id, [])
        trending_dates = video_dates[video_id]

        if (not trending_date in trending_dates):
            trending_dates.append(trending_date)
            if (persist):
                self._persist_video_date(client_id, video_id, trending_date)

    def _add_country(self, client_id, video_id, country, persist):
        self.video_countries.setdefault(client_id, {})

        video_countries = self.video_countries[client_id]

        video_countries.setdefault(video_id, [])
        trending_countries = video_countries[video_id]

        if (not country in trending_countries):
            trending_countries.append(country)
            if (persist):
                self._persist_video_country(client_id, video_id, country)

    def persist_country_count(self):
        data = self.country_count
        file_path = STORAGE_PATH + COUNTRY_COUNT_FILE
        with open(file_path, 'w') as country_count_file:
            json.dump(data, country_count_file)

    def _persist_video_date(self, client_id, video_id, value):
        self._dirty_data.setdefault(client_id, [])
        dirty_data = self._dirty_data[client_id]

        dirty_data.append((DATE_CODE, video_id, value))

    def _persist_video_country(self, client_id, video_id, value):
        self._dirty_data.setdefault(client_id, [])
        dirty_data = self._dirty_data[client_id]

        dirty_data.append((COUNTRY_CODE, video_id, value))

    def _persist_video_processed(self, client_id, video_id):
        self._dirty_data.setdefault(client_id, [])
        dirty_data = self._dirty_data[client_id]

        dirty_data.append((PROCESSED_CODE, video_id))

    def persist_data(self):
        for client_id in self._dirty_data:
            
            file_path = STORAGE_PATH + THUMBNAIL_GROUPER_PREFIX + client_id
            data = self._dirty_data[client_id]
            with open(file_path, 'a') as client_file:
                for el in data:
                    val = ','.join(el)
                    client_file.write(f'{val}\n')

        self._dirty_data = {}
