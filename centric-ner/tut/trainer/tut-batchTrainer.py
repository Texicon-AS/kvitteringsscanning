"""!
@file
@brief
@remarks
- demosntraes a case where underitting is the result <-- FIXME: still a rpbolem if a 'non-blank' model is used?
- template: [https://stackoverflow.com/questions/62272190/spacy-blank-ner-model-underfitting-even-when-trained-on-a-large-dataset]
"""
import random
import spacy
from spacy.training import Example # FIXME: write concrete exampels covering this
from spacy.matcher import PhraseMatcher
#nlp = spacy.load("en")
nlp = spacy.load("en_core_web_sm")

import pandas as pd
from tqdm import tqdm

from collections import defaultdict

users_pattern = [nlp(text) for text in ("user", "human", "person", "people", "end user")]
devices_pattern =  [nlp(text) for text in ("device", "peripheral", "appliance", "component", "accesory", "equipment", "machine")]
accounts_pattern = [nlp(text) for text in ("account", "user account", "username", "user name", "loginname", "login name", "screenname", "screen name", "account name")]
identifiers_pattern = [nlp(text) for text in ("attribute", "id", "ID", "code", "ID code")]
authentication_pattern = [nlp(text) for text in ("authentication", "authenticity", "certification", "verification", "attestation", "authenticator", "authenticators")]
time_pattern = [nlp(text) for text in ("time", "date", "moment", "present", "pace", "moment")]
unauthorized_pattern = [nlp(text) for text in ("unauthorized", "illegal", "illegitimate", "pirated", "unapproved", "unjustified", "unofficial")]
disclosure_pattern = [nlp(text) for text in ("disclosure", "acknowledgment", "admission", "exposure", "advertisement", "divulgation")]
network_pattern = [nlp(text) for text in ("network", "net", "networking", "internet", "Internet")]
wireless_pattern = [nlp(text) for text in ("wireless", "wifi", "Wi-Fi", "wireless networking")]
password_pattern = [nlp(text) for text in ("password", "passwords", "passcode", "passphrase")]
configuration_pattern = [nlp(text) for text in ("configuration", "composition")]
signatures_pattern = [nlp(text) for text in ("signature", "signatures", "digital signature", "electronic signature")]
certificates_pattern = [nlp(text) for text in ("certificate", "digital certificates", "authorization certificate", "public key certificates", "PKI", "X509", "X.509")]
revocation_pattern = [nlp(text) for text in ("revocation", "annulment", "cancellation")]
keys_pattern = [nlp(text) for text in ("key", "keys")]
algorithms_pattern = [nlp(text) for text in ("algorithm", "algorithms", "formula", "program")]
standard_pattern = [nlp(text) for text in ("standard", "standards", "specification", "specifications", "norm", "rule", "rules", "RFC")]
invalid_pattern = [nlp(text) for text in ("invalid", "false", "unreasonable", "inoperative")]
access_pattern = [nlp(text) for text in ("access", "connection", "entry", "entrance")]
blocking_pattern = [nlp(text) for text in ("blocking", "block", "blacklist", "blocklist", "close", "cut off", "deter", "prevent", "stop")]
notification_pattern = [nlp(text) for text in ("notification", "notifications", "notice", "warning")]
messages_pattern = [nlp(text) for text in ("message", "messages", "note", "news")]
untrusted_pattern = [nlp(text) for text in ("untrusted", "malicious", "unsafe")]
security_pattern = [nlp(text) for text in ("security", "secure", "securely", "protect", "defend", "guard")]
symmetric_pattern = [nlp(text) for text in ("symmetric", "symmetric crypto")]
asymmetric_pattern = [nlp(text) for text in ("asymmetric", "asymmetric crypto")]

