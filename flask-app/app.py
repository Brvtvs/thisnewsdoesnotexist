"""
Takes a feed of real news headlines as a seed to generate fake headlines and then fake news articles based on those fake
headlines.
"""

import hashlib
import os
import re
import time
from datetime import datetime, date
from multiprocessing import Process
from time import mktime
from time import sleep

import feedparser
from flask import Flask, abort, request, render_template

import config
import contact_us
import display_funcs
import grover
import storage
import text_cleanup
from google_image_search import get_image_link_for_article
from storage import published_as_datetime

# to throttle the generation, only generates a fake article from about 1 out of every X articles in the feed
# todo may want to make sure that we get coverage of different topics, rather than picking them essentially at random
gen_1_for_each_x_articles = 4

# amount of time to wait in between scraping the rss feed(s)
seconds_between_generation = 120

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
            # runs generated body through sanity check
            title_good = False
            for i in range(3):
                start = time.time()
                generated_title = grover.generate_article_title(article['title'], grover_params)
                print('It took %i seconds for grover to generate a title.' % (time.time() - start))
                # pauses between generations in order to try to give the server a chance to release memory
                sleep(15)
                if not text_cleanup.is_title_irreparable(generated_title):
                    title_good = True
                    break
                else:
                    print('Regenerating title because it was irreparable: ' + generated_title)
            if not title_good:
                raise Exception("Failed to generate good title after 3 tries for original title: %s" % article['title'])

            # runs generated body through sanity check
            body_good = False
            for i in range(3):
                start = time.time()
                generated_body = grover.generate_article_body(generated_title, grover_params)
                print('It took %i seconds for grover to generate a body.' % (time.time() - start))
                # pauses between generations in order to try to give the server a chance to release memory
                sleep(15)
                if not text_cleanup.is_body_irreparable(generated_body):
                    body_good = True
                    break
                else:
                    print('Regenerating body because it was irreparable: ' + generated_body)
            if not body_good:
                raise Exception("Failed to generate a good body after 3 tries for title: %s" % generated_title)

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
        except Exception as e:
            print('Encountered an error generating articles. Will try again later...')
            print(e)
        sleep(seconds_between_generation)


def launch_ec2_task():
    file = 'ec2_launch_timestamp.txt'

    while True:
        try:
            launch_instance = False
            # if no timestamp of last launch, time to launch
            if not os.path.exists(file):
                print("Launching grover EC2 instance because no timestamp found for the last time one was launched.")
                launch_instance = True
            # else if the last launch timestamp is far enough in the past
            else:
                with open(file, 'rt') as timestamp_file:
                    last_launched = float(timestamp_file.readline())
                    if time.time() - last_launched >= config.launch_ec2_instance_every_X_hours * 60 * 60:
                        print("Launching grover EC2 instance because the last was launched %i seconds ago." % (
                                time.time() - last_launched))
                        launch_instance = True
            if launch_instance:
                grover.launch_ec2_instance()
                with open(file, 'wt') as timestamp_file:
                    timestamp_file.write(str(time.time()))
        except Exception as e:
            print('Encountered an error launching an EC2 instance for grover. Will try again later...')
            print(e)

        # checks every 5 minutes
        sleep(300)


app = Flask(__name__)

opinion_feeds = ('conservative-opinion', 'conservative-opinion-2', 'liberal-opinion', 'liberal-opinion-2')


@app.route('/')
def homepage():
    articles = storage.get_recent_articles(max_articles_returned, 'top-news')
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

    return render_template('article.html', article=article, display_funcs=display_funcs)


@app.route('/news/<category>')
def view_category(category):
    if category not in rss_feeds:
        abort(400, 'Unrecognized category.')

    cat_articles = storage.get_recent_articles(7, category)

    return render_template('category.html', category=category, cat_articles=cat_articles, display_funcs=display_funcs)


@app.route('/opinion')
def view_opinion():
    opinions = []
    for feed in opinion_feeds:
        opinions = opinions + storage.get_recent_articles(round(max_articles_returned / len(opinion_feeds)), feed)
    opinions.sort(key=lambda a: published_as_datetime(a), reverse=True)
    opinions = opinions[:7]

    return render_template('category.html', category='opinion', cat_articles=opinions, display_funcs=display_funcs)


@app.route('/about')
def view_about():
    return render_template('about.html')


@app.route('/contact-us', methods=['GET', 'POST'])
def contact_us_page():
    if request.method == 'POST':
        form = {
            'first_name': request.form['first_name'],
            'last_name': request.form['last_name'],
            'email': request.form['email'],
            'message': request.form['message'],
        }
        contact_us.on_submission(form)
        return render_template('contact-us-response.html', display_funcs=display_funcs)

    else:
        return render_template('contact-us-form.html', display_funcs=display_funcs)


if __name__ == '__main__':
    if config.generate_new_articles:
        generator_process = Process(target=generate_articles_task)
        generator_process.start()
    if config.launch_ec2_instances and config.launch_ec2_instance_every_X_hours > 0:
        ec2_process = Process(target=launch_ec2_task)
        ec2_process.start()
    app.run(host='0.0.0.0', port=config.port)
