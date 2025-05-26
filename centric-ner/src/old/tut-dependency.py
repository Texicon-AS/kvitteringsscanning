"""
@file
@brief
@remarks src: https://spacy.io/usage/rule-based-matching
"""

import spacy
from spacy.matcher import DependencyMatcher

nlp = spacy.load("en_core_web_sm")
matcher = DependencyMatcher(nlp.vocab)

pattern = [
    {
        "RIGHT_ID": "anchor_founded",
        "RIGHT_ATTRS": {"ORTH": "founded"}
    },
    {
        "LEFT_ID": "anchor_founded",
        "REL_OP": ">",
        "RIGHT_ID": "founded_subject",
        "RIGHT_ATTRS": {"DEP": "nsubj"},
    },
    {
        "LEFT_ID": "anchor_founded",
        "REL_OP": ">",
        "RIGHT_ID": "founded_object",
        "RIGHT_ATTRS": {"DEP": "dobj"},
    },
    {
        "LEFT_ID": "founded_object",
        "REL_OP": ">",
        "RIGHT_ID": "founded_object_modifier",
        "RIGHT_ATTRS": {"DEP": {"IN": ["amod", "compound"]}},
    }
]

matcher.add("FOUNDED", [pattern])
for text in [
        # FIXME: idneitfy the grammar used when writing kvittering ... then use the below as a template
        "Lee, an experienced CEO, has founded two AI startups.",
        "Lee, an experienced CEO, has founded two AI startups.",
        #"I saw a red apple under a lamp in the large white building",
        #"I saw many red apples under a lamp in the large white building",
]:
    doc = nlp(text)
    print([(w.text, w.pos_) for w in doc]) #! which displays the grammer, thuse, uself when modelling
    matches = matcher(doc)

    print("matches : ", matches) # [(4851363122962674176, [6, 0, 10, 9])]
    # Each token_id corresponds to one pattern dict
    match_id, token_ids = matches[0]
    for i in range(len(token_ids)):
        #print(pattern[i]["LEFT_ID"]) #  + ":", doc[token_ids[i]].text)
        #print(pattern[i]["RIGHT_ATTRS"]) #  + ":", doc[token_ids[i]].text)
        print(pattern[i]["RIGHT_ID"] + ":", doc[token_ids[i]].text)
