"""!
@brief provides a basic introdution to "Named Entity Rechongiion" (NER)
@remarks clseoly related TUT-examples:
- "tut-3-ner-training.py": exmaplefies the sue fo a acic model-trainer
@remarks
- tempaltes:
- API: https://spacy.io/api/top-level
* baiscs: [https://www.machinelearningplus.com/spacy-tutorial-nlp/]
* algorithm-traning: https://newscatcherapi.com/blog/train-custom-named-entity-recognition-ner-model-with-spacy-v3
* custom-lanauge: "Every language is different – and usually full of exceptions and special cases, especially amongst the most common words. Some of these exceptions are shared across languages, while others are entirely specific – usually so specific that they need to be hard-coded. The lang module contains all language-specific data, organized in simple Python files. This makes the data easy to update and extend." [https://spacy.io/usage/linguistic-features#language-data]
@remarks notation
* a token: "Tokens are individual text entities that make up the text. Typically a token can be the words, punctuation, spaces, etc."
* tokenization: "Tokenization is the process of converting a text into smaller sub-texts, based on certain predefined rules. For example, sentences are tokenized to words (and punctuation optionally). And paragraphs into sentences, depending on the context. This is typically the first step for NLP tasks like text classification, sentiment analysis, etc. Each token in spacy has different attributes that tell us a great deal of information."
* stop-words: "Stop words and punctuation usually (not always) don’t add value to the meaning of the text and can potentially impact the outcome. To avoid this, its might make sense to remove them and clean the text of unwanted characters can reduce the size of the corpus."
* lemmatization: "Lemmatization is the method of converting a token to it’s root/base form.".
* Lemmatization (Motvation): "Have a look at these words: “played”, “playing”, “plays”, “play”. These words are not entirely unique, as they all basically refer to the root word: “play”. Very often, while trying to interpret the meaning of the text using NLP, you will be concerned about the root meaning and not the tense. For algorithms that work based on the number of occurrences of the words, having multiple forms of the same word will reduce the number of counts for the root word, which is ‘play’ in this case. Hence, counting “played” and “playing” as different tokens will not help."
- "part of speach analsysis" (POS-analysis): "Consider a sentence , “Emily likes playing football”. Here , Emily is a NOUN , and playing is a VERB. Likewise , each word of a text is either a noun, pronoun, verb, conjection, etc. These tags are called as Part of Speech tags (POS)."
"""
import os;
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' #! used to hide the Tensofrlow deubing errors [https://stackoverflow.com/questions/35911252/disable-tensorflow-debugging-information]
import spacy

#nlp = spacy.load("en_core_web_lg")
#!
#! SubStep: download the nessary model:
cmd = "python3 -m spacy download en_core_web_sm " #! [https://stackoverflow.com/questions/67733747/cant-find-model-en-core-web-lg-it-doesnt-seem-to-be-a-shortcut-link-a-pyth]
#cmd = "python3 -m spacy download en_core_web_lg " #! [https://stackoverflow.com/questions/67733747/cant-find-model-en-core-web-lg-it-doesnt-seem-to-be-a-shortcut-link-a-pyth]
nlp = spacy.load("en_core_web_sm")
text = "What video sharing service did Steve Chen, Chad Hurley, and Jawed Karim create in 2005?"
doc = nlp(text)

print(nlp.pipe_names) # FIXME: how to use pipe="ner"?
#from spacy import displacy
#displacy.render(doc, style="ent", jupyter=True)

import json

filePath = "../data/Corona2.json"; # FIXME: what classes can we use for generiting a similar file (with pos-annoations based on where the entires were found)? <-- what mdoficaionts to introdue to our NGRAM-BagOfWords approach (for supporitng this requiement)?
with open(filePath, 'r') as f:
  data = json.load(f)
print(data['examples'][0])

