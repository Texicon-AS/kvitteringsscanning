"""
@file
@brief
@remarks
- template: https://spacy.io/usage/rule-based-matching
"""
# FIXME: amke use of thsi ... update our docu with this ... and oru base-example <-- what cases to add callback to?
from spacy.lang.en import English
from spacy.matcher import Matcher
from spacy.tokens import Span

nlp = English()
matcher = Matcher(nlp.vocab)

def add_event_ent(matcher, doc, i, matches):
    # Get the current match and create tuple of entity label, start and end.
    # Append entity to the doc's entity. (Don't overwrite doc.ents!)
    match_id, start, end = matches[i]
    entity = Span(doc, start, end, label="EVENT")
    doc.ents += (entity,)
    print(entity.text)

pattern = [{"ORTH": "Google"}, {"ORTH": "I"}, {"ORTH": "/"}, {"ORTH": "O"}]
matcher.add("GoogleIO", [pattern], on_match=add_event_ent)
doc = nlp("This is a text about Google I/O")
matches = matcher(doc)
