import calendar
from datetime import datetime

from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport

from config import AUTH_KEY, BASE_URL
from helpers import get_params, get_quarters, get_isodate
from query import QUERY
from wikidata import TOPICS

import json
import os

client = Client(transport=RequestsHTTPTransport(
  url=BASE_URL,
  headers={"Authorization": "Bearer {key}".format(key=AUTH_KEY)},
  use_json=True
))

def make_path(root, folder):
  path = os.path.join(root, folder)
  if not os.path.exists(path):
    os.mkdir(path)
  return path

downloads = make_path(os.getcwd(), 'downloads_evaluation')

# we want approx 2000 labeled articles in total.
# divided by 4 topics: 500 each
# 4 quarters: 125 each quarter
print(TOPICS)
year = 2020

april_start, april_end = get_isodate(4, 4, 2020)
print(april_start, april_end)

for topic in TOPICS:
  topic_path = make_path(downloads, topic.name)
  quarter = 0
  
  _file = "{}.json".format(year)
  _path = os.path.join(topic_path, _file)

  if os.path.isfile(_path):
    print("{} exists, skipping".format(_path))
    continue

  print(_path)
  PARAMS = get_params(None, april_start, april_end, topic.ids, first=25)
  res = client.execute(QUERY, PARAMS)
  with open(_path, "w") as tmp:
    tmp.write(json.dumps(res))
