"""
@file
@brief uses regular expressionss to detect patterns in the text
@remarks a permtaution of the belwo is included into our "ClassifyProduct.py"
"""
import spacy
from spacy.matcher import Matcher
nlp = spacy.load("en_core_web_sm")

texts = [
    #"the surface is 31 l",
    #"Hansa 31 l",
    #"Hansa 31l",
    "Xtra mack 0,5l boks",
    #"Xtra mack 0,5 l boks",
    "Hansa Øl 1 l",
    "Hansa Øl 1l",
    #"the surface is sq 31", "the surface is square meters 31",
    #"the surface is 31 square meters", "the surface is about 31 square meters", "the surface is 31 kilograms"
]
pattern1 = [
    #{"IS_STOP": True},
    #{"LOWER": "surface"},
    #{"LEMMA": "be", "OP": "?"},
    #{"TEXT" : {"REGEX": "^(?i:sq(?:uare)?|m(?:et(?:er|re)s?)?)$"}, "OP": "+"},
    {"LIKE_NUM": True}, #! ie, the number before the unit, eg, "1" in substring="1 l"
    {"TEXT" : {"REGEX": "^(?i:l)$"}, "OP": "+"}, # TODO: add the other units to this "l", eg, "kg", "g", ...
    #{"TEXT" : {"REGEX": "^(?i:l)$"}, "OP": "+"},
]
pattern2 = [
    {"TEXT" : {"REGEX": r"^(\d+(,\d+)?)(?i:l)$"}, "OP": "+"}, # TODO: add the other units to this "l", eg, "kg", "g", ...
]
# pattern2 = [
#     {"IS_STOP": True},
#     {"LOWER": "surface"},
#     {"LEMMA": "be", "OP": "?"},
#     {"IS_ALPHA": True, "OP": "?"},
#     {"LIKE_NUM": True},
#     #{"TEXT" : {"REGEX": "^(?i:sq(?:uare)?|m(?:et(?:er|re)s?)?)$"}, "OP": "+"}
#     {"TEXT" : {"REGEX": "^(?i:l)$"}, "OP": "+"}
# ]

matcher = Matcher(nlp.vocab, validate=True)
matcher.add("productUnit",
            [
                pattern1,
                pattern2
            ])
#matcher.add("Surface", pattern1)
#matcher.add("Surface", pattern2)

for text in texts:
  doc = nlp(text)
  matches = matcher(doc)
  for match_id, start, end in matches:
    string_id = nlp.vocab.strings[match_id]  # Get string representation
    span = doc[start:end]  # The matched span
    print("span=", span)
    #print(match_id, string_id, start, end, span.text)
