from datetime import datetime, timedelta

import nltk.data

from text_cleanup import clean_body

nltk.download('punkt')

max_preview_char_length = 550


def get_clean_article_text(article):
    return clean_body(article['generated_body'])


def get_article_preview_text(article):
    # By default, uses first two lines of article body, separated by <br><br>
    lines = get_clean_article_text(article).splitlines()
    preview = '<br><br>'.join(lines[:2])

    # If first line is too long on its own, truncates it
    if len(lines[0]) > max_preview_char_length:
        sentences = nltk.tokenize.sent_tokenize(lines[0])
        preview = ''
        for sentence in sentences:
            if len(preview) != 0 and len(preview) + len(sentence) > max_preview_char_length:
                break
            preview += ' ' + sentence

    # If first two lines will be too long, uses just first if it is reasonably long
    elif len(preview) > max_preview_char_length and len(lines[0]) > 100:
        preview = lines[0]

    # todo deal with short first line and very long second one

    return preview.strip()


def date_as_time_ago(time):
    """
    Get a datetime object or a int() Epoch timestamp and return a
    pretty string like 'an hour ago', 'Yesterday', '3 months ago',
    'just now', etc
    """

    # makes up for the fact that we're taking predominantly from EU-timestamped articles
    now = datetime.now() + timedelta(hours=5)

    if type(time) is int:
        diff = now - datetime.fromtimestamp(time)
    elif type(time) is str:
        diff = now - datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
    elif isinstance(time, datetime):
        diff = now - time
    elif not time:
        diff = now - now
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
