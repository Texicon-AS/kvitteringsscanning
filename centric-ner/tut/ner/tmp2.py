"""
@file
@brief exemplfies ...
@remarks
- template: https://stackoverflow.com/questions/68003864/how-can-i-make-spacy-matches-case-insensitive
"""
import spacy
import pandas as pd

from spacy.pipeline import EntityRuler
nlp = spacy.load('en_core_web_sm', disable = ['ner'])
ruler = nlp.add_pipe("entity_ruler")

patterns = []
flowers = ["rose", "tulip", "african daisy"]
for f in flowers:
    patterns.append({"label": "FLOWER", "pattern": [{'LOWER': w} for w in f.split()]})
animals = ["cat", "dog", "artic fox"]
for a in animals:
    patterns.append({"label": "ANIMAL", "pattern": [{'LOWER': w} for w in a.split()]})

ruler.add_patterns(patterns)

result={}
doc = nlp("CAT and Artic fox, plant african daisy")
for ent in doc.ents:
        result[ent.label_]=ent.text

print([(ent.text, ent.label_) for ent in doc.ents])
