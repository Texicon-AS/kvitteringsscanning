# Case: Food-company

## Install
### Download language models
```bash
python3 -m spacy download en_core_web_sm;
# FIXME: the below now fails ... instead, use "nb_core_news_sm"? <-- https://spacy.io/models/nb
#python3 -m spacy download nb_core_web_sm; #! []
python3 -m spacy download nb_core_news_sm; #! []
```

## Example-code:
```bash
#! a basic example on how using pattern matching for NER-classification:
python3 src/normalize/tut-enumerateMatches.py # a hellow-world example
python3 ./src/normalize/tut-spacy-pattern-3.py

#! Code making use of our internal logics:
python3 src/normalize/nlp_findNumbersInText.py #! ....
python3 src/configure/e_experience.py
python3 src/normalize/compareTo_definitions.py #! which uses our model-training to classify the text
```

##