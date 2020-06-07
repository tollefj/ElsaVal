from Tokenizer import Tokenizer

class Segmenter(object):
  def __init__(self):
    self.tokenizer = Tokenizer()
    self.text = None
    self.SENTENCE_THRESHOLD = 15
    self.segments = None
    self.mask = "$T$"

  def add_document(self, coref_tokens):
    # input: tokens with masks as coreferences
    t = ' '.join(coref_tokens)
    # strip wrongly parsed tokens
    t = t.replace("$ T $", self.mask)
    t = t.replace("$ T$", self.mask)
    t = t.replace("$T $", self.mask)
    double_mask = self.mask + " " + self.mask
    t = t.replace(double_mask, self.mask)
    self.text = t

  def init_segments(self):
    # get sentences
    sentences = self.tokenizer.sentences(self.text)
    segments = None  # init empty segments
    no_valid_sents = False
    while len(sentences[0]) < self.SENTENCE_THRESHOLD or self.mask not in sentences[0]:
      sentences.pop(0)
      if len(sentences) == 0:
        no_valid_sents = True
        break
    else:
      segments = [sentences[0]]
    if no_valid_sents:
      return

    for sent in sentences[1:]:  # iterate the rest
      if len(sent) < self.SENTENCE_THRESHOLD:
        continue
      if self.mask in sent:
        segments.append(sent)
      else:
        segments[-1] += " " + sent

    self.segments = segments


  def pipeline(self, coref_tokens):
    self.add_document(coref_tokens)
    self.init_segments()
    return self.segments
    