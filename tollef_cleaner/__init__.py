import re
from tollef_tokenizer import Tokenizer

"""
remove multiple newlines and replace with space
"""
def clear_multiple_lines(text):
  return re.sub(r"(\n+)(?=[A-Z])", " ", text)

"""
Remove "newspaper hyphens", often occurring after an introductory sentence by metadata
"""
def clear_newspaper_hyphen(text):
  # do not remove hyphens that are well within the text.
  if '--' in text[:50]:
    newspaper_hyphen = text.index('--')
    return text[newspaper_hyphen + 2 :]
  else:
    return text

"""
Replace ( by -LRB- and ) by -RRB-
"""
def translate_brackets(text):
  text = re.sub(r"([(]+)", '-LRB-', text)
  text = re.sub(r"([)]+)", '-RRB-', text)
  return text
# alternative, remove them:
def remove_brackets(text):
  text = re.sub(r"(-LRB-)", '', text)
  text = re.sub(r"(-RRB-)", '', text)
  return text


"""
Replace multiple spaces and tabs by a single space
"""
def replace_multiple_space(text):
  return re.sub(r"\s\s+", " ", text)

"""
Remove unwanted characters from words (+For => For)
"""
def clean_individual_words(text, tokenizer):
  tokens = []
  for tok in tokenizer.whitespace(text):
    clean = re.findall(r"([a-zA-Z0-9,._'\$()-]+|[\$T\$]+)", tok)
    if len(clean) == 1:
      tokens.append(clean[0])
  return ' '.join(tokens).strip()

"""
Due to formatting of strise, some texts end in multiple punctuations
"""
def strip_repeated_punct(text):
  return re.sub(r"([.]+)", '.', text)

class Cleaner(object):
  def __init__(self):
    self.text = None
    self.tokenizer = Tokenizer()

  def set_text(self, text):
    self.text = text

  def clean(self, text, remove_newspaper_hyphen=False, keep_brackets=False):
    if text:
      self.set_text(text)
    t = self.text

    if remove_newspaper_hyphen:
      t = clear_newspaper_hyphen(t)

    if keep_brackets:
      t = translate_brackets(t)
    else:
      t = remove_brackets(t)

    t = replace_multiple_space(t)

    t = clear_multiple_lines(t)

    t = clean_individual_words(t, self.tokenizer)

    return t
