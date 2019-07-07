import json
import os

# todo This is hacky shit. Do persistence in a way that scales and does concurrency safely.
# todo  Possibly just replace this with an object store that handles concurrent reads/writes? We do not really need
#   better scaling properties than this hacky version or for writes to be immediately accessible to reads
storage_folder = 'articles/'
storage_file_base = storage_folder + '%s.json'

if not os.path.isdir(storage_folder):
    os.mkdir(storage_folder)


def get_article(date, id):
    file = storage_file_base % str(date)
    if not os.path.exists(file):
        return {}

    with open(file, 'rt') as json_file:
        articles = json.load(json_file)['articles']
        for a in articles:
            if a['id'] == id:
                return a

    return {}


def get_articles_by_date(dates):
    articles = []
    for file in [storage_file_base % str(d) for d in dates]:
        if os.path.exists(file):
            with open(file, 'rt') as json_file:
                stored = json.load(json_file)
                for a in stored['articles']:
                    articles.append(a)
    return articles


def get_recent_articles(max_articles: int, feed):
    storage_files = []

    # loads enough files in reverse order to get at least max number of articles
    for root, dirs, files in os.walk(storage_folder):
        storage_files = storage_files + files

    # starts from most recent dated file and go backwards
    storage_files.sort(reverse=True)

    articles = []
    i = 0
    while len(articles) < max_articles and i < len(storage_files):
        file = storage_files[i]
        with open(storage_folder + file, 'rt') as json_file:
            stored = json.load(json_file)
            articles += [a for a in stored['articles'] if feed is None or feed in a['feeds']]
        i += 1

    # takes the newest articles up to the max
    articles.sort(key=lambda a: a['published'], reverse=True)
    articles = articles[:max_articles]

    return articles


def put_articles(articles):
    puts_by_date = {}

    # organizes new articles by date, which is how theyll be stored
    for a in articles:
        date = a['published'].date()
        if date in puts_by_date:
            puts_by_date[date].append(a)
        else:
            puts_by_date[date] = [a]

    # reads what's already stored to combine with the new stuff
    by_date = {}
    for date in puts_by_date.keys():
        file = storage_file_base % str(date)
        if os.path.exists(file):
            with open(file, 'rt') as json_file:
                stored = json.load(json_file)
                by_date[date] = stored

    # combines new and old articles
    for date, articles in puts_by_date.items():
        if date in by_date:
            if 'articles' not in by_date[date]:
                by_date[date]['articles'] = []
            by_date[date]['articles'] = by_date[date]['articles'] + articles
        else:
            by_date[date] = {'articles': articles}

    # writes each date's article to disk
    for date in puts_by_date.keys():
        file = storage_file_base % str(date)
        with open(file, 'wt') as json_file:
            json.dump(by_date[date], json_file, sort_keys=True, default=str)
