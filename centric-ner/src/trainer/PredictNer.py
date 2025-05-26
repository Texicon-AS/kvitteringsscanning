#!/usr/bin/python3
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name, bad-whitespace,bad-continuation,wrong-import-position,bad-indentation,pointless-string-statement,superfluous-parens,line-too-long,singleton-comparison
"""
@file
@brief train a NER model using basic=simplfied data, ie, a NER hello-world example
@remarks
- Task: "How to train NER from a blank SpaCy model?"
- when: "If you don’t want to use a pre-existing model, you can create an empty model using spacy.blank() by just passing the language ID. For creating an empty model in the English language, you have to pass “en”. " [https://www.machinelearningplus.com/nlp/training-custom-ner-model-in-spacy/]
- template: https://www.machinelearningplus.com/nlp/training-custom-ner-model-in-spacy/
"""
from __future__ import annotations #! used for "forward decleartions";
#from typing import ClassVar
from typing import List #, Dict
#from typing import Tuple
from typing import Optional, Union, cast
from dataclasses import dataclass, field
import random
from pathlib import Path
#import os
#import traceback
from typeguard import typechecked
# os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' #! used to hide the Tensofrlow deubing errors [https://stackoverflow.com/questions/35911252/disable-tensorflow-debugging-information]
# Load pre-existing spacy model
import spacy
from spacy.training import Example
from spacy.language import Language #! needd when using "mypy"
from spacy.util import minibatch
from spacy.util import compounding # type: ignore[attr-defined] # TODO: resolve this
from spacy.util import filter_spans
from spacy.tokens import DocBin
#from spacy.util import DocBin
#from tqdm import tqdm

#! Local files:
#from trainer.PatternsToFind import main as PatternsToFindMain
from trainer.PatternsToFind import FoodPatterns
#from CommandLine import applyCmd
#from CommandLineTrainer import
#from CommandLineTrainer import
from trainer.CommandLineTrainer import spacy_trainUsingCommandLine

# pylint: disable=unused-argument,missing-function-docstring
# mypy:  disable-error-code=empty-body
def f(var: 'PredictNer') -> int:  #! ie, a forward decleartion
  ...


