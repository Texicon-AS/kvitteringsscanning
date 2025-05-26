"""
@file
@brief
@remarks
- template: https://stackoverflow.com/questions/70147866/blank-lemmatization-using-spacy
"""
import spacy
#from spacy.lang.id import Norwegian
from spacy.lang.nb import Norwegian
nlp = Norwegian()
nlp = spacy.blank('en')
#nlp.add_pipe("lemmatizer", config={"mode": "lookup"})
#nlp.add_pipe("lemmatizer")
optimizer = nlp.create_optimizer()
#nlp.initialize() # FIXME: this fails: why?

def tokenizer(text):
  return [token.lemma_.lower() for token in nlp(text) if not token.is_stop and not token.is_punct]


docs = [
  "jobber med cpp",
  "jobber med cpp og java",
  "glad i epler og pærer",
]

for text in docs:
    print(tokenizer(text))
