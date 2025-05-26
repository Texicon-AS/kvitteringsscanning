"""
@file
@brief exemplfies the use of the matching tool
@remarks
- template: https://medium.com/bi3-technologies/advance-text-matching-with-spacy-and-python-40b558c51413
"""
import spacy
from spacy.matcher import PhraseMatcher
from spacy.matcher import Matcher
nlp = spacy.load("en_core_web_lg")
#matcher = PhraseMatcher(nlp.vocab)
matcher = PhraseMatcher(nlp.vocab, attr="SHAPE") # FIXME: update our other exmaples ... mkae use of this "SHAPE"
# Define the phrases to match
#unitVocabTerms = ["Turkey", "U.S"]
unitVocabTerms = [
    "g"
    "p", # FIXME: remove
    "kg", "l",
    #"boks", "box"
]
#patterns = [nlp(text) for text in unitVocabTerms]
# Only run nlp.make_doc to speed things up
patterns = [nlp.make_doc(text) for text in unitVocabTerms]
#matcher.add("TerminologyList", patterns)
# Add the patterns to the matcher
#matcher.add("productUnit", patterns)
matcher.add("productUnit", patterns)
#Define a pattern to match "download" followed by a number and a file extension
patternGrammar = [
    #{"LOWER": "download"},
    {"LIKE_NUM": True},
    {"LOWER": {"IN": unitVocabTerms}}
    #{"CASEINSENSITIVE": {"IN": unitVocabTerms}}
    #{"LOWER": {"IN": ["kb", "mb", "gb"]}}
]
matcherGrammar = Matcher(nlp.vocab, validate=True)
matcherGrammar.add("productUnitPattern", [patternGrammar])

def debugMatches(doc):
    """
    @brief
    """
    # FIXME: why does the below only matches for "Kjøttpølse"?
    print("The matches for input: ", doc)
    matches = matcher(doc, as_spans=True)
    for span in matches:
        #print("span=", span)
        print(span.text, span.label_)
    matchesG = matcherGrammar(doc, as_spans=True)
    for span in matchesG:
        print(span.text, span.label_)
    print("-----")


## Apply the matcher to a text
#text = "By 2020 the telecom company Orange, will relocate from Turkey to U.S"
for text in [
        #"Explo Mango Passion Sukkerfri 0,5l boks Mack",
        "Xtra mack 0,5l box",
        "Xtra mack 0,5g boks",
        "Xtra mack 0,5p boks",
        "Xtra mack 0,5g boks",
        #"Hansa Øl 246g",
        #"Hansa Øl 246g",
        # FIXME: include below!
        "Oreo Sjokoladetrukket 246 g",
        "X-tra Røkt Kjøttpølse 1,2kg"
]:
    doc = nlp(text)
    debugMatches(doc)
    # Find matches
    matches = matcher(doc)
    for match_id, start, end in matches:
        span = doc[start:end]
        #print("doc: " + doc.text)
        print(f"-\t'{doc.text}' Matched phrase: {span.text}")
        print(f"Matched sequence: {doc[start:end]}")
    matches = matcherGrammar(doc)
    for match_id, start, end in matches:
        span = doc[start:end]
        #print("doc: " + doc.text)
        print(f"-\t'{doc.text}' Matched phrase: {span.text}")
        print(f"Matched sequence(grammar): {doc[start:end]}")
    #Matched phrase: Turkey
    #Matched phrase: U.S

# FIXME: update oru "tut-enumerateMatches.py" when the above works!
