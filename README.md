# ElsaVal - A Framework for Entity-level Sentiment Analysis
Augmenting Entity-Level Sentiment Analysis with Coreference Resolution
___
This framework consists largely of three parts:
1. Dataset generation through distant supervision with knowledge graphs
2. Model framework for classification
3. Segmentation algorithm to be used for augmentation

Another README can be found in the Model framework (`Models and Classification` folder).

___
# Distant Supervision setup
This requires access to the Strise knowledge graph, by inserting an `AUTH_KEY` which can be provided upon request. The steps required to run the system are as follows:
- GraphQL Downloader (requiring `AUTH_KEY`)
  - Run `main.py` with the desired query, found in `query.py`, and the topics defined in `wikidata.py`
- Strise Data Handler
  - Step 1: converts graphql output to a structured CSV with the segmentation algorithm found in `TextItem.py`
  - Step 2: manipulates the CSV and predicts sentiment through distant supervision
  - Step 3: data analysis and output as `.litesent` format
  - Step 4: (optional) augmentation part, later moved to another system, incorporating a better segmentation algorithm, found in `Segmentation` folder.
  
___
# Segmentation Algorithm with Coreference Resolution Augmentation
The algorithm is initially used in `main.py`, where the SpanBERT model calculates clusters and tokens.
The files `entitycentric.py` and `Segmenter.py` comprises the final algorithm.

Run by calling `main.py` with the arguments ``--source`` and ``--out'', for the input data and the new file to write to, respectively.
- Example:
  - `python main.py --source gold_labeled.litesent --out gold_labeled_coref.litesent`
  
The gold labeled dataset is included in this folder.
