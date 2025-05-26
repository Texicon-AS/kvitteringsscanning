"""
@brief examplfieis how updating the model
@remarks
- src: https://github.com/explosion/spaCy/discussions/6316
"""
import random
import spacy
from spacy.training import Example
#nlp = spacy.load("en_core_web_sm")
from spacy.lang.en import English
nlp = English() #! https://spacy.io/api/language


# FIXME: update our ?? with this training-exmaple
TRAIN_DATA = [
    ("Who is Shaka Khan?", {"entities": [(7, 17, "PERSON")]}),
    ("I like London.", {"entities": [(7, 13, "LOC")]}),
]
nlp.initialize()
for i in range(20):
    random.shuffle(TRAIN_DATA)
    sizes = spacy.util.compounding(1, 16, 1.001) #! "This utility function will yield an infinite series of compounding values. Whenever the generator is called, a value is produced by multiplying the previous value by that compound rate" [https://www.tutorialspoint.com/spacy/spacy_util_compounding.htm] # <-- FIXME: how to correctly configure this?
    for batch in spacy.util.minibatch(TRAIN_DATA, size=sizes):
        arrSamples = []
        for text, annots in batch:
            arrSamples.append(Example.from_dict(nlp.make_doc(text), annots))
        nlp.update(arrSamples)
# FIXME: in our training-system use this approach as the first step, then use "tut-trainNer.py" as a more advancd strategy <-- hopw do they relate? <-- pre: get "tut-onlineTrainer.py" to work