# FIXME: can below procedure be directy rewrittien using oiru nrosiaotn-vecotr-strategy? <- what changes are needed?
training_data = {'classes' : ['MEDICINE', "MEDICALCONDITION", "PATHOGEN"], 'annotations' : []}
for example in data['examples']:
  temp_dict = {}
  temp_dict['text'] = example['content']; #! ie, the text to train the NER-model on?
  #print("\t\t- ", example);
  #print("\t\t- ", example["content"]);
  temp_dict['entities'] = []
  for annotation in example['annotations']:
    assert(annotation["value"] in example["content"]); #! ie, that the given term (= synonym-mapping?) is found in the input-text
    #print("\t\t- ", annotation);
    start = annotation['start']
    end = annotation['end']
    label = annotation['tag_name'].upper()
    temp_dict['entities'].append((start, end, label))
  training_data['annotations'].append(temp_dict)

print(training_data['annotations'][0])

#!
#! Step: convert the training to the correct format: "spaCy uses DocBin class for annotated data, so we’ll have to create the DocBin objects for our training examples. This DocBin class efficiently serializes the information from a collection of Doc objects. It is faster and produces smaller data sizes than pickle, and allows the user to deserialize without executing arbitrary Python code.":
import spacy
from spacy.tokens import DocBin
from tqdm import tqdm
#! Note: other lanauges (than "en") is listed at [https://github.com/explosion/spaCy/tree/master/spacy/lang]
nlp = spacy.blank("en") # load a new spacy model [https://github.com/explosion/spaCy/blob/320a8b14814c7e0c6dce705ad7bf0f13bf64b61c/spacy/__init__.py#L33]
# FIXME: instead of the above, try: nlp = spacy.load("en_core_web_sm", disable = ['ner']) <-- backgorund: "If the only thing you are changing is NER, I would start with the pre-trained model (I assume English), and just disable NER pipe" [https://stackoverflow.com/questions/64724483/what-is-the-underlying-architecture-of-spacys-blank-model-spacy-blanken]
# FIXME: compare the use of "blank(..)" to altneraitve stategies: "Underfitting may be due the fact that spacy blank models are too small to perform well in your situation. In my experience spacy blank models are about 5Mb which is small (especially if we compare it with the size of spacy pretrained models that can be around 500 Mb)" [https://stackoverflow.com/questions/62272190/spacy-blank-ner-model-underfitting-even-when-trained-on-a-large-dataset]


doc_bin = DocBin() # create a DocBin object
#
#! Step: resolve isseus related to overlaps: "There are some entity span overlaps, i.e., the indices of some entities overlap. spaCy provides a utility method filter_spans to deal with this. ":
# FIXME: in the traning we use all the inptu-data? ... if eys, then how is the model trained? ... does it use a larger dataset (than what we ahve provided)? ...
from spacy.util import filter_spans
for training_example  in tqdm(training_data['annotations']):
    text = training_example['text']
    labels = training_example['entities']
    doc = nlp.make_doc(text)
    ents = []
    for start, end, label in labels:
        span = doc.char_span(start, end, label=label, alignment_mode="contract")
        if span is None:
            print("Skipping entity")
        else:
            ents.append(span)
    filtered_ents = filter_spans(ents)
    doc.ents = filtered_ents
    doc_bin.add(doc)

fileName_dataModel_forTraining = "training_data.spacy"
doc_bin.to_disk(fileName_dataModel_forTraining) # save the docbin object
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
#vectors = "en_core_web_lg"
vectors = "en_core_web_sm"
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
@architectures = "spacy.Tok2Vec.v2"

[components.tok2vec.model.embed]
@architectures = "spacy.MultiHashEmbed.v2"
width = ${components.tok2vec.model.encode.width}
attrs = ["NORM", "PREFIX", "SUFFIX", "SHAPE"]
rows = [5000, 1000, 2500, 2500]
include_static_vectors = true

[components.tok2vec.model.encode]
@architectures = "spacy.MaxoutWindowEncoder.v2"
width = 256
depth = 8
window_size = 1
maxout_pieces = 3

