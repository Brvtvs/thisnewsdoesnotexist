from datetime import datetime, timedelta

import nltk.data
import pytz
from tzlocal import get_localzone

from text_cleanup import clean_body

nltk.download('punkt')

max_preview_char_length = 450
min_preview_char_length = 300
max_preview_lines = 4


def get_clean_article_text(article):
    return clean_body(article['generated_body'])


def get_article_preview_text(article):
    preview = ''

    lines = get_clean_article_text(article).splitlines()
    for line in lines[:max_preview_lines]:
        # adds lines until reaching max length
        if len(preview) + len(line) < max_preview_char_length:
            preview += '<br><br>' + line

        # if next line surpasses max length, but we are far below what we want, truncates the last line to get closer to target length.
        elif len(preview) < min_preview_char_length:
            last_line_sentences = nltk.tokenize.sent_tokenize(line)
            preview += '<br><br>'
            for sentence in last_line_sentences:
                if len(preview) != 0 and len(preview) + len(sentence) > max_preview_char_length:
                    break
                preview += ' ' + sentence
            break

        else:
            break

    return preview.strip('<br><br>').strip()


def date_as_time_ago(time):
    """
    Get a datetime object or a int() Epoch timestamp and return a
    pretty string like 'an hour ago', 'Yesterday', '3 months ago',
    'just now', etc
    """

    # makes up for the fact that we're taking predominantly from EU-timestamped articles
    local_tz = get_localzone()
    now = local_tz.localize(datetime.now())
    source_tz = pytz.utc

    if type(time) is int:
        diff = now - source_tz.localize(datetime.fromtimestamp(time))
    elif type(time) is str:
        diff = now - source_tz.localize(datetime.strptime(time, '%Y-%m-%d %H:%M:%S'))
    elif isinstance(time, datetime):
        diff = now - source_tz.localize(time)

    second_diff = diff.seconds
    day_diff = diff.days

    if day_diff < 0:
        return ''

    if day_diff == 0:
        if second_diff < 60:
            return str(second_diff) + " seconds ago"
        if second_diff < 120:
            return "1 minute ago"
        if second_diff < 3600:
            return str(int(second_diff / 60)) + " minutes ago"
        if second_diff < 7200:
            return "1 hour ago"
        if second_diff < 86400:
            return str(int(second_diff / 3600)) + " hours ago"
    if day_diff == 1:
        return "Yesterday"
    if day_diff < 7:
        return str(int(day_diff)) + " days ago"
    if day_diff < 31:
        return str(int(day_diff / 7)) + " weeks ago"
    if day_diff < 365:
        return str(int(day_diff / 30)) + " months ago"
    return str(int(day_diff / 365)) + " years ago"


def date_with_month_name(time):
    if type(time) is int:
        time = datetime.fromtimestamp(time)
    elif type(time) is str:
        time = datetime.strptime(time, '%Y-%m-%d %H:%M:%S')

    # corrects dates that may be in the future for users in the Western Hemisphere given that most of the timestamps are GMT
    time = time - timedelta(hours=5)

    return time.strftime("%B %d, %Y")