matcher = PhraseMatcher(nlp.vocab)
matcher.add("USER", None, *users_pattern)
matcher.add("DEVICE", None, *devices_pattern)
matcher.add("ACCOUNT", None, *accounts_pattern)
matcher.add("IDENTIFIER", None, *identifiers_pattern)
matcher.add("AUTHENTICATION", None, *authentication_pattern)
matcher.add("TIME", None, *time_pattern)
matcher.add("UNAUTHORIZED", None, *unauthorized_pattern)
matcher.add("DISCLOSURE", None, *disclosure_pattern)
matcher.add("NETWORK", None, *network_pattern)
matcher.add("WIRELESS", None, *wireless_pattern)
matcher.add("PASSWORD", None, *password_pattern)
matcher.add("CONFIGURATION", None, *configuration_pattern)
matcher.add("SIGNATURE", None, *signatures_pattern)
matcher.add("CERTIFICATE", None, *certificates_pattern)
matcher.add("REVOCATION", None, *revocation_pattern)
matcher.add("KEY", None, *keys_pattern)
matcher.add("ALGORITHM", None, *algorithms_pattern)
matcher.add("STANDARD", None, *standard_pattern)
matcher.add("INVALID", None, *invalid_pattern)
matcher.add("ACCESS", None, *access_pattern)
matcher.add("BLOCKING", None, *blocking_pattern)
matcher.add("NOTIFICATION", None, *notification_pattern)
matcher.add("MESSAGE", None, *messages_pattern)
matcher.add("UNTRUSTED", None, *untrusted_pattern)
matcher.add("SECURITY", None, *security_pattern)
matcher.add("SYMMETRIC", None, *symmetric_pattern)
matcher.add("ASYMMETRIC", None, *asymmetric_pattern)

if(True): # FIXME: cosnider removing this block!
  #! After adding all the different patterns to the matcher object, the matcher object is ready for you to make predictions:
  doc = nlp("Attackers can deny service to individual victims, such as by deliberately entering a wrong password enough consecutive times to cause the victims account to be locked, or they may overload the capabilities of a machine or network and block all users at once.")
  matches = matcher(doc)
  for match_id, start, end in matches:
    label = nlp.vocab.strings[match_id]
    span = doc[start:end]
    print(f"label:{label}, start:{start}, end:{end}, text:{span.text}")



# Prepare Training Data

def offsetter(lbl, doc, matchitem):
    """
    Convert PhaseMatcher result to the format required in training (start, end, label)
    """
    o_one = len(str(doc[0:matchitem[1]]))
    subdoc = doc[matchitem[1]:matchitem[2]]
    o_two = o_one + len(str(subdoc))
    return (o_one, o_two, lbl)

#assert(False)
to_train_ents = []
count_dic = defaultdict(int)


# Load the original sentences
fileName_input = "../data/sentences_usedInSpacy_NER_training.csv"; #! note: the data was downlaoded from: https://drive.google.com/file/d/1ZNwVrW4kyXYSEn4-tmZqFfAqRaVM9b56/view
df = pd.read_csv(fileName_input, index_col=False);
phrases = df["sentence"].values
#assert(False)

for line in tqdm(phrases):


  nlp_line = nlp(line)
  matches = matcher(nlp_line)
  if matches:
    for match in matches:
      match_id = match[0]
      start = match[1]
      end = match[2]

      label = nlp.vocab.strings[match_id]  # get the unicode ID, i.e. 'COLOR'
      span = nlp_line[start:end]  # get the matched slice of the doc

      count_dic[label] += 1

      res = [offsetter(label, nlp_line, match)]
      to_train_ents.append((line, dict(entities=res)))

count_dic = dict(count_dic)

TRAIN_DATA =  to_train_ents

# After executing the above code, I obtained the training data in the format required by spaCy. These sentences contain the entities I am interested which are distributed as shown below:
#assert(False)
print(sorted(count_dic.items(), key=lambda x:x[1], reverse=True), len(count_dic))
# sum(count_dic.values())
# [('NETWORK', 1962), ('TIME', 1489), ('USER', 1206), ('SECURITY', 981), ('DEVICE', 884), ('STANDARD', 796), ('ACCESS', 652), ('ALGORITHM', 651), ('MESSAGE', 605), ('KEY', 423), ('IDENTIFIER', 389), ('BLOCKING', 354), ('AUTHENTICATION', 141), ('WIRELESS', 109), ('UNAUTHORIZED', 99), ('CONFIGURATION', 89), ('ACCOUNT', 86), ('UNTRUSTED', 77), ('PASSWORD', 62), ('DISCLOSURE', 58), ('NOTIFICATION', 55), ('INVALID', 44), ('SIGNATURE', 41), ('SYMMETRIC', 23), ('ASYMMETRIC', 11), ('CERTIFICATE', 10), ('REVOCATION', 9)] 27
# 11306
# I then used the standard training procedure to train a blank NER model in spaCy illustrated below.

# Step: Training the Blank model

