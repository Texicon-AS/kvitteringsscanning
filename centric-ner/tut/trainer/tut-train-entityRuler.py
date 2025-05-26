"""!
@brief exemplfies an appraoch using python-classes to build NER models
@remarks
- template: https://towardsdatascience.com/clinical-named-entity-recognition-using-spacy-5ae9c002e86f
"""
# FIXME: compare this apprahc to orus .... what can we learn=derive=use?
surgery = set(['acute cholangitis', 'appendectomy',
               'appendicitis', 'cholecystectomy',
               'laser capsulotomy', 'surgisis xenograft',
               'sclerotomies', 'tonsillectomy'
               ])

import spacy
from spacy.lang.en import English
from spacy.pipeline import EntityRuler

class RulerModel():
  def __init__(self, surgery, internalMedicine, medication, obstetricsGynecology):
    self.ruler_model = spacy.blank('en')
    self.entity_ruler =      self.ruler_model.add_pipe('entity_ruler')

    total_patterns = []
    patterns = self.create_patterns(surgery, 'surgery')
    total_patterns.extend(patterns)
    patterns = self.create_patterns(internalMedicine, 'internalMedicine')
    total_patterns.extend(patterns)
    patterns = self.create_patterns(medication, 'medication')
    total_patterns.extend(patterns)

    patterns = self.create_patterns(obstetricsGynecology, 'obstetricsGynecology')
    total_patterns.extend(patterns)

    self.add_patterns_into_ruler(total_patterns)

    self.save_ruler_model()

  def create_patterns(self, entity_type_set, entity_type): # FIXME: validate these data-types <--- pre: describe example-cases ... eg, example-patterns we can add to: add_pipe("entity_ruler").add_patterns(...) <-- pre: write a new tut for this
    """
    @brief
    """
    # FIXME: what does the "entity_type_set" to contain?
    patterns = []
    for item in entity_type_set:
      pattern = {'label': entity_type, 'pattern': item}
      patterns.append(pattern)
    return patterns

  def add_patterns_into_ruler(self, total_patterns):
    self.entity_ruler.add_patterns(total_patterns)

#RulerModel().ruler_model.to_disk('./model/ruler_model') # FIXME: update this ... use this to update the "../trainer/tut-trainNer.py"?
#ruler_model.to_disk('./model/RulerModel')

class GenerateDataset: # FIXME: write an example using this class ... ie, which goes throoough text-models and then update update data-model

  def __init__(self, ruler_model):
    self.ruler_model = ruler_model

  def find_entitytypes(self, text):
    ents = []
    doc = self.ruler_model(str(text))
    for ent in doc.ents:
      # FIXME: is the below strategy similar to ours?
      ents.append((ent.start_char, ent.end_char, ent.label_))
    return ents

  def assign_labels_to_documents(self, df):
    dataset = []
    text_list = df['transcription'].values.tolist()
    for text in text_list:
      ents = self.find_entitytypes(text)
      if len(ents) > 0:
        dataset.append((text, {'entities': ents}))
      else:
        continue
    return dataset

import spacy
from spacy.util import minibatch
from spacy.scorer import Scorer
from tqdm import tqdm
import random

class NERModel():
  def __init__(self, iterations=10):
    self.n_iter = iterations
    self.ner_model = spacy.blank('en')
    self.ner = self.ner_model.add_pipe('ner', last=True)

  def fit(self, train_data):
    for text, annotations in train_data:
      for ent_tuple in annotations.get('entities'):
        self.ner.add_label(ent_tuple[2])
    other_pipes = [pipe for pipe in self.ner_model.pipe_names            if pipe != 'ner']

    self.loss_history = []

    train_examples = []
    for text, annotations in train_data:
      train_examples.append(Example.from_dict(
        self.ner_model.make_doc(text), annotations))

    with self.ner_model.disable_pipes(*other_pipes):
      optimizer = self.ner_model.begin_training()
      for iteration in range(self.n_iter):
        print(f'---- NER model training iteration {iteration + 1} / {self.n_iter} ... ----')
        random.shuffle(train_examples)
        train_losses = {}
        batches = minibatch(train_examples,   size=spacy.util.compounding(4.0, 32.0, 1.001))
        batches_list = [(idx, batch) for idx, batch in   enumerate(batches)]
        for idx, batch in tqdm(batches_list):
          self.ner_model.update(
            batch,
            drop=0.5,
            losses=train_losses,
            sgd=optimizer,
          )

          self.loss_history.append(train_losses)
          print(train_losses)
  def accuracy_score(self, test_data):
    # FIXME: try using our "spacy.scorer" into our appraoch <-- first find relatet=Simliar exmapels!
    examples = []
    scorer = Scorer()
    for text, annotations in test_data:
      pred_doc = self.ner_model(text)
      try:
        example = Example.from_dict(pred_doc, annotations)
      except:
        print(f'Error: failed to process document: \n{text},  \n\n annotations: {annotations}')
        continue

      examples.append(example)

    accuracy = scorer.score(examples)
    return accuracy

#!
#! Taks. print loss history
if(False): # FIXME: how to get the "loss_history"?
  objNerModel = NERModel()
  assert(False) # FIXME: call the "objNerModel.fit(..)" <-- pre: adjsut the latter with the data to train ... then add a unti test for the udpated "fit(".."), ie, before continuting with the below
  #ner_model = objNerModel.ner_model
  from matplotlib import pyplot as plt
  loss_history = [loss['ner'] for loss in objNerModel.loss_history] # FIXME: update this
  plt.title("Model Training Loss History")
  plt.xlabel("Iterations")
  plt.ylabel("Loss")
  plt.plot(loss_history)


from spacy.language import Language
def extend_model(surgery, internalMedicine,                  medication, obstetricsGynecology):
  #ruler_model = spacy.load('./model/ruler_model')
  ruler_model = spacy.load('./model/RulerModel') # FIXME: where is this data-model exported?
  base_ner_model = spacy.load('./model/ner_model')
  @Language.component("my_entity_ruler")
  def ruler_component(doc):
    doc = ruler_model(doc)
    return doc

  for entity_type_set in [surgery, internalMedicine,                    medication, obstetricsGynecology]:
    for item in entity_type_set:
      base_ner_model.vocab.strings.add(item)
      if 'my_entity_ruler' in base_ner_model.pipe_names:
        base_ner_model.remove_pipe('my_entity_ruler')
        base_ner_model.add_pipe("my_entity_ruler", before='ner')

  return base_ner_model


doc = extended_ner_model(text)



def display_doc(doc):
    colors = { "surgery": "pink",
               "internalMedicine": "orange",
               "medication": "lightblue",
               "obstetricsGynecology": "lightgreen",
             }
    options = {"ents": ["surgery",
                        "internalMedicine",
                        "medication",
                        "obstetricsGynecology",
                       ],
                "colors": colors
              }

displacy.render(doc, style='ent',
                options=options, jupyter=True)
display_doc(doc)
