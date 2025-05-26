"""
@file
@brief
@remarks
"""
from typing import List, Tuple, ClassVar
#import traceback
#import pathlib
#import os
#! External libratires:
from dataclasses import dataclass, field
import spacy
from spacy.matcher import Matcher
from spacy.matcher import PhraseMatcher
from spacy.language import Language #! needd when using "mypy"
from typeguard import typechecked
#from spacy import displacy

#! Local files:
#from foodNer.PredictedProduct import PredictedProduct
#from foodNer.PredictedProduct import PredictedProduct
from foodNer.ClassifyNonStandardUnits import ClassifyQuantityAndUnit # ClassifyNonStandardUnits

@typechecked
@dataclass
class ShapeUnitClassification(ClassifyQuantityAndUnit):
    """
    @brief
    @remarks
    """
    NerLabelProductQuantAndUnit : ClassVar[str] = "productQuantAndUnit-merged"
    nlp : Language =  field(default_factory = lambda : spacy.load("en_core_web_lg"))
    #nlp : spacy.lang = spacy.load("en_core_web_lg")
    def __post_init__(self) -> None:
        #print("nlp.type=", type(self.nlp), self.nlp) # FIXME: remove ... udpate the aobove data-type
        #patterns = [nlp(text) for text in unitVocabTerms]
        # Only run nlp.make_doc to speed things up
        assert(self.unitVocabTerms) #! ie, at least one item
        patterns = [self.nlp.make_doc(text) for text in self.unitVocabTerms]
        #matcher.add("TerminologyList", patterns)
        # Add the patterns to the matcher
        #matcher.add("productUnit", patterns)
        self.__phraseMatcher = PhraseMatcher(self.nlp.vocab, attr="SHAPE") # TODO our other exmaples ... mkae use of this "SHAPE"
        self.__phraseMatcher.add("productUnit", patterns)
        #Define a pattern to match "download" followed by a number and a file extension
        patternGrammar : List[dict] = [ # type: ignore[type-arg]
            #{"LOWER": "download"},
            {"LIKE_NUM": True},
            {"LOWER": {"IN": self.unitVocabTerms}}
        ]
        patternGrammerCaseUpper : List[dict] = [ # type: ignore[type-arg] # TODO: merge this and the above "patternGrammar"
            {"LIKE_NUM": True},
            {"TEXT": {"IN": self.unitVocabTerms}}
        ]
        #self.__matcherGrammar = Matcher(nlp.vocab, validate=True)
        self.__matcher = Matcher(self.nlp.vocab, validate=True)
        self.__matcher.add(self.NerLabelProductQuantAndUnit, [patternGrammar])
        self.__matcher.add(self.NerLabelProductQuantAndUnit, [patternGrammerCaseUpper])

        # --------------------------
    def predict(self, productString : str) -> Tuple[str, str]:
        """
        @brief
        @return
        """
        doc = self.nlp(productString)
        arrMatches = [
            # TODO: re-order/adjust below loop when we have a better feeling fo what works!
            self.__phraseMatcher(doc),
            self.__matcher(doc),
        ]
        productAndUnit = ""
        unitTerm = ""
        for matches in arrMatches:
            #print(f".... unitTerm:{unitTerm}, productAndUnit:{productAndUnit}, input:", productString)
            if(productAndUnit != ""): #! as we assume the productAndUnit pattern is before the unitTerm-pattern
                assert(unitTerm != "")
                continue
            for match_id, start, end in matches:
                patternName = self.nlp.vocab.strings[match_id]  # Get string representation
                span = doc[start:end]  # The matched span
                #print(f"span[{matchCat}, {patternName}]=", span)
                if(patternName == self.NerLabelProductQuantAndUnit):
                    productAndUnit = span.text
                else:
                    if(span.text not in self.unitVocabTerms):
                        continue #! eg, to avoid matches for strings such as "Chickpeas in brine'", where the attr=SHAPE makes a match on the 'in' word
                    unitTerm = span.text
                    print(f"unitTerm='{unitTerm}' given productString:{productString}' and patternName:{patternName}")
                    assert(unitTerm in self.unitVocabTerms)
                #print(match_id, string_id, start, end, span.text)

        #! Extract the quantitiy-valyue and the unit/metric
        if(not productAndUnit):
            return ("", "") #! as nothing was idneifeid
        (quanityValue, unit) = self.normalizeProduct(productString, productAndUnit, unitTerm)
        return (quanityValue, unit)