@typechecked
@dataclass
class PredictNer:
  """
  @brief performs the label-training with aim of idneitfying/rechoniziing "Named Entities" (NER)
  @remarks
  """
  __nlp : Language #  = spacy.load(self.modelName)
  _nameOfGenertedModel : Path = field(default_factory = lambda : Path("centricFoodModel")) #! which defines where to store the path
  #_arrTrainData : List[tuple] = field(default_factory = lambda : [])  # type: ignore[type-arg]
  #__trainingWasPerformed : bool = field(init = False, default = False)
  # _useLocalTraining : bool = field(default = True)
  # modelName : str = field(default_factory = lambda : "en_core_web_sm")

  def train(self, arrTrainData : List[tuple], useLocalTraining : bool = False) -> bool:
    """
    @brief trains the model
    @return True if the training was performed
    """
    if(not arrTrainData):
      #if(self._useLocalTraining):
      print("(note)\t[PredictNer::__post_init__]\t zero training data provided, thus, skipts the training")
      # self.__trainingWasPerformed = False
      return False #! as the model then model is used as-is
    # Getting the pipeline component
    if(useLocalTraining):
      ner = self.__nlp.get_pipe("ner")
      # Adding labels to the `ner`
      for _, annotations in arrTrainData:
        for ent in annotations.get("entities"):
          # print("add.label=", ent[2])
          ner.add_label(ent[2])    # type: ignore[attr-defined]
      #
      trainingWasPerformed = self.__trainLocally(arrTrainData)
    else:
      trainingWasPerformed = self.__useBuiltInTrainer(arrTrainData)
    print("[PredictNer]\t the training was completed")
    return trainingWasPerformed


  #@property
  #def trainingWasPerformed(self) -> bool:
  #return self.__trainingWasPerformed

  # @property
  # def trainData(self) -> List[tuple]: # type: ignore[type-arg]
  #   """ @return the training data used for this model, ie, if any """
  #   return arrTrainData

  def __storeModel(self) -> None:
    """
    @brief stores the model to disk
    @remarks
    . what: saves the model to given directory
    - when: expected to be perormed after the training
    """
    self.__nlp.meta['name'] = 'model-predictNer'  # rename model
    if not self._nameOfGenertedModel.exists():
      self._nameOfGenertedModel.mkdir()
    self.__nlp.to_disk(self._nameOfGenertedModel)
    print("[PredictNer.py]\t Saved model to", self._nameOfGenertedModel)

  @property
  def modelPathResult(self) -> Path:
    """
    @brief get the model name
    @return the path to the generated model
    """
    #assert(self.__trainingWasPerformed) #! as this call is otehrwise wrong, as zero mdeol has been trained
    return self._nameOfGenertedModel

  def __getTrainDataAsDocBin(self, arrTrainData : List[tuple]) -> DocBin:
    """
    @brief wrap the training data in a DocBin object
    @remarks
    - what + why: "spaCy uses DocBin class for annotated data, so we’ll have to create the DocBin objects for our training examples. This DocBin class efficiently serializes the information from a collection of Doc objects. It is faster and produces smaller data sizes than pickle, and allows the user to deserialize without executing arbitrary Python code.":
    - language support: other lanauges (than "en") is listed at [https://github.com/explosion/spaCy/tree/master/spacy/lang]
    - how to load a new spacy model [https://github.com/explosion/spaCy/blob/320a8b14814c7e0c6dce705ad7bf0f13bf64b61c/spacy/__init__.py#L33]
    - vs the use of "blank(..)" to altneraitve stategies: "Underfitting may be due the fact that spacy blank models are too small to perform well in your situation. In my experience spacy blank models are about 5Mb which is small (especially if we compare it with the size of spacy pretrained models that can be around 500 Mb)" [https://stackoverflow.com/questions/62272190/spacy-blank-ner-model-underfitting-even-when-trained-on-a-large-dataset]
    @TODO: instead of the above, try: nlp = spacy.load("en_core_web_sm", disable = ['ner']) <-- backgorund: "If the only thing you are changing is NER, I would start with the pre-trained model (I assume English), and just disable NER pipe" [https://stackoverflow.com/questions/64724483/what-is-the-underlying-architecture-of-spacys-blank-model-spacy-blanken]
    """
    docBin = DocBin()
    #
    #! Step: resolve isseus related to overlaps: "There are some entity span overlaps, i.e., the indices of some entities overlap. spaCy provides a utility method filter_spans to deal with this. ":
    for text, trainingData  in arrTrainData: # tqdm(arrTrainData['annotations']):
      # print("trainingData=", trainingData)
      labels = trainingData['entities']
      doc = self.__nlp.make_doc(text)
      ents = []
      for start, end, label in labels:
        span = doc.char_span(start, end, label=label, alignment_mode="contract")
        if span is None:
          print("[PredictNer.py]\t Skipping entity", span)
        else:
          ents.append(span)
        filtered_ents = filter_spans(ents)
        doc.ents = filtered_ents
        docBin.add(doc)
    return docBin


  def __useBuiltInTrainer(self, arrTrainData : List[tuple]) -> bool:
    """
    @brief applies the build-in trainer for updating the model
    @return True on succcess
    """
    docBin = self.__getTrainDataAsDocBin(arrTrainData)
    nameOfGenertedModel : str = self._nameOfGenertedModel.name #! ie, dorp any directory preficxes from the nname <-- TODO: cases hwer this would be wrong?
    fileNameOfDataModelForTraining = nameOfGenertedModel + ".spacy"
    docBin.to_disk(fileNameOfDataModelForTraining) # save the docbin object
    spacy_trainUsingCommandLine(self.__nlp, docBin,
                                fileNameOfDataModelForTraining,
                                language = "norwegian",
                                # FIXME: write data which is ematn for testing ... in the traning we use all the inptu-data? ... if yes, then how is the model trained? ... does it use a larger dataset (than what we ahve provided)? ... we shoudl add test data ... suggestions for whoch data to use for testing? <-- should be extrem/challenging corner-cases?
                                nameOfGenertedModel = nameOfGenertedModel)

    #! Note: we do NOT call our "__storeModel(..)" as this task is deletegated to the above "spacy_trainUsingCommandLine(..)"
    # TODO: how to validate that the above works? <-- then use this to adjsut the below reutnr-value
    return True

  def __trainLocally(self, arrTrainData : List[tuple]) -> bool:
    """
    @brief applied a local permtuion of the NLP model training
    @return True if the training was performed
    """
    #!
    #! "Finally, all of the training is done within the context of the nlp model with disabled pipeline, to prevent the other components from being involved."
    # List of pipes you want to train: Disable pipeline components you dont need to change
    pipe_exceptions = ["ner", "trf_wordpiecer", "trf_tok2vec"]
    # List of pipes which should remain unaffected in training
    unaffected_pipes = [pipe for pipe in self.__nlp.pipe_names if pipe not in pipe_exceptions]
    #!
    # TRAINING THE MODEL
    with self.__nlp.disable_pipes(*unaffected_pipes):
      for _ in range(30): # Training for 30 iterations:
        # shuufling examples  before every iteration <-- tODO: why ensssayr?
        random.shuffle(arrTrainData)
        losses : dict = {}  # type: ignore[type-arg]
        # batch up the examples using spaCy's minibatch
        # fXIME: why is algortihm=minibatch used for training?
        batches = minibatch(arrTrainData, size=compounding(4.0, 32.0, 1.001)) # type: ignore[no-untyped-call]
        # TODO: explreo senitty to differnet minibatch configraitions
        #batches = minibatch(arrTrainData, size=compounding(1.0, 4.0, 1.001))
        for batch in batches:
          arr_example = []
          for text, annot in batch:
            # print(text)
            #texts, annotations = zip(*batch)
            #print("texts=", texts)
            doc = self.__nlp.make_doc(text)
            example = Example.from_dict(doc, annot)
            arr_example.append(example)
          # Update the model
          #! "At each word, the update() it makes a prediction. It then consults the annotations to check if the prediction is right. If it isn’t, it adjusts the weights so that the correct action will score higher next time."
          self.__nlp.update(arr_example, losses=losses, drop=0.5)
          # TODO: explroe effect of the bleow permtuatons
          # self.__nlp.update([example], losses=losses, drop=0.3)
          # optimizer = self.__nlp.resume_training()
          # self.__nlp.update(arr_example, losses=losses,  sgd=optimizer, drop=0.35)

          # self.__nlp.update(
          #             texts,  # batch of texts
          #             annotations,  # batch of annotations
          #             drop=0.5,  # dropout - make it harder to memorise data
          #             losses=losses,
          #         )
          print("Losses", losses)
      #!
      #! Export/Store the model:
      self.__storeModel()
      return True

  def resumeTraining(self, arrText : List[str]) -> None:
    """
    @brief
    """
    assert(False) # FIXME: write an example using this <-- then update the below scaffold code
    # Getting the ner component
    ner = self.__nlp.get_pipe('ner')
    # Resume training
    #optimizer = self.__nlp.resume_training()
    move_names = list(ner.move_names)
    assert self.__nlp.get_pipe("ner").move_names == move_names
    for text in arrText:
      doc = self.__nlp(text)
      for ent in doc.ents:
        print(ent.label_, ent.text)

  @classmethod
  def initFromModelFile(cls, modelPath : Optional[Union[str, Path]] = "en_core_web_sm",
                        arrTrainData : Optional[List[tuple]] = lambda : [],  # type: ignore[type-arg]
                        useLocalTraining : Optional[bool] = True,
                        _nameOfGenertedModel : Optional[Path] = Path("centricFoodModel")
                        ) -> PredictNer:
    """
    @brief loads a model from either a local model-file, or a global model-file
    @return
    @remarks
    - example1: use the "en_core_web_sm" model
    - example2: use the model auto-exported from this class (ie, after the training has completed)
    """
    # Load the saved model and predict
    print("Loading from", modelPath)
    assert(modelPath != None)
    nlp : Language = spacy.load(cast(Union[str, Path], modelPath))
    #doc = nlp_updated("Fridge can be ordered in FlipKart" )
    #print("Entities", [(ent.text, ent.label_) for ent in doc.ents])
    #assert(arrTrainData) #! as we asusme this was providede <-- TODO: remove
    assert(_nameOfGenertedModel != None)
    if(isinstance(_nameOfGenertedModel, str)):
      nameOfGenertedModelPath = Path(_nameOfGenertedModel)
    else:
      nameOfGenertedModelPath = _nameOfGenertedModel
    assert(isinstance(nameOfGenertedModelPath, Path))
    predictor = PredictNer(nlp, _nameOfGenertedModel = nameOfGenertedModelPath)
    wasPerformed = predictor.train(arrTrainData = arrTrainData, # type: ignore[arg-type]
                                   useLocalTraining = cast(bool, useLocalTraining))
    if(arrTrainData):
      assert(wasPerformed) #! as we otheriwe have a bug
    return predictor



  def predict(self, text : str) -> int:
    """
    @brief predicts using the current NLP model
    @return the number of identifed entries
    """
    print("--------------- (tut)\t predicts for text: ", text)
    # Testing the model
    doc = self.__nlp(text)
    print("Entities", [(ent.text, ent.label_) for ent in doc.ents])
    # Testing the NER
    # print("Entities in '%s'" % test_text)
    for ent in doc.ents:
      print(ent)
    return len(doc.ents) #! where returnv-value = zero indciates that we were NOT able to classify this


