from googleapiclient.discovery import build

import config

# Build a service object for interacting with the API. Visit
# the Google APIs Console <http://code.google.com/apis/console>
# to get an API key for your own application.
service = build("customsearch", "v1",
                developerKey=config.google_search_api_key)


def get_image_link_for_article(search_query):
    # API options: https://developers.google.com/custom-search/v1/cse/list
    # todo look at restricting by rights?
    # todo filter by aspect ratio in some way?
    res = service.cse().list(
        q=search_query,
        cx=config.google_custom_search_engine_id,
        searchType='image',
        imgType='photo',
        imgColorType='color',
        safe='medium',
        num=1
    ).execute()

    if 'items' not in res or len(res['items']) < 1:
        return ''

    return res['items'][0]['link']
