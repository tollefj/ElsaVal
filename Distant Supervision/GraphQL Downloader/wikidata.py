topics = {
    "technology": "Q11016",
    "science": "Q336",
    "finance": "Q43015",
    "economics": "Q8134",
    "sports": "Q349",
    "politics": "Q8134"
}

class Topic:
    def __init__(self, name, ids):
        self.name = name
        self.ids = ids
    
    def __iter__(self):
        return iter(self.ids)

# wikidata IDs
TECH_ID = [topics["technology"], topics["science"]]
BUSINESS_ID = [topics["finance"], topics["economics"]]
SPORTS_ID = [topics["sports"]]
POLITICS_ID = [topics["politics"]]

IDS = [TECH_ID, BUSINESS_ID, SPORTS_ID, POLITICS_ID]
NAMES = ["tech", "business", "sports", "politics"]
TOPICS = [Topic(name, ids) for name, ids in zip(NAMES, IDS)]