"""
Takes a feed of real news headlines as a seed to generate fake headlines and then fake news articles based on those fake
headlines.
"""

import json
import os

import feedparser
import spacy
from flask import Flask

import grover

app = Flask(__name__)
nlp = spacy.load("en_core_web_sm")

# limits number of articles taken from rss feed so this doesnt hit API more than necessary
# For example, if 3, this will generate fake articles based on the 3 most recent headlines from the feed.
max_articles = 6
cache_file = 'cache.json'

# gets a feed of the day's real news articles
rss = "http://feeds.reuters.com/reuters/topNews"
feed = feedparser.parse(rss)
use_these_original_titles = list(map(lambda entry: entry['title'], feed['entries']))
use_these_original_titles = use_these_original_titles[:max_articles]
print('Real titles (', len(use_these_original_titles), '):', use_these_original_titles)
print()

# loads any saved results for articles we already generated fake articles from so we do not overwhelm the API with requests
if os.path.exists(cache_file):
    with open('cache.json', 'rt') as json_file:
        cache = json.load(json_file)
else:
    cache = {}

if 'articles' in cache:
    articles = cache["articles"]
else:
    articles = []
cached_titles = set(map(lambda a: a["original_title"], articles))

uncached_titles = filter(lambda t: t not in cached_titles, use_these_original_titles)

# just uses the real title as is as the prompt for generating the fake title
# TODO is there a better way to generate seed text than this?
generate_articles = []
for title in uncached_titles:
    seed = title
    generate_articles.append({'original_title': title, 'seed_title': seed})

# generates titles based on the seeds, then generates article bodies for those titles
print('Generating %i new articles...' % len(generate_articles))
for article in generate_articles:
    article['title'] = grover.generate_article_title(article['seed_title'])
    article['article'] = grover.generate_article_body(article['title'])
print('Done generating %i new articles' % len(generate_articles))

# saves generated articles so they can be reused later
for article in generate_articles:
    articles.append(article)

cache["articles"] = articles
with open(cache_file, 'wt') as json_file:
    json.dump(cache, json_file)

# the articles to actually display in the results
display_articles = [article for article in articles if article['original_title'] in use_these_original_titles]


# TODO try generating authors?
# TODO replace with better persistence mechanism (ex: SQL database)

@app.route('/')
def top_news():
    body = ''
    i = 1
    for article in display_articles:
        body += '<b>Article ' + str(i) + '.</b><br><br>'
        body += '<b>Original headline: </b>' + article['original_title'] + '<br><br>'
        body += '<b>Seed headline: </b>' + article['seed_title'] + '<br><br>'
        body += '<b>Generated headline: </b>' + article['title'] + '<br><br>'
        body += '<b>Generated body: </b>' + article['article'].replace('\n', '<br><br>') + '<br><br><br><br>'

        i += 1

    return body


if __name__ == '__main__':
    app.run()
