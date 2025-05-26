"""
@file
@brief
@remarks
- template: https://support.prodi.gy/t/working-with-languages-not-yet-supported-by-spacy/206
"""
from spacy.lang.nb import Norwegian
nlp = Norwegian()  # alternatively: nlp = spacy.blank('nb')
# FIXME: identify a use-case for this example ... then update ?? ... <-- eg, relate to "tut-lemmatizeNorwegian.py"
#nlp.to_disk('/path/to/nb-model')
nlp.to_disk('tmp-nb-model')
