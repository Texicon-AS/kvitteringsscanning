#!/usr/bin/python3
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name, bad-whitespace,bad-continuation,wrong-import-position,bad-indentation,pointless-string-statement,superfluous-parens,line-too-long,singleton-comparison
"""
@brief provides a basic introdution to "Named Entity Rechongiion" (NER)
@remarks tempaltes:
- API: https://spacy.io/api/top-level
* baiscs: [https://www.machinelearningplus.com/spacy-tutorial-nlp/]
* algorithm-traning: https://newscatcherapi.com/blog/train-custom-named-entity-recognition-ner-model-with-spacy-v3
* custom-lanauge: "Every language is different – and usually full of exceptions and special cases, especially amongst the most common words. Some of these exceptions are shared across languages, while others are entirely specific – usually so specific that they need to be hard-coded. The lang module contains all language-specific data, organized in simple Python files. This makes the data easy to update and extend." [https://spacy.io/usage/linguistic-features#language-data]
@remarks notation
* a token: "Tokens are individual text entities that make up the text. Typically a token can be the words, punctuation, spaces, etc."
* tokenization: "Tokenization is the process of converting a text into smaller sub-texts, based on certain predefined rules. For example, sentences are tokenized to words (and punctuation optionally). And paragraphs into sentences, depending on the context. This is typically the first step for NLP tasks like text classification, sentiment analysis, etc. Each token in spacy has different attributes that tell us a great deal of information."
* stop-words: "Stop words and punctuation usually (not always) don’t add value to the meaning of the text and can potentially impact the outcome. To avoid this, its might make sense to remove them and clean the text of unwanted characters can reduce the size of the corpus."
* lemmatization: "Lemmatization is the method of converting a token to it’s root/base form.". <-- FIXME: update our code with this aspect
* Lemmatization (Motvation): "Have a look at these words: “played”, “playing”, “plays”, “play”. These words are not entirely unique, as they all basically refer to the root word: “play”. Very often, while trying to interpret the meaning of the text using NLP, you will be concerned about the root meaning and not the tense. For algorithms that work based on the number of occurrences of the words, having multiple forms of the same word will reduce the number of counts for the root word, which is ‘play’ in this case. Hence, counting “played” and “playing” as different tokens will not help."
- "part of speach analsysis" (POS-analysis): "Consider a sentence , “Emily likes playing football”. Here , Emily is a NOUN , and playing is a VERB. Likewise , each word of a text is either a noun, pronoun, verb, conjection, etc. These tags are called as Part of Speech tags (POS)."
"""
from __future__ import annotations #! used for "forward decleartions";
from dataclasses import dataclass #, field
from typing import List #, Dict
from typeguard import typechecked
import spacy
from spacy.language import Language #! needd when using "mypy"
# import json
from spacy import displacy
from spacy.tokens import Doc

#! Local files
from foodNer.MatchedEntry import MatchedLabel
from trainer.PatternsToFind import main as PatternsToFindMain
from trainer.PredictNer import buildFoodModel, PredictNer
from trainer.PredictNer import testGeneratedModel

# pylint: disable=unused-argument,missing-function-docstring
# mypy:  disable-error-code=empty-body
def f(var: 'TrainModel') -> int:  #! ie, a forward decleartion
  ...


@dataclass
class TrainModel:
  """
  @brief Logics for training and loading a given model
  @todo change the name of this module ... as we here focus on laoding (rather tan training). Then udpat ehte above documetaiotn
  """
  _nlp : Language
  # def __post_init__(self):

  @classmethod
  def initFromModel(cls, modelName : Union[Path, str]) -> TrainModel:
    """
    @brief loads the given model-name
    @return the loaded model
    """
    #! Load the model directly:
    print("Loading from", modelName)
    nlp : Language = spacy.load(modelName)
    return TrainModel(nlp)


  def predict(self, text, visu : bool = True) -> bool:
    """
    @brief predict the given text
    @return True if the text was classified
    """
    doc : Doc = self._nlp(text)
    # TODO: change how we dispaly/illsutrate the results ... eg, intead return a value?
    if(not doc.ents): #! as we assume all was classified
      print(f"!!\t[TrainModel::predict]\t Unable to classify the '{text}' text")
      return False
    for ent in doc.ents:
      print(ent)
    if(not visu):
      return True
    colors : dict = MatchedLabel.getColors() # type: ignore[type-arg]
    options = {"colors": colors}
    displacy.render(doc, style="ent", options=options, jupyter=False)
    return True

@typechecked
def getTrainFoodData() -> List[tuple]: # type: ignore[type-arg]
  """
  @return training data used for food-identificaiton
  """
  # FIXME: below uses too much memroy ... soemtimes making our text-PC to crash ... why such a large difference in the memory-consumption? ... where/what causes this voerhead?
  # TODO: instead of the below load exported data <-- which fucniton to call? <-- write this funciton?
  arrTrainDataFoods : List[tuple] = PatternsToFindMain()  # type: ignore[type-arg]
  assert(arrTrainDataFoods) #! ie, at least one text-string
  return arrTrainDataFoods

@typechecked
def main(testUsingAllData : bool = False) -> None:
  """
  @brief an abbrebiated interface for model training
  """
  if(testUsingAllData):
    arrTrainDataFoods : List[tuple]  = getTrainFoodData()
    assert(arrTrainDataFoods) #! ie, at least one text-string
  else:
    arrTrainDataFoods : List[tuple] = []

  arrTextToClassify = [
    # FIXME: move the below list to a enw module ?? focused on challeing data-sets to analyze
    # FIXME: update our grammar to correclty handle the below
    #! Note: the below subset is what we (in an aleri run) found impossible to clasisfy, thus, extend/update/mofiy the below when needed
    "Coop Solbærsirup 1,4l",
    "Coop Rå Kjøttboller Italiensk 360g",
    "Proteinfabrikken Flytende Eggehvite 1000ml", # FIXME: add permtautions of this to our AI-train-system ... as this currently is the cahhing case
    "Big One Pizza American Classic 570g",
    "Zoegas Blue Java Rwb 450g",
  ]
  #! Inspect the generated model:
  arrFoodModels : List[PredictNer] = buildFoodModel(dropTrainingIfModelExists = True) #! where latter argument is sued to reuce the test-time; if the model is NOT found, then we first train the model (ie, takes time + system reosucoeus)

  assert(len(arrFoodModels))
  for foodModel in arrFoodModels:
    if(testUsingAllData):
      arrFailedToClassify : List[str] = testGeneratedModel(foodModel, arrTrainDataFoods)
      print("Faild to classify: ", arrFailedToClassify)
    #! Then, use our local data:
    model : TrainModel = TrainModel.initFromModel(foodModel.modelPathResult)
    for text in arrTextToClassify:
      model.predict(text)

  #displacy.render(doc, style="ent", jupyter=False)

if __name__ == "__main__":
    """
    @brief
    @remarks
    """
    _ = main()
