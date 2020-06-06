import pandas as pd

class Converter(object):
  def __init__(self):
    self.doc = None
    self.df_columns = ["Text", "Entity", "Sentiment"]

  # read a file, save its lines as an iterable
  def read(self, doc):
    docs = []
    with open(doc, "r", encoding="utf8") as tmp:
      lines = tmp.readlines()
      for idx in range(0, len(lines), 3):
        text, entity, sentiment = lines[idx : idx + 3]
        docs.append([text.strip(), entity.strip(), sentiment.strip()])
    self.doc = docs

  def to_df(self, doc):
    # data is segmented into 3 lines
    self.read(doc)
    return pd.DataFrame(self.doc, columns=self.df_columns)
