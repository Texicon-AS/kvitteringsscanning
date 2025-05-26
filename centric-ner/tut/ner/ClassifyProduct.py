
from typing import List
import pathlib
import os
#! External libratires:
import spacy
from spacy.matcher import Matcher
from spacy.matcher import PhraseMatcher
from spacy import displacy
from dataclasses import dataclass

assert(False) # FIXME: pre: complete testing of "tut-enumerateMatches.py" and then itnegrate

@dataclass
class PredictedProduct:
    product : str #! ie, the product we idneitfy
    value : float #! ie, the predicted value, intepreted usign the "unit"
    unit : str # FIXME: replace this with an enum?


@dataclass
class Classify:
    nlp = spacy.load("en_core_web_lg")
    def __post_init__(self):
        pattern1 = [
            {"LIKE_NUM": True}, #! ie, the number before the unit, eg, "1" in substring="1 l"
            {"TEXT" : {"REGEX": "^(?i:l)$"}, "OP": "+"}, # FIXME: add the other units to this "l", eg, "kg", "g", ...
        ]
        pattern2 = [
            {"TEXT" : {"REGEX": r"^(\d+(,\d+)?)(?i:l)$"}, "OP": "+"}, # FIXME: add the other units to this "l", eg, "kg", "g", ...
        ]
        self.__matcher = Matcher(self.nlp.vocab, validate=True)
        self.__matcher.add("productUnit",
                    [
                        # FIXME: incldue below!
                        pattern1,
                        pattern2
                    ])
        # --------------------------
        unitVocabTerms = [
            "g"
            "kg",
            "l",
            #"boks", "box"
        ]
        #patterns = [nlp(text) for text in unitVocabTerms]
        # Only run nlp.make_doc to speed things up
        patterns = [self.nlp.make_doc(text) for text in unitVocabTerms]
        #matcher.add("TerminologyList", patterns)
        # Add the patterns to the matcher
        #matcher.add("productUnit", patterns)
        self.__matcherPhases = PhraseMatcher(self.nlp.vocab, attr="SHAPE") # FIXME: update our other exmaples ... mkae use of this "SHAPE"
        self.__matcherPhases.add("productUnit", patterns)
        #Define a pattern to match "download" followed by a number and a file extension
        patternGrammar = [
            #{"LOWER": "download"},
            {"LIKE_NUM": True},
            {"LOWER": {"IN": unitVocabTerms}}
            #{"CASEINSENSITIVE": {"IN": unitVocabTerms}}
            #{"LOWER": {"IN": ["kb", "mb", "gb"]}}
        ]
        #self.__matcherGrammar = Matcher(nlp.vocab, validate=True)
        self.__matcher.add("productUnitPattern", [patternGrammar])

        # --------------------------
    def predict(self, productString : str): # -> PredictedProduct:
        """
        @brief
        """
        doc = self.nlp(productString)
        arrMatches = [
            # FIXME: adjust below loop when we have a better feeling fo what works!
            self.__matcher(doc),
            self.__matcherPhases(doc),
        ]
        for matchCat, matches in enumerate(arrMatches):
            for match_id, start, end in matches:
                string_id = self.nlp.vocab.strings[match_id]  # Get string representation
                span = doc[start:end]  # The matched span
                print(f"span[{matchCat}]=", span)
                unit = span # FIXME: handle cases where "self.__matcherPhases" mergs the units 0 the qunaity <-- add a fallsback for this?
                #print(match_id, string_id, start, end, span.text)
        #assert(False) # FIXME: update the below
        return unit # FIXME: remove, icnlcue bleow instead!
        #return PredictedProduct(product, value, unit)

if __name__ == "__main__":
    assert(False) # FIXME: complete "tut-enumerateMatches.py"
    assert(False) # FIXME: rewrite the above ... add stuff into this
    assert(False) # FIXME: update ""
    classify = Classify()
    arrProdEntries : List[str] = [
        "Mills Peanut Butter 350g",
        "Hansa Øl 1 l",
        "Hansa Øl 1l",
        "Xtra mack 0,5l boks",
        "Mills Peanut Butter 350g",
        # FIXME: how can we extraact "ost" from "Fløtemysost"?
        "Fløtemysost Lettere skivet 130g Tine",
        "Vita Hjertego Lettmargarin 370g;370 g",
        "Coop Hamburgerrygg 100g;",
        "Oreo Sjokoladetrukket 246 g",
        "Freia Sitrongele Uten Sukker 14g", # FIXME: use algorithmn-tranining for ths partciular case?
        "Toro Lofoten Fiskesuppe 70g;",
        "X-tra Røkt Kjøttpølse 1,2kg;"
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
        print(f"predicted({productString}): ", classify.predict(productString))

    assert(False) # FIXME: when completed print out the cases we failed to handle? what is the erpcentage of these? <--- to resovle these, cosntruct dummy bdata and then train
    assert(False) # FIXME: udpate this ... read all the data from "/sample_data/openfoodfacts_export.csv"... make use of these as extneive testing ...
