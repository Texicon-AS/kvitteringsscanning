#! Src: https://spacy.io/usage/linguistic-features#lemmatizer-lookup
from spacy.language import Language
import spacy

text = "this is a sentence...hello...and another sentence."

nlp = spacy.load("en_core_web_sm")
doc = nlp(text)
print("Before:", [sent.text for sent in doc.sents])

@Language.component("set_custom_boundaries")
def set_custom_boundaries(doc):
    for token in doc[:-1]:
        if token.text == "...":
            doc[token.i + 1].is_sent_start = True
    return doc

nlp.add_pipe("set_custom_boundaries", before="parser")
doc = nlp(text)
print("After:", [sent.text for sent in doc.sents])

# FIXME: update our ?? (in our "src/training")  with above ... how cna the above straegy improve our=the overall pemrtfoance? <--- can we use the aobve for diffenrt ngram-cases?