#! ***************************************

@typechecked
def testGeneratedModel(trainNer : PredictNer, arrTrainData : List[tuple]) -> List[str]:
  """
  @brief predicts entries listed in the training data
  @return the texts which we failed to classify
  @remarks a base-test for the training; for an actualy quality-control use data not part of the training itself
  """
  cntFailedToIdentify : int = 0
  cntIdentifedTotal : int = 0 #! used as a control
  arrFailedToPredict : List[str] = []
  for entry in arrTrainData:
    text = entry[0]
    # TODO: what to validate?
    cntIdentified : int = trainNer.predict(text)  #! ie, test the gneraed model
    if(cntIdentified == 0):
      print("(PredictNer.py::predict:failedCase)\t ", text)
      arrFailedToPredict.append(text)
      cntFailedToIdentify += 1
    cntIdentifedTotal += cntIdentified
  # TODO: apply tests to classify this <-- which?
  if(cntFailedToIdentify):
    print(f"!!\t[PredictNer.py::testGeneratedModel]\t Failed to idneitfy {cntFailedToIdentify} cases")
  #! Validate: Re-load the model:
  modelNameExported : Path = trainNer.modelPathResult
  assert(modelNameExported != None)
  trainNerReloaded = PredictNer.initFromModelFile(modelPath = modelNameExported, arrTrainData = [])
  cntIdentifedTotalAfterReload : int = 0 #! used as a control
  for entry in arrTrainData: #trainNer.trainData:
    text = entry[0]
    # TODO: what to validate?
    cntIdentified : int = trainNerReloaded.predict(text) # type: ignore[no-redef] #! ie, test the gneraed model
    cntIdentifedTotalAfterReload += cntIdentified
  print(f"cntIdentifedTotalAfterReload:{cntIdentifedTotalAfterReload} VS cntIdentifedTotal:{cntIdentifedTotal}")
  # assert(cntIdentifedTotalAfterReload == cntIdentifedTotal)
  return arrFailedToPredict

