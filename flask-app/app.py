import json

import requests
from flask import Flask

app = Flask(__name__)

# todo use dynamic headlines taken from reuters rss or elsewhere
headline = 'Blast-hit tankers to be assessed off UAE coast'

grover_url = 'https://api.grover.allenai.org/api/ask'
# todo use correct date, author(s), domain
request_json_str = """{
  "target": "article",
  "title": "%s",
  "article": "",
  "domain": "nytimes.com",
  "date": "June 16, 2019",
  "authors": ""
}""" % headline

grover_response = requests.post(grover_url, json=json.loads(request_json_str),
                                headers={"Accept": "application/json, text/plain, */*",
                                         "Content-Type": "application/json;charset=utf-8",
                                         "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:67.0) Gecko/20100101 Firefox/67.0"})

generated_body = grover_response.json()['gen'].replace('\n', '<br>')


@app.route('/')
def hello_world():
    return '<b>Headline prompt:</b> ' + headline + '<br><br><br><b>Grover-generated body: </b><br>' + generated_body


if __name__ == '__main__':
    app.run()
