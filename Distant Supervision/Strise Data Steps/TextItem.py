import re
from tollef_tokenizer import Tokenizer
from text_cleaning import clear_multiple_lines
from text_cleaning import clear_newspaper_hyphen
from text_cleaning import clean_individual_words
from text_cleaning import strip_repeated_punct
from unidecode import unidecode

# define a set of valid "instance_of" identifiers
instance_people = ["human", "billionaire", "social status", "position"]
instance_companies = ["business", "industry", "economic sector", "stock market index",
  "stock exchange", "corporate title", "website", "brand", "enterprise", "company"]
instance_locations = ["country", "city", "sovereign state", "federal state", "city of the United States", "capital", "geographic region", "largest city"]
instance_others = ["profession", "taxon"]

valid_instance_ofs = [
  instance_people, instance_companies, instance_locations, instance_others
]

VALID_INSTANCES = []
for instances in valid_instance_ofs:
  VALID_INSTANCES.extend(instances)

def get_if_exists(object, key):
  if key in object:
    return object[key]
  return None

class TextItem(object):
  def __init__(self, data, lookup_dict=set(), limit_to_relations=False):
    self.LOOKUP = lookup_dict
    self.LIMIT = limit_to_relations
    # initialize the custom sentence tokenizer
    self.tokenizer = Tokenizer(lang="english")

    # return the node, containing all data for one text object
    self.data = data['node']

    self.mask = "$T$"  # the mask used to mask entities

    # unique id for the event
    self.id = self.data["id"]
    self.text = None
    self.parse_text(self.data["body"])


    self.entities = self.parse_entities()

  def parse_text(self, text):
    text = clear_multiple_lines(text)
    text = clear_newspaper_hyphen(text)
    text = clean_individual_words(text, tokenizer=self.tokenizer)
    text = strip_repeated_punct(text)
    self.text = text

        
  def get_text_object(self):
    return {
      'id': self.id,
      'text': self.text
    }


  def get_entities_object(self):
    return self.entities


  def get_annotation_extractors(self, annotation):
    extractors = get_if_exists(annotation, "extractors")
    # if extractors and "SPOTLIGHT" in extractors:
    if extractors:
      return ', '.join(extractors)
    return None


  def get_annotation_offset(self, annotation):
    offset = get_if_exists(annotation, "offset")
    if offset:
      offset_type = get_if_exists(offset, "__typename")
      if offset_type == "BodyOffset":
        # the offset type is defined as { offset: { offset: int }}
        offset_number = get_if_exists(offset, "offset")
        return offset_number
      else:
        return None
    else:
      return None


  def get_entity_aliases(self, entity):
    valid_aliases = []
    aliases = get_if_exists(entity, "aliases")
    if aliases:
      for alias in aliases:
        if not alias["disabled"] and alias["color"] != "BLACK":
          # alias colors can be WHITE, GRAY, BLACK
          # WHITE: proper alias match
          # GRAY: can be used for resolving disambiguations
          # BLACK: never use this
          valid_aliases.append(alias["value"])
    return valid_aliases


  def get_entity_relations(self, entity):
    # relations_to_process = [
    #   "occupation", "position_held", "spouse",
    #   "said_to_be_the_same_as", "subclass_of", "parent_concept",
    #   "instance_of", "topic_iptc"
    # ]
    """ Expanation

    people:
    - occupation (david ige => politician)
    - position_held (david ige => governor of hawaii)
    - spouse (donald trump => melania trump)
    generally:
    - said_to_be_the_same_as (actor => actress, artist)
    - subclass_of (screenplay => creative work)
    - parent_concept (banknote => cash)
    - instance_of (europe => continent)
    - topic_itpc (Norwegian Cruise Line => waterway and maritime transport)
    - owner_of (Royal Dutch Shell => Sakhalin Energy)
    - chief_executive_officer (Royal Dutch Shell => Ben van Beurden)
    """
    person_relations = ["occupation", "profession", "position_held", "spouse"]
    business_relations = ["topic_itpc", "owner_of", "leader", "chief_executive_officer", "headquarters_location", "parent_organization", "industry", "investor"]
    location_relations = ["capital", "country", "continent", "executive_body", "head_of_government", "head_of_state", "location", "located_in_the_administrative_territorial_entity"]
    product_relations = ["inception", "manufacturer", "developer", "discoverer_or_inventor", "designed_by", "founded_by"]
    arts_relations = ["composer", "director", "distributor", "genre", "producer", "production_company"]
    other_relations = ["creator", "owned_by", "used_by", "sport"]

    # relations_to_process = ["said_to_be_the_same_as"]
    relations_to_process = []  # use this to only include people and companies
    relations_to_process.extend(person_relations)
    relations_to_process.extend(business_relations)
    relations_to_process.extend(location_relations)
    relations_to_process.extend(product_relations)
    relations_to_process.extend(arts_relations)
    relations_to_process.extend(other_relations)

    valid_relations = []
    # TODO: add a Relation class to each unique entity, and populate it separately
    relation_object = get_if_exists(entity, "relations")
    if not relation_object:
      return None

    relations = get_if_exists(relation_object, "edges")

    #instance_ofs = []
    valid_subclasses = ["telephone", "mobile device", "television film", "film",
      "television series episode", "application", "leisure", "digital media",
      "interactive media", "online publication", "wearable technology", "computing platform",
      "live broadcast", "political organisation", "juridical person", "computer", "producer", "person"]

    # only apply the "said to be the same as"-relation if other relations are found
    same_as = []  

    for rel in relations:
      rel_node = get_if_exists(rel, "node")
      if rel_node:
        rel_to = get_if_exists(rel_node, "name")
        if rel_to:
          # if the relation exists in current text, and has been parsed as a root entity
          if rel_to in self.LOOKUP and rel_to in self.text:
            continue

          rel_details = get_if_exists(rel, "relationship")
          rel_type = get_if_exists(rel_details, "name")

          if "instance_of" in rel_type:
            if rel_to in VALID_INSTANCES:
              valid_relations.append((rel_type, rel_to))
          if "subclass_of" in rel_type:
            if rel_to in valid_subclasses:
              valid_relations.append((rel_type, rel_to))
          if "said_to_be_the_same_as" in rel_type:
            same_as.append((rel_type, rel_to))

          if rel_type in relations_to_process:
            valid_relations.append((rel_type, rel_to))

    valid_instance = True
    #for inst in instance_ofs:
    #  if inst in VALID_INSTANCES:
    #    valid_instance = True
    #    break
        # use the relations!

    if valid_instance and len(valid_relations) > 0:
      valid_relations.extend(same_as)
      return valid_relations
    #print(">>>\nDID NOT RETURN THESE ONES:")
    #print(relations)
    #rint()

    return None

    # if ent["relations"]:
    #   for rel in ent["relations"]["edges"]:
    #     if rel["node"]:
    #       rel_type = rel["relationship"]["name"]
    #       if rel_type in relations_to_process:
    #         rel_to = rel["node"]["name"]
    #         valid_relations.append(rel_to)


  def parse_entities(self):
    # all relevant data is held in annotations
    entities = get_if_exists(self.data, "entities")
    entity_edges = get_if_exists(entities, "edges")

    parsed_entities = []

    for entity_object in entity_edges:
      # all data resides in a node for each entity
      entity = get_if_exists(entity_object, "node")
      if not entity:
        continue
    
      entity_name = get_if_exists(entity, "name")
      if not entity_name:
        continue

      references = set()

      relations = self.get_entity_relations(entity)
      if not relations:
        if self.LIMIT:
          continue

      if relations and len(relations) > 0:
        # we don't care about the type of relation, just the relation entity itself
        for _, relname in relations:
          # leave piece-wise comparisons to the coreference system
          if relname not in entity_name:
            references.add(relname) 

      aliases = self.get_entity_aliases(entity)
      aliases = [a for a in aliases if len(a) < 30]  # make sure to not use invalid aliases (extremely long chemical names, etc.)
      aliases = aliases[:20]  # keep max 20 aliases

      for a in aliases:
        #if a != entity_name:
        references.add(a)

      # parse everything
      entity_text = self.text  # make a copy of the originally passed text
      entity_text = unidecode(entity_text)
      # match words, names, hyphens and apostrophes
      regex_pattern = re.compile("([a-zA-Z0-9_'-]+)")

      for ref in references:
        ref = unidecode(ref)
        # print("Checking {} in references".format(ref))
        regmatch = regex_pattern.match(ref)
        if not regmatch: # avoid non-alphanumeric aliases
          continue
        #elif len(ref) != len(regmatch[0]): # avoid invalid chars such as / $ etc.
        #  continue
        # print(">> Valid")

        is_multi_word = len(ref.split()) > 1
        if is_multi_word:
          entity_text = entity_text.replace(ref, self.mask)
        else:
          # try:
          entity_text = re.sub(r"\b{}\b".format(ref), self.mask, entity_text)
          # except Exception:
          #   print("_______________")
          #   print(ref)
          #   print(entity_text)
          #   print("_______________")
        #print("Entitytext\n{}".format(entity_text))
      maskcount = entity_text.count(self.mask)
      if maskcount > 0:
        # now, the entity text is updated where each reference to the root entity is masked as $T$
        # replace all $T$-era, $T$'s and other concatenated masks
        damaged_masks = []
        for whitespace_token in entity_text.split():
          if self.mask in whitespace_token and whitespace_token != self.mask:
            damaged_masks.append(whitespace_token)
        for bad_mask in damaged_masks:
          entity_text = entity_text.replace(bad_mask, self.mask)
        # this restored text may be used for coreference!
        # handle coreference with the entity text, restoring masks to the one root entity
      if maskcount == 0:
        continue

      # use spaCy to tokenize text
      sentences = self.tokenizer.sentences(entity_text)
      if not sentences:
        continue

      PARSE_AS_SENTENCES = False

      if PARSE_AS_SENTENCES:
        for sentence in sentences:
          masks = sentence.count(self.mask)
          if masks == 0: # or masks > 1:  # skip > 1 if we want multiple masks.
            continue
          # if len(sentence) < 50:
          #   continue

          parsed_entities.append({
            "id": self.id,  # the document id, not the entity id
            "entity_id": get_if_exists(entity, "id"),
            "name": entity_name,
            "description": entity["description"],
            "text": sentence,
            "references": ','.join(references),  # return a string with comma separations
            # "aliases": aliases,
            # "relations": relation_names
          })

      # generate segments... (21.05.20)
      # the entity_text item is already containing $T$, just make sure to segment these properly
      SENT_THRESHOLD = 25  # minimum length of sentences

      # initialize first valid sentence as segment.
      # goes under the assumption that the target must be in the first sentence.      segments = None
      no_valid_sentences = False

      while len(sentences[0]) < SENT_THRESHOLD or self.mask not in sentences[0]:
        sentences.pop(0)
        if len(sentences) == 0:
          no_valid_sentences = True
          break
      else:
        segments = [sentences[0]]
      if no_valid_sentences:
        continue
      
      for sent in sentences[1:]:
        if len(sent) < SENT_THRESHOLD:
          continue
        if self.mask in sent:
          segments.append(sent)
        else:
          segments[-1] += " " + sent

      MAX_SEG_LENGTH = 1024  # two maximum BERT segments

      for seg in segments:
        if len(seg) > MAX_SEG_LENGTH:
          continue
        # parse simple errors like double masking
        double_mask = self.mask + " " + self.mask
        seg = seg.replace(double_mask, self.mask)
        parsed_entities.append({
          "id": self.id,  # the document id, not the entity id
          "entity_id": get_if_exists(entity, "id"),
          "name": entity_name,
          # "description": entity["description"],
          "text": seg,
          "references": ','.join(references),  # return a string with comma separations
          # "aliases": aliases,
          # "relations": relation_names
        })

    return parsed_entities