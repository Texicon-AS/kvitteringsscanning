#! Src: https://spacy.io/usage/linguistic-features
# FIXME: consider to rename ths example
import spacy
from spacy import displacy


nlp = spacy.load("en_core_web_sm")
# Merge noun phrases and entities for easier analysis
# FIXME: how does the "spacy" pipes work? what is the point (of the pipes)? how do they changE=improve the predictins? <-- a nested filter?
nlp.add_pipe("merge_entities")
nlp.add_pipe("merge_noun_chunks")

TEXTS = [
    "Net income was $9.4 million compared to the prior year of $2.7 million.",
    "Revenue exceeded twelve billion dollars, with a loss of $1b.",
]
# FIXME: use below to fethc moneys nivovled in a givne contract?
for doc in nlp.pipe(TEXTS):
    for token in doc:
        if token.ent_type_ == "MONEY":
            # We have an attribute and direct object, so check for subject
            if token.dep_ in ("attr", "dobj"):
                subj = [w for w in token.head.lefts if w.dep_ == "nsubj"]
                if subj:
                    print(subj[0], "-->", token)
            # We have a prepositional object with a preposition
            elif token.dep_ == "pobj" and token.head.dep_ == "prep":
                print(token.head.head, "-->", token)

if(True): #! Visualizing dependencies []
  # FIXME: merge below and above
  nlp = spacy.load("en_core_web_sm")
  doc = nlp("Autonomous cars shift insurance liability toward manufacturers")
  # Since this is an interactive Jupyter environment, we can use displacy.render here
  svg = displacy.render(doc, style='dep')
  #svg = spacy.displacy.render(doc, style="dep")
  import pathlib;
  import os;
  output_path = pathlib.Path(os.path.join("./", "sentence.svg"))
  output_path.open('w', encoding="utf-8").write(svg); #! [https://stackoverflow.com/questions/55723812/when-i-save-the-output-of-displacy-renderdoc-style-dep-to-a-svg-file-there]
  #displacy.serve(doc, style="ent"); #! ie, starts a server
if(True): #! Named Entity Recognition []
  # FIXME: merge below and above
  nlp = spacy.load("en_core_web_sm")
  doc = nlp("Apple is looking at buying U.K. startup for $1 billion")
  print("Apple:");
  for ent in doc.ents:
    print(ent.text, ent.start_char, ent.end_char, ent.label_)
if(True): #! Accessing entity annotations and labels []
  # FIXME: merge below and above
  nlp = spacy.load("en_core_web_sm")
  nlp = spacy.load("en_core_web_sm")
  doc = nlp("San Francisco considers banning sidewalk delivery robots")

  # document level
  ents = [(e.text, e.start_char, e.end_char, e.label_) for e in doc.ents]
  print("ents=", ents)

  # token level
  ent_san = [doc[0].text, doc[0].ent_iob_, doc[0].ent_type_]
  ent_francisco = [doc[1].text, doc[1].ent_iob_, doc[1].ent_type_]
  print(ent_san)  # ['San', 'B', 'GPE']
  print(ent_francisco)  # ['Francisco', 'I', 'GPE']
if(True): #! Word vectors and semantic similarity []
  # FIXME: merge below and above
  nlp = spacy.load("en_core_web_sm")
  #nlp = spacy.load("en_core_web_md")
  tokens = nlp("dog doga cat banana afskfsd")
  print("\n\n# Word vectors and semantic similarity:")
  for token in tokens:
    # fIXME: what is the meanign fo the below "token.vector_norm"?
    print(token.text, token.has_vector, token.vector_norm, token.is_oov)
