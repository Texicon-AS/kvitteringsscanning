"""
@file
@brief
@remarks
- API: https://spacy.io/usage/rule-based-matching
- challgen: the below basic Spacy-use examplies/udnelrines that basic NER-matching does not work, thus, need for grammar and/or AI-training.
- usage: a permtaution of the belwo is included into our "ClassifyProduct.py"
"""
from typing import List, Union
import spacy
from spacy import displacy
from spacy.matcher import Matcher
import pathlib
import os

#! Note: to make the below classifciaont mroe acucarte, then train consturct a new "nlp" based on a traiend data-set
#nlp = spacy.load("en_core_web_sm")
nlpProductSpecific = spacy.load("en_core_web_lg")
nlpProductSpecific.add_pipe("merge_noun_chunks")
nlp = spacy.load("en_core_web_lg")
# Merge noun phrases and entities for easier analysis
# FIXME: how does the "spacy" pipes work? what is the point (of the pipes)? how do they changE=improve the predictins? <-- a nested filter?
#nlp.add_pipe("merge_entities")
arr_patterns = [];
pattern = [
  {"LOWER": "databases"}, {"LEMMA": "be"}, {"POS": "ADV", "OP": "*"}, {"POS": "ADJ"}
]
arr_patterns.append(pattern);

# arr_matches = []  # Collect data of matched sentences to be visualized
# def __collect_sents(label, matcher, doc, i, matches):
#   #print("matcher==", matcher.vocab);
#   #help(matcher);
#   #assert(False);
#   match_id, start, end = matches[i]
#   print("... ", nlp.vocab.strings[match_id]);
#   #print("label=", matcher.label);
#   #print("label=", matcher.label);
#   span = doc[start:end]  # Matched span
#   sent = span.sent  # Sentence containing matched span
#   # Append mock entity for match in displaCy style to arr_matches
#   # get the match span by ofsetting the start and end of the span with the
#   # start and end of the sentence in the doc
#   print("\t(match)", sent.text, "; subset=", span.text);
#   #!
#   start = span.start_char - sent.start_char;
#   end   = span.end_char - sent.start_char;
#   #!
#   match_ents = [{
#     "start": start,
#     "end": end,
#     "label": label,
#   }]
#   #!
#   #! Test if text already contains a match:
#   for obj in arr_matches:
#     if(obj["text"] == sent.text): # FIXME: for the below ... why is the text concantedna muliple tiems (in the results)? <-- to symbolzie pattern-voerlaps (ie, an idneited=meanigufl feature)?
#       isExtended = False;
#       for o in obj["ents"]:
#         prev = [o["start"], o["end"]];
#         if( (start < prev[0]) or (end > prev[1])):
#           isExtended = True;
#       if(isExtended):
#         obj["ents"] += match_ents; #! ie, then extend exiintg
#       #!
#       #assert(False);
#       return;
#   arr_matches.append({"text": sent.text, "ents": match_ents})
#   #if(arr_matches_doc != None):
#   #doc = nlp.make_doc(word)   #! Note: documetnation for class="doc" is found at [https://spacy.io/api/doc]

# def __entryOf_db(matcher, doc, i, matches):
#   return __collect_sents("database", matcher, doc, i, matches)
# def __entryOf_years(matcher, doc, i, matches):
#   return __collect_sents("MATCH", matcher, doc, i, matches)

matcher.add("DatabaseIs", arr_patterns, on_match=__entryOf_db)  # add pattern
matcher.add("NumberRange", arr_patterns, on_match=__entryOf_years)  # add pattern
#productString = "Mills Peanut Butter 350g"

