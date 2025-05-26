"""
@file
@brief
"""
import spacy
nlp = spacy.load("en_core_web_sm")
import en_core_web_sm
nlp = en_core_web_sm.load()
doc = nlp("This is a sentence.")
print([(w.text, w.pos_) for w in doc]) #! which displays the grammer, thuse, uself when modelling

#! ---------------
#! Use the PhraseMatcher:
from spacy.matcher import PhraseMatcher

nlp = spacy.load("en_core_web_sm")
matcher = PhraseMatcher(nlp.vocab)
terms = ["Barack Obama", "Angela Merkel", "Washington, D.C."]
# Only run nlp.make_doc to speed things up
patterns = [nlp.make_doc(text) for text in terms]
matcher.add("TerminologyList", patterns)

doc = nlp("German Chancellor Angela Merkel and US President Barack Obama "
          "converse in the Oval Office inside the White House in Washington, D.C."
          " Angelas Merkel name was was partially misspelled" # which is not made part of the example due to the "s"
          )
matches = matcher(doc)
for match_id, start, end in matches:
    span = doc[start:end]
    print(span.text)
