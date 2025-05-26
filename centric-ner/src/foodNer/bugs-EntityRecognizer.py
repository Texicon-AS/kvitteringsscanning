assert(False) # FIXME: pre: understand how t correctly use "EntityRecognizer" ... then udpat ehte below! <--- the below are based on: https://stackoverflow.com/questions/67678987/whats-the-most-efficient-way-to-load-spacy-language-models-when-working-with-mu


import spacy
#from spacy.gold import GoldParse
from spacy.pipeline import EntityRecognizer
#from spacy.language import EntityRecognizer

nlp = spacy.load('en_core_web_sm')  # NER tags PERSON, GPE, ...
#nlp = spacy.load('en', entity = False, parser = False)

doc_list = []
doc = nlp('Llamas make great pets.')
doc_list.append(doc)
gold_list = []
#gold_list.append(GoldParse(doc, [u'ANIMAL', u'O', u'O', u'O']))

ner = EntityRecognizer(nlp.vocab, entity_types = ['ANIMAL'])
#ner.update(doc_list, gold_list)

# -------------
assert(False) # FIXME: whenm the above works ... then move this into a new tut-example ... and thereafter conie with the elow
# ----------------
# ==========================================================================================
# ==========================================================================================
# ==========================================================================================

import spacy # tested with v2.2.3
from spacy.pipeline import EntityRecognizer



text = "Jane lives in Boston. Jan lives in Bremen."

# load the English and German models
#nlp_en = spacy.load('en_core_web_sm')  # NER tags PERSON, GPE, ...
nlp_en = spacy.load('en_core_web_sm')  # NER tags PERSON, GPE, ...
#nlp_en = spacy.load('en_core_news_sm')  # NER tags PERSON, GPE, ...
# FIXME: change hte bleow varialbe name!!!
nlp_de = spacy.load('nb_core_news_sm') # NER tags PER, LOC, ...

# the Vocab objects are not the same
#assert nlp_en.vocab != nlp_de.vocab

# but the vectors are identical (because neither model has vectors)
#assert nlp_en.vocab.vectors.to_bytes() == nlp_de.vocab.vectors.to_bytes()

# original English output
doc1 = nlp_en(text)
print([(ent.text, ent.label_) for ent in doc1.ents])
# [('Jane', 'PERSON'), ('Boston', 'GPE'), ('Bremen', 'GPE')]

# original German output (the German model makes weird predictions for English text)
doc2 = nlp_de(text)
print([(ent.text, ent.label_) for ent in doc2.ents])
# [('Jane lives', 'PER'), ('Boston', 'LOC'), ('Jan lives', 'PER'), ('Bremen', 'LOC')]

# initialize a new NER component with the vocab from the English pipeline
help(EntityRecognizer)
ner_de = EntityRecognizer(nlp_en.vocab,  entity_types = ['ANIMAL'])
#ner_de = EntityRecognizer(nlp_en.vocab)

# reload the NER component from the German model by serializing
# without the vocab and deserializing using the new NER component
ner_de.from_bytes(nlp_de.get_pipe("ner").to_bytes(exclude=["vocab"]))

# add the German NER component to the end of the English pipeline
nlp_en.add_pipe(ner_de, name="ner_de")

# check that they have the same vocab
assert nlp_en.vocab == ner_de.vocab

# combined output (English NER runs first, German second)
doc3 = nlp_en(text)
print([(ent.text, ent.label_) for ent in doc3.ents])
# [('Jane', 'PERSON'), ('Boston', 'GPE'), ('Jan lives', 'PER'), ('Bremen', 'GPE')]


# ----------------