# define variables
model = None
n_iter = 100

if model is not None:
  nlp_new = spacy.load(model)  # load existing spaCy model
  print("Loaded model '%s'" % model)
  assert(False)
else:
  #nlp_new = spacy.load("en_core_web_sm")
  nlp_new = spacy.blank("en")  # create blank Language class
  #assert(False)
  print("Created blank 'en' model")
#assert(False)
# Add entity recognizer to model if it's not in the pipeline
# nlp.create_pipe works for built-ins that are registered with spaCy
if "ner" not in nlp_new.pipe_names:
  #ner = nlp_new.create_pipe("ner")
  ner = nlp_new.add_pipe("ner")
else: # otherwise, get it, so we can add labels to it
  ner = nlp_new.get_pipe("ner")

print("................: add labels")
# add labels
for _, annotations in TRAIN_DATA:
    for ent in annotations.get("entities"):
        ner.add_label(ent[2])

# get names of other pipes to disable them during training
other_pipes = [pipe for pipe in nlp_new.pipe_names if pipe != "ner"]

print("................: starts the optimizer")
#assert(False)
with nlp_new.disable_pipes(*other_pipes):  # only train NER

    if model is None:
        optimizer = nlp_new.begin_training()
    else:
        optimizer = nlp_new.resume_training()


    # Set this based on this resource: spacy compounding batch size
    sizes = spacy.util.compounding(1, 16, 1.001) #! "This utility function will yield an infinite series of compounding values. Whenever the generator is called, a value is produced by multiplying the previous value by that compound rate" [https://www.tutorialspoint.com/spacy/spacy_util_compounding.htm]
    print("... new iteration")
    # batch up the examples using spaCy's minibatch
    # FIXME: relate this example to our "tut-modelUpdate-ner.py" minmal exampel
    for itn in tqdm(range(n_iter)):
        losses = {}
        random.shuffle(TRAIN_DATA)
        batches = spacy.util.minibatch(TRAIN_DATA, size=sizes)
        arrSamples = []
        #print(f"... \t add the {len(batches)} batches")
        for batchIndex, batch in enumerate(batches):
          if(batchIndex > 1000): # FIXME: idneitfy a better threshold
            break #
          texts, annotations = zip(*batch)
          assert(len(texts) == len(annotations)) # ?? correct?
          for index, text in enumerate(texts): # FIXME: correct?
            arrSamples.append(Example.from_dict(nlp.make_doc(text), annotations[index]))
          nlp_new.update(arrSamples, sgd=optimizer, drop=0.2, losses=losses)
        #nlp_new.update(texts, annotations, sgd=optimizer, drop=0.2, losses=losses)
        print(f"Losses({itn})", losses)
print("................: count-dicts")
#!
# The final loss after this is about 500.
# Finally, I tested how the new model performed using the training data. I would expect to recover as much as entities as specified originally in the training dataset. However, after running the below code I only get about ~600 instances out of ~11k in total.

# Step: Test Trained Model
count_dic = defaultdict(int)
for text, _ in TRAIN_DATA:
    doc = nlp_new(text)
    for ent in doc.ents:
        count_dic[ent.label_] += 1

print(sorted(count_dic.items(), key=lambda x:x[1], reverse=True), len(count_dic))
#sum(count_dic.values())

# [('TIME', 369), ('NETWORK', 47), ('IDENTIFIER', 41), ('BLOCKING', 28), ('USER', 22), ('STANDARD', 22), ('SECURITY', 15), ('MESSAGE', 15), ('ACCESS', 7), ('CONFIGURATION', 7), ('DEVICE', 7), ('KEY', 4), ('ALGORITHM', 3), ('SYMMETRIC', 2), ('UNAUTHORIZED', 2), ('SIGNATURE', 2), ('WIRELESS', 1), ('DISCLOSURE', 1), ('INVALID', 1), ('PASSWORD', 1), ('NOTIFICATION', 1)] 21
# 598

# eval: I wonder why this procedure is producing a model with such underfitting behavior. I am aware of the comments in these posts: NER training using Spacy and SPACY custom NER is not returning any entity but they do not address my issue.

# eval: I hope you can provide any feedback about what I have done and how I can improve detection of entities in the training set. I thought that 11k sentences would be enough unless I am doing something wrong. I am using Python 3.6.9 and spaCy 2.2.4.