@typechecked
def loadAndValidate(arrTrainData : List[tuple], useLocalTraining : bool) -> None:  # type: ignore[type-arg]
  """
  @brief validates the basic of thr training-lgoics
  """
  assert(arrTrainData) #! as we asusme this was providede
  for modelPath in [
      #! Note: the belwo models are expected to be downlaoded when running the "x-installer.bash" script
      "en_core_web_sm",
      "nb_core_news_sm",
      # "nb_core_news_lg",
      # "en_core_web_lg",
  ]:
    trainNer1 : PredictNer = PredictNer.initFromModelFile(modelPath = modelPath,
                                                          arrTrainData  = arrTrainData,
                                                          useLocalTraining = useLocalTraining
                                                          )
    print(f"[PredictNer.py::main]\t the \"{modelPath}\" was loaded")
    #assert(trainNer1.trainingWasPerformed)
    #! Validate the basics of the loaded model:
    testGeneratedModel(trainNer1, arrTrainData)

def buildFoodModel(useLocalTraining : bool = False, dropTrainingIfModelExists : bool = False) -> List[PredictNer]:
  """
  @brief constructs the training-data
  @param useLocalTraining gives an singht into the effect of optmized/deicated batch-training; prelimiary expierments indicates that accuracy is sigicntfaly improved if useLocalTraining = False
  @param dropTrainingIfModelExists introduced to make mdoel-testing + experiemntaiotn mreo resabiel
  @return the training-data
  """
  arrModelNames : List[Path] = [
    Path("centricFoodModel_nb"),
    Path("centricFoodModel_en"),
  ]

  if(dropTrainingIfModelExists):
    arrPredictors : List[PredictNer] = []
    try:
      for modelName in arrModelNames:
        nlp : Language = spacy.load(cast(Union[str, Path], modelName))
        predictor : PredictNer = PredictNer(nlp, modelName)
        arrPredictors.append(predictor)
      return arrPredictors
    except Exception as e: # FIXME: make this exception more specific
      print("!!\t[PredictNer.py::buildFoodModel]\t Unable to load existing models. Therefore, starts the trainign from scrach (which can take some time + system resoruces). This, givne the follwoing error: ", e)


  foodPatterns : FoodPatterns = FoodPatterns() #! ie, an object holding the result of the NLP generation of input data
  #modelPath = "nb_core_news_sm" # TODO: drop this, get the below to work!
  modelPath = "nb_core_news_lg" #
  trainNerFoods : PredictNer = PredictNer.initFromModelFile(
    modelPath = modelPath,
    arrTrainData = foodPatterns.arrTrainingData,
    useLocalTraining = useLocalTraining,
    _nameOfGenertedModel = arrModelNames[0]
  )
  print(f"[PredictNer.py::main]\t the \"{modelPath}\" was loaded")
  #assert(trainNerFoods.trainingWasPerformed)
  #! apply tests to classify this
  arrFailedToPredictNb : List[str] = testGeneratedModel(trainNerFoods, foodPatterns.arrTrainingData)
  if(not arrFailedToPredictNb): #! then we managed to predict all
    return [trainNerFoods]
  print(f"[PredictNer::main]\t failed to predict {len(arrFailedToPredictNb)} entries (norwegian)")
  #! Then re-apply
  # FIXME: instead of the "en_core_web_lg" use a better sutied model? if yes, suggestions?
  modelPath : str = "en_core_web_lg" # type: ignore[no-redef]
  trainNerFoodsEng : PredictNer = PredictNer.initFromModelFile(modelPath = modelPath,
                                                               arrTrainData = foodPatterns.arrTrainingData,
                                                               useLocalTraining = useLocalTraining,
                                                               _nameOfGenertedModel = arrModelNames[1]
                                                               )
  print(f"[PredictNer.py::main]\t the \"{modelPath}\" was loaded")
  # assert(trainNerFoodsEng.trainingWasPerformed)
  #! apply tests to classify this
  arrFailedToPredictEn : List[str] = testGeneratedModel(trainNerFoodsEng, foodPatterns.arrTrainingData)
  if(arrFailedToPredictEn):
    print(f"[PredictNer::main]\t failed to predict {len(arrFailedToPredictEn)} entries (english)")
    if(len(arrFailedToPredictEn) == len(arrFailedToPredictNb)):
      print("[PredictNer::main]\t \t Note: exedning oru prediciton with the enligsh data-set did NOT help")
    for text in arrFailedToPredictEn:
      if(text in arrFailedToPredictNb):
        print(f"\t\t(PredictNer.py::prediction failed for)\t{text}")
      # else: #! then it was correctlly in the first/default calcuation
      #print(f"\t\t(PredictNer.py::prediction failed for)\t{text}")
  return [trainNerFoods, trainNerFoodsEng]