def printUnit(productString : str):
    print("\n--------------- productString=", productString)
    lemmatizer = nlp.get_pipe("lemmatizer")
    #productString = productString.replace("Uten Sukker", "utenSukker")
    #print("productString=", productString)
    #assert(False)
    productString = productString.replace("X-tra", "Xtra")
    #print(lemmatizer.mode)  # 'rule'
    docProductSpecific = nlpProductSpecific(productString)
    for token in docProductSpecific:
        print("token: ", token, token.dep_)
        if(token.dep_ == "ROOT"):
            productTypeSpecific = token.text #! eg, "hamburgerrygg"
    doc = nlp(productString)
    print("lemma; ", [token.lemma_ for token in doc])    #! eg, ['Mills', 'Peanut', 'Butter', '350', 'g']
    if(True):
        svg = displacy.render(doc, style='dep')
        #output_path = pathlib.Path(os.path.join("./", "sentence.svg"))
        output_path = pathlib.Path(os.path.join("./", "sentence.png"))
        output_path.open('w', encoding="utf-8").write(svg); #! [https://stackoverflow.com/questions/55723812/when-i-save-the-output-of-displacy-renderdoc-style-dep-to-a-svg-file-there]
    if(True): # FIXME: merge this and the below appraoch!
        matches = matcher(doc)
        print("matches=", matches)
    arrCompound : List[str] = [] # FIXME: figure out how using this
    arrModifierKeys : List[str] = []
    quanity : Union[str, int, float] = ""
    for token in doc:
        print("token: ", token, token.dep_)
        if(token.dep_ == "ROOT"):
            productType = token.text #! eg, "hamburgerrygg"
        if(token.dep_ == "nummod"): #! then the value does NOT feref to a count <-- FIXME: autoamte this proceudre ... adding a mapping-table for this
            # FIXME: repplace below by an enum
            unit = token.head.text

            if(quanity == ""):
                quanity = token.text
            else:
                print(f"!!\t quanity:{quanity} while valueToSet:{token.text}")
                unit = token.text
                #print(f"!!\t quanity:{quanity} while unit:{unit}")
                #assert(False)
            # print(f"quanity={quanity}") #, token.dep_)
            # print("\t\tunit: " +
            #       #print("\tunit: "...text",
            #       #token.text, token.dep_,
            #       unit,
            #       #token.head.pos_,
            #       #[child for child in token.children]
            #       )
            arrModifierKeys.append(unit) #! as this is NOT a compound
            #assert(unit not in arrModifierKeys) #! ?? cases where this will not hold?
            #assert(False) # FIXME: ...
        else:
            aCompound : bool = (token.text not in arrModifierKeys)
            #print(f"--- token({token}) w/text={token.text}", token.dep_, aCompound, arrModifierKeys)
            #print("; children:")
            if(token.text not in arrCompound):
                arrCompound.append(token.text)
            for child in token.children:
                #print("\t....", child.dep_, child.text)
                pass
            #if(token.dep_ in ["ROOT"]):
            #if(aCompound):
            #    arrCompound.append(token.text)
            #print("token.children: ", token.text, token.dep_, token.head.text, token.head.pos_,
            #[child for child in token.children])
        for child in token.children:
            if(child.text in arrCompound):
                continue #! as it was already added
            if child.dep_ in ["compound", "ROOT"]:
                #print(f"{child} is compound to {tok}")
                arrCompound.append(child.text)
            #else:
            #; # print("\t- (not-a-compound)\t ", child)
    arrCompoundFiltered : List[str] = []
    for compound in arrCompound:
        if(compound in arrModifierKeys):
            continue
        arrCompoundFiltered.append(compound)
    print("arrCompound=", arrCompoundFiltered) # FIXME: how can this list be used for searching?
    print("productType=", productType)
    print("productTypeSpecific=", productTypeSpecific)
    print("quanity=", quanity)
    print("unit=", unit)



if __name__ == "__main__":
    arrProdEntries : List[str] = [
        "Mills Peanut Butter 350g",
        # FIXME: add below
        # FIXME: how can we extraact "ost" from "Fløtemysost"?
        "Fløtemysost Lettere skivet 130g", #;130 g",
        "Fløtemysost Lettere skivet 130g Tine", #;130 g",
        "Vita Hjertego Lettmargarin 370g",
        "Oreo Sjokoladetrukket 246 g",
        "X-tra Røkt Kjøttpølse 1,2kg", # FIXME: merge "x-tra" into one word <-- a manual step? better appraoch?
        "Coop Hamburgerrygg 100g", # FIXME: why is unit "hamburgerrygg"?
        "Toro Lofoten Fiskesuppe 70g",
        "Leverpostei 160g Metervare",
    ]
    _arrProdEntries : List[str] = [
        # FIXME: get below to work
        #"Majones Ekte 160g Tube Mills", # FIXME: productType= Ekte and productTypeSpecific= Majones Ekte
        "Explo Mango Passion Sukkerfri 0,5l boks Mack",
        # "Coop Grøtris 1kg",
        # "Kulinaris Iskrem Salt Karamel&Cookies 0,5l;500 ml",
        # "Jordbærgele 1l Piano",
        # "Idyll Sjokoladeis Plantebasert 500ml Hennig-Olsen",
        # "Daim Iskake 0,9l Hennig-Olsen",
        # "Sjokoladepudding 1l Piano",
        # "Sørlandsis Krokan 2l Hennig-Olsen",
        # "Knorr Chicken Curry 321g",
        # "Royal Is Sjokolade 0.9l Diplom-Is",
        # "Vaniljeis 3l First Price",
        # "Surdeig baguette",
        # "Sausage",
        # "Laksefilet Naturell",
        # "Cut chicken filet",
        # "Big 100 Cookie Dough",
        # "Store Tortillalefser",
        # "Chickpeas in brine",
    ]
    _arrProdEntries : List[str] = [
        # FIXME: get below to work!
        "Freia Sitrongele Uten Sukker 14g", # FIXME: how to merge "uten sukker" in one word? <-- when needed?
    ]
    for productString in arrProdEntries:
        #print(f"predicted({productString}): ", classify.predict(productString))
        #print(f"predicted({productString}): ", printUnit(productString))
         printUnit(productString)
