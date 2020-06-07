from Segmenter import Segmenter
segmenter = Segmenter()

"""
feed a model's clusters and tokens
define a target to look for
set a min dist, being the minimum distance required to be between coreferences
anaphora_only if only the head_antecedent should be matched to the target
masking if the references should be updated by a mask, used for sentiment classification
"""
def get_antecedents(clusters, tokens, min_refs=3, as_text=False):
  antecedents = []
  for c in clusters:
    cluster_mentions = []
    for m in c:
      mention = tokens[m[0] : m[1] + 1]
      cluster_mentions.append(mention)
    cluster_ant = max(cluster_mentions, key=len)
    if len(c) > min_refs:
      if as_text:
        antecedents.append(cluster_ant)
      else:
        antecedents.append(c)
  return antecedents

def entity_centric_segmentation(clusters, tokens, tar, min_dist=15, anaphora_only=False, bypass_segmentation=False, original_target=False):
  MASK = "$T$"
  root_clusters = []

  for c in clusters:
    if anaphora_only:
      head_antecedent = tokens[c[0][0] : c[0][1] + 1]
      if (tar in head_antecedent or tar in ' '.join(head_antecedent)):
        root_clusters.append(c)

    # compute both anaphora + cataphora
    else:
      for m in c:
        mention = tokens[m[0] : m[1] + 1]
        if (tar in mention or tar in ' '.join(mention)):
          root_clusters.append(c)
          break
    
  if len(root_clusters) == 0:
    return None

  if bypass_segmentation:
    return root_clusters

  coref_tokens = tokens.copy()

  for c in root_clusters:
    _start, _end = c[0]
    # remask antecedent
    coref_tokens[_start : _end + 1] = [MASK]
    offset = _end - _start

    last_mention_index = _end

    for mention in c[1:]:  # do not include root
      start, end = mention
      if end - last_mention_index > min_dist:
        start -= offset
        end -= offset
        # uncomment if the original text is desired to use
        # mention_text = coref_tokens[start : end + 1]
        coref_tokens[start : end + 1] = [MASK]
        offset += end - start
        last_mention_index = end

  segments = segmenter.pipeline(coref_tokens)
  if original_target:
    return [seg.replace(MASK, tar) for seg in segments]
  return segments
