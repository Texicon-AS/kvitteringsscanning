import os
import sys
import spacy
from spacy.matcher import PhraseMatcher
from classification import DatasetBuilder
import time
from rich.progress import Progress
import logging

def get_output_function(is_verbose: bool):
    """
    Returns either print function or appropiate logging function based on verbosity.
    """

    if verbose:
        return print

    logging.basicConfig(filename="python_output.log", level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger()
    return logger.info


if __name__ == "__main__":
    srcPath = os.getcwd() 
    modelPath =  "./trainer/centricFoodModel_nb"
    verbose = True
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg == "-s":
            verbose = False
        if sys.argv[2] == "-m":
            srcPath = sys.argv[3]
            modelPath = os.path.join(srcPath ,"src", "trainer","centricFoodModel_nb")

    log = get_output_function(verbose)
    start = time.time()
    # Load Model
    nlp = spacy.load(modelPath)
    end = time.time()
    log(f"Loaded language model in {end - start:.4f} seconds")
    # Load Prediction files.
    ourMatcher = PhraseMatcher(nlp.vocab)
    phraseData = DatasetBuilder.fastLoad(srcPath)
    if verbose:
        lenData = len(phraseData.keys())
        log(f"Loading phrases : {lenData}")
        with Progress() as progress:
            task = progress.add_task("[cyan]Loading phrases", total=lenData)

            name = ""
            patterns = ""
            try:
                for (name,groupsofFood) in phraseData.items():
                    patterns = [nlp.make_doc(food) for food in groupsofFood]
                    ourMatcher.add(name,patterns)

                    progress.update(task, advance=1)
            except Exception as e:
                log(f"Error adding patterns for {name }: {e}")
                log(f"Failed patterns: {patterns}")
                exit(-1)

            end = time.time()
        log(f"Loaded phraseData into the model in {end - start:.4f} seconds")
    else:
       for (name,groupsofFood) in phraseData.items():
           patterns = [nlp.make_doc(food) for food in groupsofFood]
           ourMatcher.add(name,patterns)

    # When ready listen for sys.stdin:
    log("listening to stdin!")
    for line in sys.stdin:
        log(f"line being read {line.strip()}")
        doc = nlp(line.strip())
        matches = ourMatcher(doc)
        matchedDict = {}
        returnString = ""
        if matches:
            for match_id, start, end in matches:
                match_id_str = nlp.vocab.strings[match_id]
                phrase = doc[start:end].text
                if phrase not in matchedDict:
                    matchedDict[phrase] = [match_id_str]
                else:
                    matchedDict[phrase].append(match_id_str)
        if len(matchedDict) > 0:
            longestKey = max(matchedDict, key=len)
            returnString += f"Ingredient: {longestKey} | Groups: {matchedDict[longestKey]} "
        else:
            returnString += f"Ingredient: NOT_FOUND | Groups: NOT_FOUND"
        entString = ""
        for ent in doc.ents:
            entString += f"{ent}"
            log(f"Ents are {ent}")
        if entString == "":
            entString = "NOT_FOUND"
        returnString += f"| Quantity: {entString}"
        log(f"returnString is {returnString}")
        print(returnString)
        sys.stdout.flush()
