"""!
@file
@brief train a NER model using basic=simplfied data, ie, a NER hello-world example
@remarks
- Task: "How to train NER from a blank SpaCy model?"
- when: "If you don’t want to use a pre-existing model, you can create an empty model using spacy.blank() by just passing the language ID. For creating an empty model in the English language, you have to pass “en”. " [https://www.machinelearningplus.com/nlp/training-custom-ner-model-in-spacy/]
- template: https://www.machinelearningplus.com/nlp/training-custom-ner-model-in-spacy/
"""
import os;
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' #! used to hide the Tensofrlow deubing errors [https://stackoverflow.com/questions/35911252/disable-tensorflow-debugging-information]
# Load pre-existing spacy model
import spacy
from spacy.training.example import Example
# Import requirements
import random
from spacy.util import minibatch, compounding
from pathlib import Path


# training data
TRAIN_DATA = [
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


class Build_NER_basic:
  def __init__(self, TRAIN_DATA, language = "english"):
    assert(language == "english"); #! otehrwise, udpate the below:
    nlp=spacy.load('en_core_web_sm')
    # Getting the pipeline component
    ner=nlp.get_pipe("ner")
    # "Each tuple should contain the text and a dictionary. The dictionary should hold the start and end indices of the named enity in the text, and the category or label of the named entity.":
    # Example-data: , ("Walmart is a leading e-commerce company", {"entities": [(0, 7, "ORG")]})

    # Adding labels to the `ner`
    for _, annotations in TRAIN_DATA:
      for ent in annotations.get("entities"):
        # print("add.label=", ent[2]);
        ner.add_label(ent[2])


    #
    #
    self.nlp = nlp;
    self.train(TRAIN_DATA);
  def train(self, TRAIN_DATA):
    #!
    #! "Finally, all of the training is done within the context of the nlp model with disabled pipeline, to prevent the other components from being involved."
    # List of pipes you want to train: Disable pipeline components you dont need to change
    pipe_exceptions = ["ner", "trf_wordpiecer", "trf_tok2vec"]
    # List of pipes which should remain unaffected in training
    unaffected_pipes = [pipe for pipe in self.nlp.pipe_names if pipe not in pipe_exceptions]
    #!
    # TRAINING THE MODEL
    with self.nlp.disable_pipes(*unaffected_pipes):
      # Training for 30 iterations
      for iteration in range(30):
        # shuufling examples  before every iteration <-- tODO: why ensssayr?
        random.shuffle(TRAIN_DATA)
        losses = {}
        # batch up the examples using spaCy's minibatch
        # fXIME: why is algortihm=minibatch used for training?
        batches = minibatch(TRAIN_DATA, size=compounding(4.0, 32.0, 1.001))
        # FIXME: explreo senitty to differnet minibatch configraitions
        #batches = minibatch(TRAIN_DATA, size=compounding(1.0, 4.0, 1.001))
        for batch in batches:
          arr_example = [];
          for text, annot in batch:
            # print(text);
            #texts, annotations = zip(*batch)
            #print("texts=", texts);
            doc = self.nlp.make_doc(text)
            example = Example.from_dict(doc, annot)
            arr_example.append(example);
          # Update the model
          #! "At each word, the update() it makes a prediction. It then consults the annotations to check if the prediction is right. If it isn’t, it adjusts the weights so that the correct action will score higher next time."
          self.nlp.update(arr_example, losses=losses, drop=0.5)
          # FIXME: explroe effect of the bleow permtuatons
          # nlp.update([example], losses=losses, drop=0.3)
          # optimizer = self.nlp.resume_training()
          # self.nlp.update(arr_example, losses=losses,  sgd=optimizer, drop=0.35)

          # nlp.update(
          #             texts,  # batch of texts
          #             annotations,  # batch of annotations
          #             drop=0.5,  # dropout - make it harder to memorise data
          #             losses=losses,
          #         )
          print("Losses", losses)
  def predict(self):
    #!
    #! Step: "Let’s predict on new texts the model has not seen"
    #! - "Training of our NER is complete now. You can test if the ner is now working as you expected. If it’s not up to your expectations, include more training examples and try again.":
    text : str = "I was driving a Alto"
    print("--------------- (tut)\t predicts for text: ", text)
    # Testing the model
    doc = self.nlp(text)
    print("Entities", [(ent.text, ent.label_) for ent in doc.ents])

    # Testing the NER
    test_text = "I ate Sushi yesterday. Maggi is a common fast food "
    doc = self.nlp(test_text)
    print("Entities in '%s'" % test_text)
    for ent in doc.ents:
      print(ent)

    # Save the  model to directory
    filePath_result = "dummyNerTraining/"
    output_dir = Path(filePath_result);
    # Saving the model to the output directory
    self.nlp.meta['name'] = 'nerTraining-dummyData'  # rename model
    if not output_dir.exists():
      output_dir.mkdir()
    self.nlp.to_disk(output_dir)
    print("Saved model to", output_dir)

    # Load the saved model and predict
    print("Loading from", output_dir)
    nlp_updated = spacy.load(output_dir)
    doc = nlp_updated("Fridge can be ordered in FlipKart" )
    print("Entities", [(ent.text, ent.label_) for ent in doc.ents])

    # Getting the ner component
    ner = self.nlp.get_pipe('ner')
    # Resume training
    #optimizer = nlp.resume_training()
    move_names = list(ner.move_names)
    assert nlp_updated.get_pipe("ner").move_names == move_names
    doc2 = nlp_updated(' Dosa is an extremely famous south Indian dish')
    for ent in doc2.ents:
      print(ent.label_, ent.text)


obj_trainNer =  Build_NER_basic(TRAIN_DATA);
obj_trainNer.predict(); #! ie, test the gneraed model



#! ***************************************
#!

# Train NER from a blank spacy model
#import spacy
#nlp=spacy.blank("en") #! Note: other lanauges (than "en") is listed at [https://github.com/explosion/spaCy/tree/master/spacy/lang]
# nlp.add_pipe("ner"); # nlp.create_pipe('ner'))
# nlp.begin_training() #! "You want to avoid calling begin_training() if you've already loaded the model. begin_training() will reinitialize the weights, which isn't what you want." [https://github.com/explosion/spaCy/issues/1978]


assert(False); # FIXME: merge below code-chubnnk with the above ... tehn get working!
assert(False); # FIXME: when thsi is competled, contoue on "tut-1-introductionTo-namedEntityRechognition-ner.py"
