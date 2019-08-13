import json
from datetime import date

import requests

grover_url = 'https://api.grover.allenai.org/api/ask'


def request_json():
    return {
        "target": "",
        "meta": {
            "title": "",
            "summary": "",
            "text": "",
            "domain": "",
            "url": "",
            "publish_date": "",
            "authors": ""
        }
    }


headers = {"Accept": "application/json, text/plain, */*",
           "Content-Type": "application/json;charset=utf-8",
           "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:67.0) Gecko/20100101 Firefox/67.0"}


def generate_article_title(prompt, grover_parameters=None):
    if grover_parameters is None:
        grover_parameters = {}

    request_body = request_json()
    request_body["meta"]["publish_date"] = date.today().strftime("%B %d, %Y")

    for k, v in grover_parameters.items():
        request_body[k] = v

    request_body["target"] = "title"

    # TODO putting the prompt as the article's body seems to have some impact on making the generated title relate to
    #  the prompt, but the model is expecting an actual article body, not arbitrary text, so this may behave unexpectedly
    request_body["meta"]["text"] = prompt

    # todo testing
    print('Making grover query for title with this config:')
    print(json.dumps(request_body))

    grover_response = requests.post(grover_url, json=request_body, headers=headers)
    return grover_response.json()['gen']


def generate_article_body(article_title, grover_parameters=None):
    if grover_parameters is None:
        grover_parameters = {}

    request_body = request_json()
    request_body["meta"]["publish_date"] = date.today().strftime("%B %d, %Y")

    for k, v in grover_parameters.items():
        request_body[k] = v

    request_body["target"] = "article"
    request_body["meta"]["title"] = article_title

    # todo testing
    print('Making grover query for body with this config:')
    print(json.dumps(request_body))

    grover_response = requests.post(grover_url, json=request_body, headers=headers)

    if grover_response.status_code != 200:
        print('ERROR with grover, code:', grover_response.status_code)
        print('Request JSON:')
        print(request_body)

    return grover_response.json()['gen']
