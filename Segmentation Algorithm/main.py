from argparse import ArgumentParser

from Cleaner import Cleaner
from Spanbert import SpanBert
from entitycentric import entity_centric_segmentation

cleaner = Cleaner()
model = SpanBert()

def write(f, text, tar, sent):
  f.write(text)
  f.write("\n")
  f.write(tar)
  f.write("\n")
  f.write(sent)
  f.write("\n")

def segmentation(text, tar):
  text = text.replace("$T$", tar)
  text = cleaner.clean(text)

  clusters = model.predict(text)
  tokens = model.get_tokens()

  return entity_centric_segmentation(clusters,
    tokens,
    tar,
    min_dist=15,
    anaphora_only=False,
    bypass_segmentation=False,
    original_target=False
  )

def write_corefs(source, out):
  with open(out, "w", encoding="utf8") as outfile:
    with open(source, "r", encoding="utf8") as infile:
      lines = infile.readlines()
      # first, write all original files to the new augmented one
      # outfile.writelines(lines)
      step = 3  # iterate text, sentiment, entity_name
      for i in range(0, len(lines), step):
        text = lines[i].strip()
        tar = lines[i+1].strip()
        sentiment = lines[i+2].strip()
        segments = segmentation(text, tar)

        text = cleaner.lrb_rrb(text)  # convert ( and ) to -LRB- and -RRB-
        # write(outfile, text, tar, sentiment)
        if not segments:
          continue
        for segment in segments:
          #print("SEGMENT:\n", segment, end="\n\n")
          segment = cleaner.lrb_rrb(segment)
          write(outfile, segment, tar, sentiment)


if __name__ == "__main__":
  parser = ArgumentParser()

  parser.add_argument("--source", required=True, help="input data")
  parser.add_argument("--out", required=True, help="file to write to")

  args = parser.parse_args()

  source, out = args.source, args.out

  write_corefs(source, out)


