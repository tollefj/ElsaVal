from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
# initialize transformer pipeline for SA
from transformers import pipeline

POSITIVE = 1
NEGATIVE = -1
NEUTRAL = 0

class SentimentLabel():
  def __init__(self, label, confidence):
    if isinstance(label, str):
      # convert this to an integer label
      self.label = self.convert_label(label)
    else:
      self.label = label

    self.confidence = confidence

  def convert_label(self, label):
    if "POS" in label:
      return POSITIVE
    elif "NEG" in label:
      return NEGATIVE
    else:
      return NEUTRAL

  def __str__(self):
    return "Label: {} (confidence: {})".format(self.label, self.confidence)

class TwoStepSentimentClassifier(object):
  def __init__(self):
    # self.text = None
    print("Init vader")
    self.vader = SentimentIntensityAnalyzer()
    print("Init DistilBERT SST-2")
    self.pipeline = pipeline("sentiment-analysis")

  def neutral_score(self, text):
      polarity = self.vader.polarity_scores(text)
      # from https://github.com/cjhutto/vaderSentiment
      # neutral sentiment: (compound score > -0.05) and (compound score < 0.05)
      comp = polarity["compound"]
      threshold = 0.12  # this probably needs to be altered.
      comp_neutral = -threshold < comp < threshold
      
      pos, neu, neg = polarity["pos"], polarity["neu"], polarity["neg"]
      neutral_highest = max([pos, neu, neg]) == neu

      # return both label and confidence
      if neutral_highest and comp_neutral:
        return SentimentLabel(NEUTRAL, confidence=neu)
      return None

  # compute sst-2 polarity from the distilbert pretrained model
  # returns
  # { label: positive/negative, score: int in range (0,1) }
  #def sst2(self, text):

    
  def label_and_confidence(self, text):
    # step 1, determine neutral or not from Vader
    sentiment = self.neutral_score(text)

    # if the text is opinionated (i.e. neutral = None), compute the sst-2 score
    if sentiment is None:
      sst2 = self.pipeline([text])[0]
      label = sst2["label"]
      score = sst2["score"]
      score = round(score, 4)
      sentiment = SentimentLabel(label, confidence=score)
    
    return sentiment
    # return int(round(score))