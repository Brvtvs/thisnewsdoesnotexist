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
