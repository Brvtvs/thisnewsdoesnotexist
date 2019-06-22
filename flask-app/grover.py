import requests

grover_url = 'https://api.grover.allenai.org/api/ask'


# todo use correct date, author(s), domain
def request_json():
    return {
        "target": "",
        "title": "",
        "article": "",
        "domain": "nytimes.com",
        "date": "June 16, 2019",
        "authors": ""
    }


headers = {"Accept": "application/json, text/plain, */*",
           "Content-Type": "application/json;charset=utf-8",
           "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:67.0) Gecko/20100101 Firefox/67.0"}


def generate_article_title(prompt):
    request_body = request_json()
    request_body["target"] = "title"
    # TODO putting the prompt as the article's body seems to have some impact on making the generated title relate to
    #  the prompt, but the model is expecting an actual article body, not arbitrary text, so this may behave unexpectedly
    request_body["article"] = prompt
    grover_response = requests.post(grover_url, json=request_body, headers=headers)
    return grover_response.json()['gen']


def generate_article_body(article_title):
    request_body = request_json()
    request_body["target"] = "article"
    request_body["title"] = article_title
    grover_response = requests.post(grover_url, json=request_body, headers=headers)

    if grover_response.status_code != 200:
        print('ERROR with grover, code:', grover_response.status_code)
        print('Request JSON:')
        print(request_body)

    return grover_response.json()['gen']
