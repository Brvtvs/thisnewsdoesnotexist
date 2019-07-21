"""
Takes a feed of real news headlines as a seed to generate fake headlines and then fake news articles based on those fake
headlines.
"""

import hashlib
import json
import re
from datetime import datetime, date
from multiprocessing import Process
from time import mktime
from time import sleep

import feedparser
from flask import Flask, abort, request, render_template

import config
import display_funcs
import grover
import storage
from google_image_search import get_image_link_for_article
from storage import published_as_datetime

# to throttle the generation, only generates a fake article from about 1 out of every X articles in the feed
# todo may want to make sure that we get coverage of different topics, rather than picking them essentially at random
gen_1_for_each_x_articles = 4

# amount of time to wait in between scraping the rss feed(s)
seconds_between_generation = 1200

rss_feeds = {
    'top-news': 'http://feeds.reuters.com/reuters/topNews',
    'world': 'http://feeds.reuters.com/Reuters/worldNews',
    'business': 'http://feeds.reuters.com/reuters/businessNews',
    'technology': 'http://feeds.reuters.com/reuters/technologyNews',
    'politics': 'http://feeds.reuters.com/Reuters/PoliticsNews',
    'health': 'http://feeds.reuters.com/reuters/healthNews',
    'entertainment': 'http://feeds.reuters.com/reuters/entertainment',
    'sports': 'http://feeds.reuters.com/reuters/sportsNews',
    'conservative-opinion': 'https://www.washingtontimes.com/rss/headlines/opinion/commentary/',
    'conservative-opinion-2': 'https://www.washingtontimes.com/rss/headlines/opinion/editorials/',
    'liberal-opinion': 'http://jacobinmag.com/feed',
    'liberal-opinion-2': 'http://www.thenation.com/feed/?post_type=article',
}
special_grover_configs = {
    'conservative-opinion': {'domain': 'redstate.com'},
    'conservative-opinion-2': {'domain': 'redstate.com'},
    'liberal-opinion': {'domain': 'thenation.com'},
    'liberal-opinion-2': {'domain': 'thenation.com'},
}

max_articles_returned = 50


def generate_articles():
    """Generates fake news articles, using a feed of real ones as seed data."""
    print('Generating new articles based on scraped articles from %i feeds...' % len(rss_feeds))

    real_articles_by_title = dict()
    feeds_by_title = dict()
    dates_seen = set()

    # collects metadata for articles from each rss feed
    for feed_name, url in rss_feeds.items():
        feed = feedparser.parse(url)

        # filters out articles based on a deterministic hash of their name to throttle how much generation we're doing
        filtered_real_articles = [a for a in feed['entries'] if
                                  int.from_bytes(hashlib.md5(a['title'].encode('utf-8')).digest(),
                                                 byteorder='big') % gen_1_for_each_x_articles == 0]

        for a in filtered_real_articles:
            # adds article to list of those that need processing if it isnt already in the list
            if a['title'] not in real_articles_by_title:
                real_articles_by_title[a['title']] = a

            # tracks which feeds each title was found in
            if a['title'] in feeds_by_title:
                feeds_by_title[a['title']].append(feed_name)
            else:
                feeds_by_title[a['title']] = [feed_name]

            # tracks which dates have been seen so we know what local storage to load
            dates_seen.add(date.fromtimestamp(mktime(a.published_parsed)))

    # loads any saved results for articles we already generated fake articles from so we do not overwhelm the API with requests
    cached_articles = storage.get_articles_by_date(dates_seen)
    cached_titles = set(map(lambda a: a["original_title"], cached_articles))

    print('Real titles (', len(real_articles_by_title), '):', real_articles_by_title.keys())
    print()

    # only need to generate results for those we have not already generated results for
    uncached_articles = [a for a in real_articles_by_title.values() if a['title'] not in cached_titles]

    # generates titles based on the seeds, then generates article bodies for those titles
    print('Generating %i new articles...' % len(uncached_articles))
    generated_articles = []
    for article in uncached_articles:
        try:
            feeds = feeds_by_title[article['title']]

            grover_params = None
            for feed_id, grover_conf in special_grover_configs.items():
                if feed_id in feeds:
                    grover_params = grover_conf
                    break

            # todo is there a better way to seed the generator than this?
            generated_title = grover.generate_article_title(article['title'], grover_params)
            generated_body = grover.generate_article_body(generated_title, grover_params)

            # todo look for a way to filter out what results are going to be bad
            image = get_image_link_for_article(generated_title)

            # Removes all non-word characters (everything except numbers and letters)
            id = re.sub(r"[^\w\s]", '', generated_title.lower())
            # Replaces all runs of whitespace with a single dash
            id = re.sub(r"\s+", '-', id)

            generated_articles.append({
                'id': id,
                'original_title': article['title'],
                'published': datetime.fromtimestamp(mktime(article.published_parsed)),
                'generated_title': generated_title,
                'generated_body': generated_body,
                'matched_image_link': image,
                'feeds': feeds
            })
        except Exception as e:
            print(e)
            print('Failed to generate an article from %s. Ignoring it for now...' % article['title'])

    print('Done generating %i new articles' % len(generated_articles))

    # saves generated articles so they can be reused later
    storage.put_articles(generated_articles)


def generate_articles_task():
    while True:
        try:
            generate_articles()
        except Exception:
            print('Encountered an error generating articles. Will try again later...')
        sleep(seconds_between_generation)


app = Flask(__name__)


@app.route('/')
def homepage():
    articles = storage.get_recent_articles(max_articles_returned, 'top-news')
    opinion_feeds = ('conservative-opinion', 'conservative-opinion-2', 'liberal-opinion', 'liberal-opinion-2')
    opinions = []
    for feed in opinion_feeds:
        opinions = opinions + storage.get_recent_articles(round(max_articles_returned / len(opinion_feeds)), feed)
    opinions.sort(key=lambda a: published_as_datetime(a), reverse=True)

    return render_template('index.html', articles=articles, opinions=opinions, display_funcs=display_funcs)


@app.route('/article/<date>/<id>')
def view_article(date, id):
    article = storage.get_article(date, id)

    # todo add good-looking 404 behavior
    if not article:
        abort(404, 'Article not found.')

    return render_template('article.html', article=article)


@app.route('/api/v1/articles')
def get_articles():
    # todo handle io errors because we have no actual concurrency control

    feed = request.args.get('feed')
    quantity = request.args.get('quantity')
    if not feed or not quantity:
        abort(400, "Missing parameters.")
    max_results = min(int(quantity), max_articles_returned)

    if feed not in rss_feeds:
        abort(400, 'Unrecognized feed.')

    return json.dumps(
        {'articles': storage.get_recent_articles(max_results, feed)},
        sort_keys=True, default=str)


@app.route('/api/v1/article/<date>/<id>')
def get_article(date: str, id: str):
    article = storage.get_article(date, id)
    if not article:
        abort(404, 'Article not found.')
    return json.dumps(article, sort_keys=True, default=str)


if __name__ == '__main__':
    if config.generate_new_articles:
        background_process = Process(target=generate_articles_task)
        background_process.start()
    app.run(host='0.0.0.0', port=config.port)
