import logging

MIN_PERIOD_IN_DAYS = 21

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
