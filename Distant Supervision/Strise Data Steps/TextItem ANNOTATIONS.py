import re
from tollef_tokenizer import Tokenizer
from text_cleaning import clear_multiple_lines
from text_cleaning import clear_newspaper_hyphen
from text_cleaning import clean_individual_words
from text_cleaning import strip_repeated_punct

def get_if_exists(object, key):
  if key in object:
    return object[key]
  return None

class TextItem(object):
  def __init__(self, data):
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
    person_relations = ["occupation", "position_held", "spouse"]
    business_relations = ["topic_itpc", "owner_of", "employer", "chief_executive_officer"]

    # relations_to_process = ["said_to_be_the_same_as"]
    relations_to_process = []  # use this to only include people and companies
    relations_to_process.extend(person_relations)
    relations_to_process.extend(business_relations)

    valid_relations = []
    # TODO: add a Relation class to each unique entity, and populate it separately
    relation_object = get_if_exists(entity, "relations")
    if not relation_object:
      return None

    relations = get_if_exists(relation_object, "edges")

    for rel in relations:
      rel_node = get_if_exists(rel, "node")
      if rel_node:
        rel_to = get_if_exists(rel_node, "name")
        if rel_to:
          rel_details = get_if_exists(rel, "relationship")
          rel_type = get_if_exists(rel_details, "name")
          if rel_type in relations_to_process:
            valid_relations.append((rel_type, rel_to))

    if len(valid_relations) > 0:
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
      # we are only interested in the annotations for the entity
      # the annotation is a singular list
      annotation = get_if_exists(entity_object, "annotations")
      if not annotation:
        continue
      else:
        annotation = annotation[0]

      extractors = self.get_annotation_extractors(annotation)
      
      # offset must exist to identify location of entity, continue if not found
      offset = self.get_annotation_offset(annotation)
      if not offset and offset != 0:
        offset = None

      # annotated entity, shorthand ent for simple usage
      entity = get_if_exists(annotation, "entity")
      if not entity:
        continue

      # this is now a valid entity

      entity_name = get_if_exists(entity, "name")
      if not entity_name:
        continue

      if ("mahmood") in entity_name.lower():
        print(entity)

      relations = self.get_entity_relations(entity)

      references = set()

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
        if a != entity_name:
          references.add(a)

      # parse everything
      entity_text = self.text  # make a copy of the originally passed text
      # match words, names, hyphens and apostrophes
      regex_pattern = re.compile("([a-zA-Z0-9_'-]+)")

      for ref in references:
        if not regex_pattern.fullmatch(ref):  # avoid non-alphanumeric aliases
          continue

        is_multi_word = len(ref.split()) > 1
        if is_multi_word:
          entity_text = entity_text.replace(ref, self.mask)
        else:
          # try:
          entity_text = re.sub(r"\b{}\b".format(ref), self.mask, entity_text)
          # except Exception:
          #   print("_______________")
          #   print(annotation)
          #   print(ref)
          #   print(entity_text)
          #   print("_______________")

      # now, the entity text is updated where each reference to the root entity is masked as $T$
      # replace all $T$-era, $T$'s and other concatenated masks
      damaged_masks = []
      for whitespace_token in entity_text.split():
        if self.mask in whitespace_token:
          damaged_masks.append(whitespace_token)
      for bad_mask in damaged_masks:
        entity_text = entity_text.replace(bad_mask, self.mask)
      # this restored text may be used for coreference!
      # handle coreference with the entity text, restoring masks to the one root entity

      # use spaCy to tokenize text
      sentences = self.tokenizer.sentences(entity_text)

      for sentence in sentences:
        masks = sentence.count(self.mask)
        if masks == 0 or masks > 1:  # skip > 1 if we want multiple masks.
          continue

        if len(sentence) < 50:
          continue

        parsed_entities.append({
          "id": self.id,  # the document id, not the entity id
          "entity_id": get_if_exists(entity, "id"),
          "name": entity_name,
          "description": entity["description"],
          "text": sentence,
          "references": ','.join(references),  # return a string with comma separations
          "offset": offset,
          # "aliases": aliases,
          # "relations": relation_names
        })

    return parsed_entities