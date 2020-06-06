import calendar
from datetime import datetime

from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport

from config import AUTH_KEY, BASE_URL
from helpers import get_params, get_quarters
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

downloads = make_path(os.getcwd(), 'downloads')

# we want approx 2000 labeled articles in total.
# divided by 4 topics: 500 each
# 4 quarters: 125 each quarter
print(TOPICS)
years = [2018, 2019, 2020]
for year in years:
  print("Handling year: {}".format(year))
  for topic in TOPICS:
    topic_path = make_path(downloads, topic.name)
    quarter = 0
    print("Handling topic: {}".format(topic))
    for _from, _to in get_quarters(year):
      quarter += 1
      Q = "{}_Q{}.json".format(year, quarter)
      quarter_path = os.path.join(topic_path, Q)

      if os.path.isfile(quarter_path):
        print("{} exists, skipping".format(quarter_path))
        continue

      print(quarter_path)
      print("Topic: {}, {}-{}".format(topic.name, _from, _to))

      # cursor does not need to be implemented yet
      PARAMS = get_params(None, _from, _to, topic.ids, first=125)
      # 100 each Q, 400 a year, 4 topics is 1600 per year
      # 2 years: 3200 + 1quarter in 2020: 3600 total docs
      res = client.execute(QUERY, PARAMS)
      with open(quarter_path, "w") as tmp:
        tmp.write(json.dumps(res))

      # page_info = res["events"]["pageInfo"]
      # print(json.dumps(page_info))