if __name__ == "__main__":
    """
    @brief tests the ShapeUnitClassification class
    @remarks
    - overall: quaintify the error of this class, eg, make explit which cases are supported, and those which other classes needs to handle
    """
    classify = ShapeUnitClassification()
    arrProdEntries : List[str] = [
        "Gilde Ovnsbakt Leverpostei med Bacon 180g", #! ie, which the "ShapeUnitClassification.py" is repsonbie for solving
        "Mills Peanut Butter 350g",
        "Hansa Øl 1 l",
        "Mills Peanut Butter 350g",
        # TODO/ingredient-analysis: how can we extraact "ost" from term="Fløtemysost" (eg, extracted from "Fløtemysost Lettere skivet 130g Tine")?
        "Fløtemysost Lettere skivet 130g Tine",
        "Vita Hjertego Lettmargarin 370g",
        "Coop Hamburgerrygg 100g;",
        "Oreo Sjokoladetrukket 246 g",
        "Freia Sitrongele Uten Sukker 14g", # TPDP: challnging case: how to resolve/idneitfy? <-- use algorithmn-tranining for ths partciular case? <-- a better approach? <-- and, how to merge "uten sukker" in one word? <-- when needed?
        "Toro Lofoten Fiskesuppe 70g;",
        "X-tra Røkt Kjøttpølse 1,2kg;"
        "Coop Grøtris 1kg",
        "Knorr Chicken Curry 321g",
        "Majones Ekte 160g Tube Mills", # TODO: productType= Ekte and productTypeSpecific= Majones Ekte
    ]
    for productString in arrProdEntries:
        # TODO: add tests to validate that the quanityValue and unit has the correct values
        (quanityValue, unit) = classify.predict(productString)
        print(f"[ClassifyNonStandardUnits.py]\t '{productString}' => unit:'{unit}' and quanityValue:'{quanityValue}'")
        assert(quanityValue != "")
        assert(unit != "")
        #print(f"predicted({productString}): ", classify.predict(productString))
    #! ------------------------------------
    #! Validate that our system does not 'break'æ when encoruteirng unsupported cases:
    arrProdEntries : List[str] = [ # type: ignore[no-redef]
        "Hansa Øl 1l",
        "Explo Mango Passion Sukkerfri 0,5l boks Mack",
        "Xtra mack 0,5l boks",
        "Kulinaris Iskrem Salt Karamel&Cookies 0,5l",
        "Jordbærgele 1l Piano",
        "Idyll Sjokoladeis Plantebasert 500ml Hennig-Olsen",
        "Daim Iskake 0,9l Hennig-Olsen",
        # ---
        "Sjokoladepudding 1l Piano",
        "Sørlandsis Krokan 2l Hennig-Olsen",
        "Royal Is Sjokolade 0.9l Diplom-Is",
        "Vaniljeis 3l First Price",
        "Chickpeas in brine",
    ]
    for productString in arrProdEntries:
        (quanityValue, unit) = classify.predict(productString)
        print(f"[ClassifyNonStandardUnits.py]\t '{productString}' => unit:'{unit}' and quanityValue:'{quanityValue}'")
        assert(quanityValue == "")
        assert(unit == "")
        #print(f"predicted({productString}): ", classify.predict(productString))
    #! ------------------------------------
    #! Validate the handling of cases where there is zero ecolit quanity--unit information provided:
    arrProdEntries : List[str] = [ # type: ignore[no-redef]
        "Store Tortillalefser",
        "Big 100 Cookie Dough",
        "Cut chicken filet",
        "Laksefilet Naturell",
        "Sausage",
        "Surdeig baguette",
    ]
    for productString in arrProdEntries:
        (quanityValue, unit) = classify.predict(productString)
        print(f"[ClassifyNonStandardUnits.py]\t '{productString}' => unit:'{unit}' and quanityValue:'{quanityValue}'")
        assert(quanityValue == "")
        assert(unit == "")
    # ----
