"""!
@file
@brief
@remarks
- demosntraes a case where underitting is the result <-- FIXME: still a rpbolem if a 'non-blank' model is used?
- template: [https://stackoverflow.com/questions/62272190/spacy-blank-ner-model-underfitting-even-when-trained-on-a-large-dataset]
"""
from __future__ import annotations #! used for "forward decleartions";
import random
import traceback
from typing import ClassVar
from typing import List #, Dict
from typing import Tuple
from dataclasses import dataclass, field
import spacy
from spacy.training import Example # FIXME: write concrete exampels covering this
from spacy.matcher import PhraseMatcher
from typeguard import typechecked

#nlp = spacy.load("en")
#nlp = spacy.load("en_core_web_sm")


#! Local files:
#from foodNer.PredictedProduct import PredictedProduct
#from stopWords.StopWordRemoval import StopWordRemoval
#from loadData.LoadData import LoadData
#from foodNer.PredictedProduct import PredictedProduct
#from foodNer.ClassifyNonStandardUnits import ClassifyNonStandardUnits
#from foodNer.ShapeUnitClassification import ShapeUnitClassification
from loadData.Matvaretabellen import MatrixOfFoods, FoodEntry
from loadData.LoadData import MatrixOfProductAndQuantity
from loadData.LoadData import ProductAndQuantity
from foodNer.ClassifyEntry import ClassifyEntryMultiLang #, MatchedEntry
from foodNer.ClassifyEntry import main as ClassifyEntryMain
from foodNer.ClassifyEntry import StoreResults
from foodNer.MatchedEntry import MatchedEntry, MatchedEntryArr, MatchedLabel

# pylint: disable=unused-argument
# mypy:  disable-error-code=empty-body
def f(var: 'PatternsToFind') -> int:  #! ie, a forward decleartion
    ...


@typechecked
@dataclass
class PatternsToFind:
  """
  @brief
  @remarks
  """
  _arrResultTrainData : List[tuple] = field(init = False, default_factory = lambda : []) # type: ignore[type-arg]
  _arrTextsWeFailedToClassify : List[str] = field(init = False, default_factory = lambda : [])
  _grammarSpec : ClassifyEntryMultiLang = field(init = False, default_factory = lambda : ClassifyEntryMultiLang())
  def __post_init__(self) -> None:
    foods = MatrixOfFoods()
    assert(len(foods.rows))
    for entry in foods.rows:
        print(entry)
        #print("data=", objData.rows)
        #print("data=", entry.productString
    if(False): # FIXME: include a permatuion fot he below ... using the "Matvaretabellen" data
        assert(False) # FIXME: when needed re-include the belwo after we rewrite it
        # users_pattern = [nlp(text) for text in ("user", "human", "person", "people", "end user")]
        # self.matcher = PhraseMatcher(nlp.vocab)
        # self.matcher.add("USER", None, *users_pattern)
        # FIXME: add mulitple ... usnig the abov epattern
        # ...
        # ...        )
        assert(False) # FIXME: then re-include the code in our "getMatches(..)"
  def getMatches(self, text : str) -> MatchedEntryArr:
    """
    @brief
    @return the set of matches
    """
    try:
      matchedArr : MatchedEntryArr = self._grammarSpec.getMatches(text)
    except (ValueError, AssertionError) as e:
      print(f"!!\t[PatternsToFind.py]\t Unable to idneitfy any quanityt--metric relationships for input({text}). Thus, givne: ", e)
      self._arrTextsWeFailedToClassify.append(text)
      matchedArr = MatchedEntryArr(text) #! ie, an empty object


    if(False): # FIXME: re-include this ...
      #! After adding all the different patterns to the matcher object, the matcher object is ready for you to make predictions:
        assert(False) # FIXME: when needed re-include the belwo after we rewrite it
        # doc = self.nlp(text) # FIXME: add this <-- use the "ClassifyEntryMultiLang"??
        # matches = self.matcher(doc)
        # for match_id, start, end in matches:
        #   label = nlp.vocab.strings[match_id]
        #   span = doc[start:end]
        #   print(f"label:{label}, start:{start}, end:{end}, text:{span.text}")
        #   matchedEntry : MatchedEntry = MatchedEntry(label, start, end)
        #   matches.append(matchedEntry)
      #!
      #!
    return matchedArr

  def addTrainingData(self, arrText : List[str]) -> None:
    """
    @brief update our internla set with the provided trainign-data
    @remarks the input-data is classifed using our internla grammar, thus, a need for having a mapping between these (for the trainign to consturct correct=meniagnful data)
    """
    for text in arrText:
      matchedArr : MatchedEntryArr = self.getMatches(text)
      if(not matchedArr):
        continue #! as zero matched
      arrEnts : List[tuple] = [] # type: ignore[type-arg]
      #print(".... matchedArr.entries=", matchedArr.entries)
      for entry in matchedArr.entries:
        arrEnts.append((entry.posStart, entry.posEnd, entry.label.name),)

      objResult = (text, {"entities" : arrEnts},)
      self._arrResultTrainData.append(objResult)

  def getTrainData(self) -> List[tuple]:  # type: ignore[type-arg]
    """
    @return the training-data constructed from our `addTrainingData(..)`
    """
    return self._arrResultTrainData
  def getTextsWeFailedToClassify(self) -> List[str]:  # type: ignore[type-arg]
    """
    @return the input-texts we failed to classify
    """
    return self._arrTextsWeFailedToClassify

  @classmethod
  def init(cls) -> PatternsToFind:
    """
    @return an object holding the training data
    """
    patterns = PatternsToFind()
    # FIXME: adjust the below ... instead, load the the filtered subset holding classifciaotns which are correct <-- does our system auto-idneitfy these cases (ie, not neccessary?)? <-- correct for (quanity, unit) cases. However, when we start applying this to correctly inify the ingredients-names, we get a challenge ... then a need for loading a subset of manually curated entites
    objData = MatrixOfProductAndQuantity() #! holds data from "openfoodfacts" (subset)
    arrProductAndQuantity : List[ProductAndQuantity] = objData.rows
    arrText : List[str] = []
    for entry in arrProductAndQuantity:
      arrText.append(entry.productString)
    assert(isinstance(arrText, list))
    print("... type=", type(arrText[0]), arrText[0])
    assert(isinstance(arrText[0], str))
    patterns.addTrainingData(arrText)
    entryClassifications : StoreResults = ClassifyEntryMain()
    assert(entryClassifications.arrInputText)
    patterns.addTrainingData(entryClassifications.arrInputText)
    return patterns

@typechecked
@dataclass
class FoodPatterns:
  """
  @brief an object holding the result of the NLP generation of input data
  @remarks
  """
  def __post_init__(self):
    patterns = PatternsToFind.init()
    self.arrTrainingData = patterns.getTrainData()   # type: ignore[type-arg]
    self.arrTextsWeFailedToClassify = patterns.getTextsWeFailedToClassify()

@typechecked
def main() -> FoodPatterns:
  """
  @brief constructs the training-data
  @return the training-data
  """
  return FoodPatterns() #! ie, an object holding the result of the NLP generation of input data

if __name__ == "__main__":
    """
    @brief
    @remarks
    """
    foodPatterns : FoodPatterns = main()  # type: ignore[type-arg]
    assert(foodPatterns.arrTrainingData)
    for index, row in enumerate(foodPatterns.arrTrainingData):
      print(f"[{index}]\t {row}")
    assert(False) # FIXME: write sanit-tests for this module
