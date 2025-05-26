"""!
@file
@brief exemplfeis basic cualisaiotn of how the terms relate
@remarks
- validation: [https://deepnote.com/@isaac-aderogba/Spacy-Food-Entities-2cc2d19c-c3ac-4321-8853-0bcf2ef565b3] expltly anntoates the traning-data with the mathes. However, they do not provide a system to evlauate unkown sentences <-- how should this be peromred?
"""
#! https://spacy.io/usage/visualizers
import sys;
sys.path.append("./");
import os;
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' #! used to hide the Tensofrlow deubing errors [https://stackoverflow.com/questions/35911252/disable-tensorflow-debugging-information]



import spacy
from spacy import displacy
from spacy.tokens import Span

import spacy
from spacy import displacy

text = "When Sebastian Thrun started working on self-driving cars at Google in 2007, few people outside of the company took him seriously."

nlp = spacy.load("en_core_web_sm")
doc0 = nlp(text)
#displacy.serve(doc0, style="ent")


nlp = spacy.load("en_core_web_sm")
doc1 = nlp("This is a sentence.")
doc2 = nlp("This is another sentence.")
html = displacy.render([doc1, doc2], style="dep", page=True)
print(html);
#
#
text = "Welcome to the Bank of China."

nlp = spacy.blank("en")
doc4 = nlp(text)

doc4.spans["sc"] = [
    Span(doc4, 3, 6, "ORG"),
    Span(doc4, 5, 6, "GPE"),
]

#displacy.serve([doc4], style="span")
#displacy.serve([doc0, doc1, doc2, doc4], style="sent")
#displacy.serve([doc0, doc1, doc2, doc4], style="span")
#displacy.serve([doc0, doc1, doc2, doc4], style="ent")
#displacy.serve([doc0, doc1, doc2, doc4], style="dep")
#displacy.serve(doc1, style="span")
#displacy.serve(doc2, style="span")
#displacy.serve(doc0, style="span")
displacy.serve(doc4, style="span")

#
#
#! "display sentence involving original entities"
#! Src: [https://deepnote.com/@isaac-aderogba/Spacy-Food-Entities-2cc2d19c-c3ac-4321-8853-0bcf2ef565b3]
# FIXME: try making use of the below
spacy.displacy.render(nlp("Apple is looking at buying U.K. startup for $1 billion"), style="ent")
# display sentences involving target entity
spacy.displacy.render(nlp("I had a hamburger and chips for lunch today."), style="ent")
spacy.displacy.render(nlp("I decided to have chocolate ice cream as a little treat for myself."), style="ent")
spacy.displacy.render(nlp("I ordered basmati rice, leaf spinach and cheese from Tesco yesterday"), style="ent")

if(False): # FIXME: write a permtaution fo the below where we use "named entities (ents)" to label our data) <-- related: get our "tut-train-entityRuler.py" to work for our data
    def display_doc(doc):
        colors = { "surgery": "pink",
                   "internalMedicine": "orange",
                   "medication": "lightblue",
                   "obstetricsGynecology": "lightgreen",
                  }
        options = {"ents": ["surgery",
                            "internalMedicine",
                            "medication",
                            "obstetricsGynecology",
                            ],
                   "colors": colors
                   }

        displacy.render(doc, style='ent',
                        options=options, jupyter=True)
        display_doc(doc)


#!
#! Step: save the model
nlp.meta["name"] = "food_entity_extractor_v2" # FIXME: update our approach with this line!
nlp.to_disk(".") # "./models/v2")