@typechecked
def main() -> List[PredictNer]:
  """
  @brief constructs the training-data
  @return the training-data
  """
  #! Pre: perofmr a dummy run, thus, to effitvely weed out basic bugs:
  arrTrainData : List[tuple] = [  # type: ignore[type-arg]
    # Below/idea: "Each tuple should contain the text and a dictionary. The dictionary should hold the start and end indices of the named enity in the text, and the category or label of the named entity.":
    ("Walmart is a leading e-commerce company", {"entities": [(0, 7, "ORG")]}),
    ("I reached Chennai yesterday.", {"entities": [(19, 28, "GPE")]}),
    ("I recently ordered a book from Amazon", {"entities": [(24,32, "ORG")]}),
    ("I was driving a BMW", {"entities": [(16,19, "PRODUCT")]}),
    ("I ordered this from ShopClues", {"entities": [(20,29, "ORG")]}),
    ("Fridge can be ordered in Amazon ", {"entities": [(0,6, "PRODUCT")]}),
    ("I bought a new Washer", {"entities": [(16,22, "PRODUCT")]}),
    ("I bought a old table", {"entities": [(16,21, "PRODUCT")]}),
    ("I bought a fancy dress", {"entities": [(18,23, "PRODUCT")]}),
    ("I rented a camera", {"entities": [(12,18, "PRODUCT")]}),
    ("I rented a tent for our trip", {"entities": [(12,16, "PRODUCT")]}),
    ("I rented a screwdriver from our neighbour", {"entities": [(12,22, "PRODUCT")]}),
    ("I repaired my computer", {"entities": [(15,23, "PRODUCT")]}),
    ("I got my clock fixed", {"entities": [(16,21, "PRODUCT")]}),
    ("I got my truck fixed", {"entities": [(16,21, "PRODUCT")]}),
    ("Flipkart started it's journey from zero", {"entities": [(0,8, "ORG")]}),
    ("I recently ordered from Max", {"entities": [(24,27, "ORG")]}),
    ("Flipkart is recognized as leader in market",{"entities": [(0,8, "ORG")]}),
    ("I recently ordered from Swiggy", {"entities": [(24,29, "ORG")]})
  ]

  _ = loadAndValidate(arrTrainData, useLocalTraining = False)
  _ = loadAndValidate(arrTrainData, useLocalTraining = True)
  # ****************************************
  #!
  #! Consturct the model we need:
  #! Pre: try reloading an existing pre-calcuated model:
  arrPredictors : List[PredictNer]  = buildFoodModel(useLocalTraining = False, dropTrainingIfModelExists = True)
  assert(arrPredictors)
  #! Pre: validate tah thte lcoal training works:
  #buildFoodModel(useLocalTraining = True)
  #! Then, use the better-suited generic/estlibhes traning-approach:
  return buildFoodModel(useLocalTraining = False)


if __name__ == "__main__":
    """
    @brief
    @remarks
    """
    _ = main()
