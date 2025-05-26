import spacy
from spacy.matcher import DependencyMatcher

nlp = spacy.load("en_core_web_sm")

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
# pattern = [
#     {
#         "RIGHT_ID": "anchor_founded",
#         "RIGHT_ATTRS": {"ORTH": "founded"}
#     },
#     {
#         "LEFT_ID": "anchor_founded",
#         "REL_OP": ">",
#         "RIGHT_ID": "founded_subject",
#         "RIGHT_ATTRS": {"DEP": "nsubj"},
#     },
#     {
#         "LEFT_ID": "anchor_founded",
#         "REL_OP": ">",
#         "RIGHT_ID": "founded_object",
#         "RIGHT_ATTRS": {"DEP": "dobj"},
#     },
#     {
#         "LEFT_ID": "founded_object",
#         "REL_OP": ">",
#         "RIGHT_ID": "founded_object_modifier",
#         "RIGHT_ATTRS": {"DEP": {"IN": ["amod", "compound"]}},
#     }
# ]

matcher = DependencyMatcher(nlp.vocab)
matcher.add("FOUNDED", [pattern])
doc = nlp("Mills Peanut Butter 350g")
#doc = nlp("Lee, an experienced CEO, has founded two AI startups.")
matches = matcher(doc)

print(matches) # [(4851363122962674176, [6, 0, 10, 9])]
assert(len(matches))
# Each token_id corresponds to one pattern dict
match_id, token_ids = matches[0]
for i in range(len(token_ids)):
    print(pattern[i]["RIGHT_ID"] + ":", doc[token_ids[i]].text)