assert(False) # FIXME: when the aobve works then update our "tut-extractCardinalAndMetric.py"
if(False): #! Visualizing dependencies []
    #doc = nlp("Autonomous cars shift insurance liability toward manufacturers")
    lemmatizer = nlp.get_pipe("lemmatizer")
    print(lemmatizer.mode)  # 'rule'

    doc = nlp(productString)
    print("lemma; ", [token.lemma_ for token in doc])    #! eg, ['Mills', 'Peanut', 'Butter', '350', 'g']
    #doc = nlp(productString)
    svg = displacy.render(doc, style='dep')
    #output_path = pathlib.Path(os.path.join("./", "sentence.svg"))
    output_path = pathlib.Path(os.path.join("./", "sentence.png"))
    output_path.open('w', encoding="utf-8").write(svg); #! [https://stackoverflow.com/questions/55723812/when-i-save-the-output-of-displacy-renderdoc-style-dep-to-a-svg-file-there]

    for token in doc:
        if(token.dep_ == "nummod"): #! then the value does NOT feref to a count <-- FIXME: autoamte this proceudre ... adding a mapping-table for this
            # FIXME: repplace below by an enum
            print(f"quanity={token.text}") #, token.dep_)
            print("\t\tunit: " +
                  #print("\tunit: "...text",
                  #token.text, token.dep_,
                  token.head.text,
                  #token.head.pos_,
                  #[child for child in token.children]
                  )
        else:
            print(f"token({token}) w/text={token.text}", token.dep_)
            print("token.children: ", token.text, token.dep_, token.head.text, token.head.pos_,
                  [child for child in token.children])
assert(False) # FIXME: update our "tut-productGrammar.py" based on the above
if(True): #! Named Entity Recognition []
  # FIXME: merge below and above
  nlp = spacy.load("en_core_web_lg")
  doc = nlp("one bottle of beer")
  #doc = nlp("Apple is looking at buying U.K. startup for $1 billion")
  print("Entities:");
  for index, ent in enumerate(doc.ents):
    print(f"{index}\t {ent.text}, {ent.start_char}, {ent.end_char}, {ent.label_}")
if(True): #! Accessing entity annotations and labels []
  # FIXME: merge below and above
  nlp = spacy.load("en_core_web_lg")
  #nlp = spacy.load("en_core_web_sm")
  #doc = nlp("San Francisco considers banning sidewalk delivery robots")
  doc = nlp("one bottle of beer")

  # document level
  ents = [(e.text, e.start_char, e.end_char, e.label_) for e in doc.ents]
  print("ents(text, startChar, endChar, label)=", ents)

  # token level
  ent_san = [doc[0].text, doc[0].ent_iob_, doc[0].ent_type_]
  ent_francisco = [doc[1].text, doc[1].ent_iob_, doc[1].ent_type_]
  print(ent_san)  # ['San', 'B', 'GPE']
  print(ent_francisco)  # ['Francisco', 'I', 'GPE']
if(True): #! Word vectors and semantic similarity []
  # FIXME: merge below and above
  nlp = spacy.load("en_core_web_sm")
  #nlp = spacy.load("en_core_web_md")
  tokens = nlp("one bottle of beer")
  #tokens = nlp("dog doga cat banana afskfsd")
  print("\n\n# Word vectors and semantic similarity:")
  for token in tokens:
    # fIXME: what is the meanign fo the below "token.vector_norm"?
    print(token.text, token.has_vector, token.vector_norm, token.is_oov)

#nlp = spacy.blank("en")


patterns = [
    {"label": "vegetable", "pattern": "red apple"},
    {"label": "vegetable", "pattern": "red apples"},
    {"label": "building", "pattern": "large white building"},
    {"label": "SOMETHING", "pattern": "lamp"},
    {"label": "SOMETHING", "pattern": "light"},
    {"label": "SOMETHING", "pattern": "fan"}
]

#ruler = nlp.add_pipe("entity_ruler")
#ruler.add_patterns(patterns)

for text in [
        "I saw a red apple under a lamp in the large white building",
        "I saw many red apples under a lamp in the large white building",
        "five applies",
        "5 applies",
        "one bottle of beer",
]:
    print("# Input: " + text)
    for ent in nlp(text).ents:
        print(ent.label_, ent, sep="\t")

if __name__ == "__main__":
    assert(False) # FIXME: complete "tut-readFile.py"
    assert(False) # FIXME: rewrite the above ... add stuff into this
    assert(False) # FIXME: update ""
