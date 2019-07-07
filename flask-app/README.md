###Installation
1. Install dependencies in requirements.txt.
2. Download spacy english model with `python -m spacy download en_core_web_sm`

###Endpoints
```
GET /api/v1/articles

Purpose: Returns the most recent articles from a given news feed. 

parameters:
- feed: the news feed you want to pull from. The current options are 'top-news', 'world', 'business', 'technology', 'politics', 'health', 'entertainment', and 'sports'
- quantity: the maximum number of articles to return

Example: if you wanted 10 articles for the front page, you'd do:
http://<host>/api/v1/articles?feed=top-news&quantity=10
```
```
GET /api/v1/article/<date>/<id>

Purpose: gets the contents of a specific article from its publication date and its id.

For example: 
http://<host>/api/v1/article/2019-07-06/trump-clogs-the-toilet-in-the-white-house-again
```