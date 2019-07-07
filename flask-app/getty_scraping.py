import re

import en_core_web_sm
import requests

nlp = en_core_web_sm.load()

search_url_base = 'https://www.gettyimages.com/photos/%s'


def get_image_link_for_article(article):
    entities = nlp(article['generated_title']).ents

    if len(entities) < 1:
        return ''

    search_term = ' '.join(map(lambda x: str(x), entities))

    first_instance = re.sub(r"[^\w\s]", '', search_term.lower())
    first_instance = re.sub(r"\s+", '-', first_instance)
    search_url = search_url_base % first_instance

    # todo may be better to sort by best 'best'?
    params = {'family': 'editorial', 'orientations': 'horizontal', 'phrase': search_term, 'sort': 'mostpopular'}

    response = requests.get(search_url, params=params)
    matches = re.search(r"https://media\.gettyimages\.com/photos/(.*?)&quot", response.text)
    if matches is None:
        return ''

    first_match = matches.group(0).replace('&quot', '').replace("\\u0026", '&')

    return first_match
