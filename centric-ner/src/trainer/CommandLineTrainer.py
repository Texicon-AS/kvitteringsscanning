#!/usr/bin/python3
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name, bad-whitespace,bad-continuation,wrong-import-position,bad-indentation,pointless-string-statement,superfluous-parens,line-too-long,consider-using-f-string,singleton-comparison, broad-exception-caught
"""
@file
@brief provides comamnd line tulises used for the Spacy library, eg, for algorithmic model-training
@remarks before running this, remember to call the `../../x-installer.bash` script
"""
import sys
import os
from typing import Optional
from spacy.language import Language #! needd when using "mypy"
from spacy.tokens import DocBin

#! Local modules:
from trainer.CommandLine import applyCmd
from trainer.CommandLine import moveFileToDateTimeAnnotationIfAlreadyExists

#!
#! Step: construc tthe config-file:
#! Note: the below alternaitves=suggesitons where created at [https://spacy.io/usage/training#quickstart]
str_config_en = """
# This is an auto-generated partial config. To use it with 'spacy train'
# you can run spacy init fill-config to auto-fill all default settings:
# python -m spacy init fill-config ./base_config.cfg ./config.cfg
[paths]
train = null
dev = null
vectors = "en_core_web_lg"
[system]
gpu_allocator = null

[nlp]
lang = "en"
pipeline = ["tok2vec","ner"]
batch_size = 1000

[components]

[components.tok2vec]
factory = "tok2vec"

[components.tok2vec.model]
@architectures = "spacy.Tok2Vec.v1"

[components.tok2vec.model.embed]
@architectures = "spacy.MultiHashEmbed.v1"
width = ${components.tok2vec.model.encode.width}
attrs = ["NORM", "PREFIX", "SUFFIX", "SHAPE"]
rows = [5000, 1000, 2500, 2500]
include_static_vectors = false

[components.tok2vec.model.encode]
@architectures = "spacy.MaxoutWindowEncoder.v1"
width = 256
depth = 8
window_size = 1
maxout_pieces = 3

[components.ner]
factory = "ner"

[components.ner.model]
@architectures = "spacy.TransitionBasedParser.v1"
state_type = "ner"
extra_state_tokens = false
hidden_width = 64
maxout_pieces = 2
use_upper = true
nO = null

[components.ner.model.tok2vec]
@architectures = "spacy.Tok2VecListener.v1"
width = ${components.tok2vec.model.encode.width}

[corpora]

[corpora.train]
@readers = "spacy.Corpus.v1"
path = ${paths.train}
max_length = 0

[corpora.dev]
@readers = "spacy.Corpus.v1"
path = ${paths.dev}
max_length = 0

[training]
dev_corpus = "corpora.dev"
train_corpus = "corpora.train"

[training.optimizer]
@optimizers = "Adam.v1"

[training.batcher]
@batchers = "spacy.batch_by_words.v1"
discard_oversize = false
tolerance = 0.2

[training.batcher.size]
@schedules = "compounding.v1"
start = 100
stop = 1000
compound = 1.001

[initialize]
vectors = ${paths.vectors}
"""
str_config_no = """
# This is an auto-generated partial config. To use it with 'spacy train'
# you can run spacy init fill-config to auto-fill all default settings:
# python -m spacy init fill-config ./base_config.cfg ./config.cfg
[paths]
train = null
dev = null
# vectors = "nb_core_news_lg"
vectors = "nb_core_news_sm"
[system]
gpu_allocator = null

[nlp]
lang = "nb"
pipeline = ["tok2vec","ner"]
batch_size = 1000

[components]

[components.tok2vec]
factory = "tok2vec"

[components.tok2vec.model]
@architectures = "spacy.Tok2Vec.v1"

[components.tok2vec.model.embed]
@architectures = "spacy.MultiHashEmbed.v1"
width = ${components.tok2vec.model.encode.width}
attrs = ["NORM", "PREFIX", "SUFFIX", "SHAPE"]
rows = [5000, 1000, 2500, 2500]
include_static_vectors = false

[components.tok2vec.model.encode]
@architectures = "spacy.MaxoutWindowEncoder.v1"
width = 256
depth = 8
window_size = 1
maxout_pieces = 3

[components.ner]
factory = "ner"

[components.ner.model]
@architectures = "spacy.TransitionBasedParser.v1"
state_type = "ner"
extra_state_tokens = false
hidden_width = 64
maxout_pieces = 2
use_upper = true
nO = null

[components.ner.model.tok2vec]
@architectures = "spacy.Tok2VecListener.v1"
width = ${components.tok2vec.model.encode.width}

[corpora]

[corpora.train]
@readers = "spacy.Corpus.v1"
path = ${paths.train}
max_length = 0

[corpora.dev]
@readers = "spacy.Corpus.v1"
path = ${paths.dev}
max_length = 0

[training]
dev_corpus = "corpora.dev"
train_corpus = "corpora.train"

[training.optimizer]
@optimizers = "Adam.v1"

[training.batcher]
@batchers = "spacy.batch_by_words.v1"
discard_oversize = false
tolerance = 0.2

[training.batcher.size]
@schedules = "compounding.v1"
start = 100
stop = 1000
compound = 1.001

[initialize]
vectors = ${paths.vectors}
"""


