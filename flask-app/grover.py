import json
import os
import subprocess
import time
from datetime import date

import requests

grover_url_base = 'http://%s:8000'


def request_json():
    return {
        "meta": {
            "title": "",
            "summary": "",
            "text": "",
            "domain": "",
            "authors": "",
            "url": "",
            "publish_date": ""
        },
        "target": ""
    }


headers = {"Accept": "application/json, text/plain, */*",
           "Content-Type": "application/json;charset=utf-8",
           "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:67.0) Gecko/20100101 Firefox/67.0"}


def get_grover_url():
    file = "../tex-mex/scripts/running-instance-ip.txt"
    if not os.path.exists(file):
        raise Exception(
            "No IP address found in tex-mex/scripts/running-instance-ip.txt. Has an AWS instance been spun up yet?")
    with open(file, 'rt') as ip_file:
        ip = ip_file.readline()
        return grover_url_base % ip


def generate_article_title(prompt, grover_parameters=None):
    if grover_parameters is None:
        grover_parameters = {}

    request_body = request_json()
    request_body["meta"]["date"] = date.today().strftime("%B %d, %Y")

    for k, v in grover_parameters.items():
        request_body["meta"][k] = v

    request_body["target"] = "title"

    # TODO putting the prompt as the article's body seems to have some impact on making the generated title relate to
    #  the prompt, but the model is expecting an actual article body, not arbitrary text, so this may behave unexpectedly
    request_body["meta"]["text"] = prompt

    # todo testing
    print('Making grover query for title with this config:')
    print(json.dumps(request_body))

    grover_response = requests.post(get_grover_url(), json=request_body, headers=headers)
    return grover_response.json()['gen']


def generate_article_body(article_title, grover_parameters=None):
    if grover_parameters is None:
        grover_parameters = {}

    request_body = request_json()
    request_body["meta"]["date"] = date.today().strftime("%B %d, %Y")

    for k, v in grover_parameters.items():
        request_body["meta"][k] = v

    request_body["target"] = "article"
    request_body["meta"]["title"] = article_title

    # todo testing
    print('Making grover query for body with this config:')
    print(json.dumps(request_body))

    grover_response = requests.post(get_grover_url(), json=request_body, headers=headers)

    if grover_response.status_code != 200:
        print('ERROR with grover, code:', grover_response.status_code)
        print('Request JSON:')
        print(request_body)

    return grover_response.json()['gen']


def launch_ec2_instance():
    start = time.time()
    result = subprocess.run(['sh', '../tex-mex/scripts/create-instance.sh'], stdout=subprocess.PIPE).stdout.decode(
        'utf-8')
    print("Result of running create-instance.sh after %i seconds:" % (time.time() - start))
    print(result)
