#!/usr/bin/bash

# ------------------
# Task: Install dependencies
# ------------------
python3 -m pip install requirements.txt
python3 -m spacy download en_core_web_sm
python3 -m spacy download nb_core_news_sm
python3 -m spacy download nb_core_news_lg
python3 -m spacy download en_core_web_lg

python3 -c "import nltk ; nltk.download('stopwords')"
python3 -c "import nltk ; nltk.download('punkt_tab')"