[components.ner]
factory = "ner"

[components.ner.model]
@architectures = "spacy.TransitionBasedParser.v2"
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
#vectors = "nb_core_news_lg"
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
@architectures = "spacy.Tok2Vec.v2"

[components.tok2vec.model.embed]
@architectures = "spacy.MultiHashEmbed.v2"
width = ${components.tok2vec.model.encode.width}
attrs = ["NORM", "PREFIX", "SUFFIX", "SHAPE"]
rows = [5000, 1000, 2500, 2500]
include_static_vectors = true

[components.tok2vec.model.encode]
@architectures = "spacy.MaxoutWindowEncoder.v2"
width = 256
depth = 8
window_size = 1
maxout_pieces = 3

[components.ner]
factory = "ner"

[components.ner.model]
@architectures = "spacy.TransitionBasedParser.v2"
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
#import tempfile
str_config = str_config_en; #! ie, the choise donfig
fileNameConfig = "spacy_config.cfg";
f = open(fileNameConfig, "w")
f.write(str_config);
f.close()
#!
#! Step: train our model:
import subprocess
def applyCmd(cmd):
  try:
    result = subprocess.check_output(
      #arr_cmdToCall,
      cmd,
      stderr=subprocess.STDOUT, shell=True, timeout=60*10*4,
      universal_newlines=True)
  except subprocess.CalledProcessError as exc:
    print("!!\t [tut] operation failed");
    print("-\t reproduce: run: \"{}\"\t({})".format(cmd, __file__));
    print("-\tRaw Error Details : FAIL", exc.returncode, exc.output)
    return False;
  else: # FIXME: when is this "else" clause triggeered?
    print("Output from \"{}\": \n{}\n".format(cmd, result))
    print("\t OK: the \"{}\" worked.".format(cmd));
  return True;

fileName_result = "spacy.configAfterTuning.cfg";
cmd = f"python3 -m spacy init fill-config {fileNameConfig} {fileName_result}"
#cmd = f"python3 -m spacy init fill-config base_config.cfg {fileNameConfig}"
is_ok = applyCmd(cmd );
assert(is_ok);
#cmd = f"python -m spacy init fill-config base_config.cfg config.cfg"

is_ok = applyCmd(cmd );
assert(is_ok);



#!
#! Step: use the trained model:
#cmd = f"python3 -m spacy train config.cfg --output ./ --paths.train ./training_data.spacy --paths.dev ./training_data.spacy --gpu-id 0";
#cmd = f"python3 -m spacy train {fileName_result} --output ./ --paths.train {fileName_dataModel_forTraining} --paths.dev  {fileName_dataModel_forTraining} --gpu-id 0";
cmd = f"python3 -m spacy train {fileName_result} --output ./ --paths.train {fileName_dataModel_forTraining} --paths.dev  {fileName_dataModel_forTraining}";
is_ok = applyCmd(cmd );
assert(is_ok);



#!
#! Step: load the generated model:
nameOf_newModel = "model-best"; # FIXME: ?? why si this the above gnerated modle? is it?
nlp_ner = spacy.load(nameOf_newModel);


doc = nlp_ner("Antiretroviral therapy (ART) is recommended for all HIV-infected\
individuals to reduce the risk of disease progression.\nART also is recommended \
for HIV-infected individuals for the prevention of transmission of HIV.\nPatients \
starting ART should be willing and able to commit to treatment and understand the\
benefits and risks of therapy and the importance of adherence. Patients may choose\
to postpone therapy, and providers, on a case-by-case basis, may elect to defer\
therapy on the basis of clinical and/or psychosocial factors.")

colors = {"PATHOGEN": "#F67DE3", "MEDICINE": "#7DF6D9", "MEDICALCONDITION":"#FFFFFF"}
options = {"colors": colors}
spacy.displacy.render(doc, style="ent", options= options, jupyter=False)
