"""
@file
@brief a basic exampel of stop-word fitlering
@remarks this example is based on:
- https://stackoverflow.com/questions/68010465/how-to-remove-stop-words-and-lemmatize-at-the-same-time-when-using-spacy
- https://stackoverflow.com/questions/68010465/how-to-remove-stop-words-and-lemmatize-at-the-same-time-when-using-spacy
@todo use this to update our "PredictedProduct.py"
"""
from typing import List, Union, Any
from dataclasses import dataclass, field
import spacy
# TODO: correct to sue both NLTK and spacy?
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

@dataclass
class StopWordRemoval:
    """
    @brief
    @remarks
    """
    arrNlp : List[spacy.lang] = field(default_factory = lambda : [
        spacy.load("en_core_web_sm"),
        spacy.load("nb_core_news_lg"), #! [https://spacy.io/models/nb]
    ])
    arrNltkStopWords : List[Any] = field(default_factory = lambda : [
        stopwords.words('english'),
        stopwords.words('norwegian'),
    ])

    def __post_init__(self):
        # FIXME: suggestions for where to get a list of product-component-pasudo-.stopwrods to use/add?
        pass # nlp.Defaults.stop_words.add("friend") # Adding "friend" to stopword list


    def __spacyApproach(self, text : Union[str, List[str]], treatAsLowerCase : bool = True) -> List[str]:
        assert(treatAsLowerCase) #! as we otehrsise needs adjsuting the below
        assert(treatAsLowerCase) #! as we otehrsise needs adjsuting the below
        if(isinstance(text, str)):
            arrInput : List[str] = [text.lower()]
        else:
            arrInput : List[str] = []
            for word in text:
                arrInput.append(word.lower())
        arrResult : List[str] = []
        for word in arrInput:
            wordWasAdded = False
            for nlp in self.arrNlp:
                if(wordWasAdded):
                    continue
                for token in nlp(word):
                    if token.lemma_.lower() not in map(str.lower, nlp.Defaults.stop_words): # and token.is_alpha # FIXME: when shoudl teh latter "is_alpha" critiera be used?
                        wordWasAdded = True # TODO: correct ... as we did not add for allt he 'lemma' in the word?
                        arrResult.append(token.lemma_)
        return arrResult

    def __nltkFilter(self, text : str, treatAsLowerCase : bool = True) -> List[str]:
        #! Join the stop-wrod list <-- TODO: cases where this woudl be inaccurate?
        multiLangStopWords = set()
        for stopWords in self.arrNltkStopWords:
            [multiLangStopWords.add(_) for _ in set(stopWords)]

        wordTokens = word_tokenize(text)
        arrFilteredText = [w for w in wordTokens if not w.lower() in multiLangStopWords]
        return arrFilteredText

    def predict(self, text : Union[str, List[str]], treatAsLowerCase : bool = True) -> List[str]:
        """
        @brief
        @return
        """
        # TODO: any point in using both appraoches? <-- if not, which to choose?
        arrResult = self.__spacyApproach(text, treatAsLowerCase)
        arrResult = self.__nltkFilter(" ".join(arrResult), treatAsLowerCase)
        return arrResult

if __name__ == "__main__":
    """
    @brief
    @remarks
    """
    stopRemoval = StopWordRemoval()
    text = "I have a lot of friends"
    result = stopRemoval.predict(text)
    print(f"input({text}) => {result}")
