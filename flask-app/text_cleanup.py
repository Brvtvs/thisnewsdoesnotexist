import re

strip_from_anywhere = [
    'Ad Policy',
    'AlertMe',
    "ADVERTISING Read more",
    'ADVERTISEMENT',
    "And please follow Alex Parker on Twitter and Facebook.",
    "Please send me information on current events (all items on RedState.com).",
    "Please enable Javascript to watch this video",
    "Download the ERR News app for Android and iOS now and never miss an update!",
    "READ THE REST",
]
strip_from_anywhere_nocase = list(map(lambda s: re.compile(s, re.IGNORECASE), [
    '\(reuters\)',
    '\(AFP\)',
    '\(AP\)',
    '© 2019 AFP',
    "Copyright © 2018 by Creative Commons\. All rights reserved\. This material may not be published, broadcast, rewritten or redistributed\.? ?",
    "This work is licensed under a Creative Commons Attribution-Share Alike 3\.0 License\.? ?",
    "Neuer Inhalt Horizontal Line",
    "^,",
    "Have a tip\? Tell us\. nj\.com/tips",
    "This slideshow requires JavaScript\.?",
    "Ruth Marcus' email address is ruthmarcus@washpost\.com\.?",
    "\(c\) 2019, Washington Post Writers Group\.?",
    "Follow Labor Party and Progressives@RedState\.com for more on the Left and right\.?",
    "Get the latest updates right in your inbox\.?",
    "Subscribe to NJ\.com’s newsletters\.",
]))
strip_paragraphs_nocase = list(map(lambda s: re.compile(s, re.IGNORECASE), [
    "^Related$",
    "^Read the full article here\.?$",
    "^Story Continued Below?:\.?$",
    "^By AFP$",
    "^Share:?$",
    "^Shares:?$",
    "First posted\.? ?",
    "^#?#?#?$",
    "^Watch the president’s remarks below:?$",
    "^Source: http://commondreams.org$",
    "^[? ?Video is not available to stream or download.? ]?$",
    "^With Post wires$",
    "^Find all my RedState work here\.?$",
    "^About the Author:?$",
    "^Imported and Older Comments:?$",
    "^Featured image: Pool/Getty Images$",
    "^SWI swissinfo\.ch on Instagram SWI swissinfo\.ch on Instagram$",
    "^AGENCE FRANCE-PRESSE$",
    "^\(Repeats for more subscribers with no changes to text\)$",
    "^Copyright Associated Press\.?$",
    "^From PA$",
    "^Bloomberg\.com$",
    "^-? Advertisement –?$",
    "^Continue Reading Below$",
    "^Read the full article ?»?$",
    "^MA$",
    "^Relevant RedState links in this article.*$",
    "^SEE MORE VIDEOS$",
    "^Reuters/AP$",
    "^Read more:?$",
    "^\(?BBC\)?$",
    "^Learn more at: mru.ca$",
    "^T?h?e? ?Associated Press$",
    "^Updated$",
    "^Comments$",
    "^\(?Adds LSE comment, detail\)?$",
    "^©? ?Thomson Reuters 2019$",
    "^World$",
    "^business$",
    "^technology$",
    "^sports$",
    "^health$",
    "^entertainment$",
    "^advertisement$",
    "^Breaking News World$",
    "^AP$",
    "^Don’t Miss:$",
    "^Watch more above\.?$",
    "^Follow Labor Party and Progressives@RedState\.com for more on the Left and right\.$",
    "^Breaking News National$",
    "^National$",
    "^Subscribe to Sports Now newsletter By clicking Sign up, you agree to our privacy policy\.?$",
    "^\(Keystone\)?$",
    "^swissinfo\.ch with agencies/dos$",
    "^swissinfo EN Teaser Join us on Facebook! swissinfo\.ch Join us on Facebook!$",
    "^Follow Colvin on Twitter at https://twitter\.com/colvinj$",
    "^© 2018 AFP$",
    "^Follow \w+(\s\w+)?\son Twitter.*",
    "^Share on Facebook SHARE$",
    "^Share on \w+(\s\w+)$",
    "^Reuters$",
    "^Photo(:\s\w+)?$",
    "^Story continues below…?:?\.?$",
    "^If you have an iPhone and want to comment, select the box with the upward arrow at the bottom of your screen; swipe left and choose “Request Desktop Site.” You may have to do this several times before the page reloads. Scroll down to the red horizontal bar that says “Show Comments.”$",
    "^This article is over \w+ months old\.?$",
    "^\(?Adds details, context\)?$",
]))

# todo block title-like paragraphs at the end of the article? Often may be non-existent links to other articles

# todo implement
strip_sentences_with_prefix = [
    "Read the full story at",
    "Editorial:",
    "READ MORE:",
    ">>Also check out:",
    "This content was published on",
    "Topics: ",
    "FILE PHOTO: ",
]
# todo implement
strip_sentences_nocase = [
    "Follow Trend on Telegram.",
    "Only most interesting and important news"
]


def clean_body(body: str):
    lines = body.splitlines()
    filtered_lines = []

    for i in range(len(lines)):
        line = lines[i]

        for strip_regex in strip_from_anywhere_nocase:
            line = strip_regex.sub('', line)

        for strip in strip_from_anywhere:
            line = line.replace(strip, '')

        line = line.strip()

        include = True

        for strip_regex in strip_paragraphs_nocase:
            if strip_regex.match(line) is not None:
                include = False
                break

        # Addresses lines like "By Susan B. Parker"
        if line.lower().startswith('by ') or line.lower().startswith('story by ') \
                or line.lower().startswith('reporting by ') and len(line.split()) <= 5:
            include = False

        line = line.strip()

        # removes duplicate lines one after the other
        if len(filtered_lines) > 0 and filtered_lines[len(filtered_lines) - 1] == line:
            include = False

        if include and len(line) > 0:
            filtered_lines.append(line)
    if len(filtered_lines) > 0:
        last_line = filtered_lines[len(filtered_lines) - 1]

        if last_line.lower().startswith('reporting by ') or last_line.lower().startswith('(reporting by ') \
                or last_line.lower().startswith('this article was written by ') or last_line.lower().startswith(
            'additional reporting by ') or last_line.lower().startswith('(additional reporting by '):
            filtered_lines = filtered_lines[:-1]

    # todo strip any errant periods?

    return '\n'.join(filtered_lines).strip()


def is_body_irreparable(body: str):
    """Gets whether the generated body of an article should just be thrown out."""
    body = clean_body(body)

    # throws out all-caps articles because grover periodically generates "articles" that are really transcripts that
    # tend to be completely nonsensical
    lower_count = 0
    upper_count = 0
    for i in body:
        if i.islower():
            lower_count += 1
        elif i.isupper():
            upper_count += 1
    if upper_count > lower_count:
        return True

    return False


filter_titles_with = list(map(lambda s: re.compile(s, re.IGNORECASE), [
    "john mccain",
    "senator mccain",
    "theresa may",
    "pm may",
    "paul ryan",
    "speaker ryan",
    "video",
    "\[watch\]",
    "\[video\]",
]))


def is_title_irreparable(title: str):
    for bad_regex in filter_titles_with:
        if bad_regex.match(title) is not None:
            return True

    return False