def __sanityCheckOndocBin(nlp : Language, docBin : DocBin) -> None:
  """
  @brief perform baisc sanity-cheklcs of the input
  @remarks
  - scope: ease udneringg of bugs in data
  - overlap: relates to oru "x-spacyDebugger-readDocBinFile.py"
  """
  docs = list(docBin.get_docs(nlp.vocab))
  if(len(docs) == 0):
    print("!!\t[CommandLineTrainer.py]\t not any entries (in the data to analyse): could it be that zero=None (of the trainign data strings) matches the ctieria?")
  assert(len(docs) > 0) #! as the data-file otherwise cotnians not any enties, ie, would be an dicniatorion of a bug!
  # TODO: suggeiosnt for other tests (to integrate)?


def spacy_trainUsingCommandLine(nlp : Language, docBin : DocBin,
                                fileNameOfDataModelForTraining : str,
                                language : str, nameOfGenertedModel : str,
                                #fileNameOfDataModelForScoreTesting : Optional[str] = lambda : ""
                                fileNameOfDataModelForScoreTesting : Optional[str] = ""
                                ) -> None:
  """
  @brief store teh model, and then use command-line to train it:
  """
  if(fileNameOfDataModelForScoreTesting in [None, fileNameOfDataModelForScoreTesting]):
    #! Reading: see: [https://stackoverflow.com/questions/66997147/train-ner-in-spacy-v3-needs-dev-spacy-at-command-line]
    print("(warn)\t[spacy_trainUsingCommandLine]\t Not any seperate score-testing file is provided. Implicaiton: \"The dev.spacy file should look exactly the same as the train.spacy file, but should contain new examples that the training process hasn't seen before to get a realistic evaluation of the performance of your model. To create this dev set, you can first split your original data into train/dev parts, and then run convert separately on each of them, calling the larger one train.spacy and the smaller one dev.spacy. As @mbrunecky suggests, an 80-20 split is usually good, but it depends on the dataset [https://stackoverflow.com/questions/66997147/train-ner-in-spacy-v3-needs-dev-spacy-at-command-line]")
    fileNameOfDataModelForScoreTesting = fileNameOfDataModelForTraining #! ie, epclty use the same

  folderName_default = "model-best/"  #! where "model-best" is assumed to be the deuflat=autognerated folder-name (resulting frm the aobve cmd-python-spacy call)
  try:
    #! Step: if leftovers of a previosu model is found, then remove this (To a new tmeproary drieoty, ie, eo avoid a cdeu=scary dele-process):
    moveFileToDateTimeAnnotationIfAlreadyExists(folderName_default)
  except Exception as e:
    print("!!\t[spacy_commandLineUtility]\t Unable to move file=\"{}\" to new location=\"{}\"".format(folderName_default, nameOfGenertedModel), str(e))

  assert(isinstance(docBin, DocBin))
  __sanityCheckOndocBin(nlp, docBin)
  str_config = str_config_en #! ie, the choise donfig <--
  if(language == "norwegian"):
    str_config = str_config_no
  elif(language != "english"):
    print("!!\t[CommandLineTrainer.py::spacy_trainUsingCommandLine]\t unsupprted language=", language)
    assert(False) #! ie, then add supprot for this (eg, by writing a enw cofnig-file)

  docBin.to_disk(fileNameOfDataModelForTraining) # save the docbin object
  #import tempfile
  fileNameConfig = "spacy_config.cfg"  # FIXME: instead, use a temprary-gnerated file-name?
  with open(fileNameConfig, 'w', encoding="utf8") as fileP:
    fileP.write(str_config)
    #fileP.close() # TODO: drop?
  fileName_result = "spacy.configAfterTuning.cfg"
  cmd = f"python3 -m spacy init fill-config {fileNameConfig} {fileName_result}"
  #cmd = f"python3 -m spacy init fill-config base_config.cfg {fileNameConfig}"
  is_ok = applyCmd(cmd )
  assert(is_ok)
  #cmd = f"python -m spacy init fill-config base_config.cfg config.cfg"

  #!
  #! Step:  trained the model:
  #cmd = f"python3 -m spacy train config.cfg --output ./ --paths.train ./training_data.spacy --paths.dev ./training_data.spacy --gpu-id 0"
  #cmd = f"python3 -m spacy train {fileName_result} --output ./ --paths.train {fileNameOfDataModelForTraining} --paths.dev  {fileNameOfDataModelForTraining} --gpu-id 0"
  #cmd = f"python3 -m spacy train {fileName_result} --output ./ --paths.train {fileNameOfDataModelForTraining} --paths.dev  {fileNameOfDataModelForTraining}"
  cmd = f"python3 -m spacy train {fileName_result} --output ./ --paths.train {fileNameOfDataModelForTraining} --paths.dev  {fileNameOfDataModelForScoreTesting}"
  is_ok = applyCmd(cmd)
  if(not is_ok):
    sys.stderr.write(f"!!\t [CommandLineTrainer.py]\tUnable to perform the following task: {cmd}")
    return
  #!
  #! Step: rename the folder:
  try:
    print("(info)\t[CommandLineTrainer.py]\t rename \"{}\" into \"{}\"".format(folderName_default, nameOfGenertedModel))
    #! Then rename the folder (as expeted by the caller):
    os.rename(folderName_default, nameOfGenertedModel) #! eg, to aovid ovewriting the preivosu modle (when a new run is appleid=called=started)
  except Exception as e:
    print("!!\t[spacy_commandLineUtility]\t Unable to move file=\"{}\" to new location=\"{}\"".format(folderName_default, nameOfGenertedModel), str(e))
