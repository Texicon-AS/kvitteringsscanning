import spacy
from spacy.language import Language
from spacy import displacy
from spacy.util import filter_spans; # FIXME: what is the fecct of this
#from spacy.tokens import DocBin
#from spacy.tokens import Span
import pathlib;
import os;

# nlp = spacy.load("en_core_web_sm")
# @Language.component("extract_person_orgs")
# def extract_person_orgs(doc):
#   person_entities = [ent for ent in doc.ents if ent.label_ == "PERSON"]
#   for ent in person_entities:
#     head = ent.root.head
#     if head.lemma_ == "work":
#       preps = [token for token in head.children if token.dep_ == "prep"]
#       for prep in preps:
#         orgs = [token for token in prep.children if token.ent_type_ == "ORG"]
#         print({'person': ent, 'orgs': orgs, 'past': head.tag_ == "VBD"})
#   return doc

# # To make the entities easier to work with, we'll merge them into single tokens
# nlp.add_pipe("merge_entities")
# nlp.add_pipe("extract_person_orgs")

# doc = nlp("Alex Smith worked at Acme Corp Inc.")
# #displacy.serve(doc, options={"fine_grained": True})
# displacy.serve(doc, options={"fine_grained": True})
import spacy
from spacy import displacy
from spacy.matcher import Matcher

#nlp = spacy.load("en_core_web_sm")
#nlp = spacy.load("nb_core_news_sm")
#nlp = spacy.load("en_core_news_lg") #! as it seems likke "en_core_web_lg" is no longer avialble
nlp = spacy.load("en_core_web_lg") #! ie, a larger model than "en_core_web_sm" [https://github.com/Cristianasp/spacy/blob/master/Chapter_02.ipynb] <-- eval: how does htis affect the eprcomen? <-- install: python -m spacy download en_core_web_lg
#nlp = spacy.load("nb_core_news_lg")
matcher = Matcher(nlp.vocab)
arr_matches = []  # Collect data of matched sentences to be visualized

def __collect_sents(label, matcher, doc, i, matches):
  #print("matcher==", matcher.vocab);
  #help(matcher);
  #assert(False);
  match_id, start, end = matches[i]
  print("... ", nlp.vocab.strings[match_id]);
  #print("label=", matcher.label);
  #print("label=", matcher.label);
  span = doc[start:end]  # Matched span
  sent = span.sent  # Sentence containing matched span
  # Append mock entity for match in displaCy style to arr_matches
  # get the match span by ofsetting the start and end of the span with the
  # start and end of the sentence in the doc
  print("\t(match)", sent.text, "; subset=", span.text);
  #!
  start = span.start_char - sent.start_char;
  end   = span.end_char - sent.start_char;
  #!
  match_ents = [{
    "start": start,
    "end": end,
    "label": label,
  }]
  #!
  #! Test if text already contains a match:
  for obj in arr_matches:
    if(obj["text"] == sent.text): # FIXME: for the below ... why is the text concantedna muliple tiems (in the results)? <-- to symbolzie pattern-voerlaps (ie, an idneited=meanigufl feature)?
      isExtended = False;
      for o in obj["ents"]:
        prev = [o["start"], o["end"]];
        if( (start < prev[0]) or (end > prev[1])):
          isExtended = True;
      if(isExtended):
        obj["ents"] += match_ents; #! ie, then extend exiintg
      #!
      #assert(False);
      return;
  arr_matches.append({"text": sent.text, "ents": match_ents})
  #if(arr_matches_doc != None):
  #doc = nlp.make_doc(word)   #! Note: documetnation for class="doc" is found at [https://spacy.io/api/doc]

def __entryOf_db(matcher, doc, i, matches):
  return __collect_sents("database", matcher, doc, i, matches)
def __entryOf_years(matcher, doc, i, matches):
  return __collect_sents("MATCH", matcher, doc, i, matches)

arr_patterns = []
pattern = [
  {"LOWER": "databases"}, {"LEMMA": "be"}, {"POS": "ADV", "OP": "*"}, {"POS": "ADJ"}
]
arr_patterns.append(pattern);
matcher.add("DatabaseIs", arr_patterns, on_match=__entryOf_db)  # add pattern
#!
#! Clear:
arr_patterns = [];
#!

# """
# class Pattern:
#   def __init__(self, arr_entries):
#     self.arr_data = [];
#     assert(isinstance(arr_entries, list));
#     for obj in arr_entries:
#       if(isinstance(obj, E_TYPE_NUMBER)):

#         for obj in arr_entries:
#       assert(isinstance(obj, dict));
#   def __list__(self):
#     return self.arr_data;
# class PatternArr:
#   def __init__(self):
#     self.arr_data = [];

#   def __list__(self):
#     arr_result = []
#     assert(len(self.arr_data) > 0);
#     for obj_entry in self.arr_data:
#       res = list(obj_entry);
#       for obj in res:
#       assert(isinstance(obj, list):
#       assert(res != None);
#       assert(isinstance(res, list));
#       arr_result.append(res)
#     return arr_result;
#   def append(self, obj_pattern):
#     assert(isinstance(obj_pattern, Pattern));
#     self.arr_data.append(obj_pattern);
# """



#!
# pattern = [ #! Example: For this position, we are also looking for:. 2-5 years’ relevant experience and IT academic background.
#   #{ "POS" : "NUM"},#! eg, "2"
#   { "LIKE_NUM" : True},#! eg, "2"
#   { "POS" : "SYM"},#! eg, "-"
#   { "LIKE_NUM" : True},#! eg, "5"
#   #{ "POS" : "NUM"},#! eg, "5"
#   { "POS" : "NOUN"},#! eg, "years"
#   { "POS" : "PART"},#! eg, "’"
#   { "POS" : "ADJ"},#! eg, "relevant"
#   { "POS" : "NOUN"},#! eg, "experience"
# ]
#arr_patterns.append(pattern);
#
arr_numbers_no = ["null", "en", "to",   "tre",    "fire", "fem", "seks", "syv", "åtte", "ni", "ti"]
subPattern_number = { "LEMMA" : {"IN" : arr_numbers_no} };
#arr_patterns.append([{ "LIKE_NUM" : True}]);
#arr_patterns.append([{ "LIKE_NUM" : True}, {"LOWER" : "-"}, { "LIKE_NUM" : True}]);
arr_suffix_always = ["years of experience"]
arr_lookAHead1 = ["år", "års", "year", "years", "years’"]
arr_lookAHead2_not = ["we", "us", "vi", "utdanning", "utdannelse", "education", "higher", "høyere"]
#arr_lookAHead2 =

# FIXME: what is the effect of the below pattern? <- note: dropped ... as this would result a loss of: "For å lykkes hos oss tror vi du. har høyere utdanning, gjerne på Masternivå og 5-10 års erfaring MATCH innen informasjonssikkerhet (fortrinnsvis fra roller som CISO, sikkerhetsarkitekt eller, konsulent/rådgiver)"
#arr_prefix = [None, ["erfaring", "års", "minst", "min.", "minimum", "looking for", "or more years of experience", "experience", "har over"]];
#arr_patterns.append([{ "LIKE_NUM" : True}, {"LOWER" : "-"}, { "LIKE_NUM" : True}, {}, {"LEMMA" : { "IN" : arr_suffix_always }}]);
#arr_patterns.append([ {"LEMMA" : { "IN" : arr_lookAHead1} }, {"LEMMA" : { "NOT_IN" : arr_lookAHead2_not} } ]); #! where "{}" is a wild-card
for part1 in [
    [{ "LIKE_NUM" : True}, {"LOWER" : "-"}],
    [],
]:
  for part2 in [
      [{ "LIKE_NUM" : True}]
  ]:
    for part3 in [
        [ {"LEMMA" : { "IN" : arr_lookAHead1} }, {"LEMMA" : { "NOT_IN" : arr_lookAHead2_not} } ],
        [{}, {"LEMMA" : { "IN" : arr_suffix_always }}],
    ]:
      arr_patterns.append(part1 + part2 + part3);


#arr_patterns.append([{ "LIKE_NUM" : True}, {"LOWER" : "-"}, { "LIKE_NUM" : True}, ]); #! where "{}" is a wild-card
#arr_patterns.append([{ "LIKE_NUM" : True}, {}, { "LIKE_NUM" : True}]); #! where "{}" is a wild-card
#arr_patterns.append([subPattern_number, {}, subPattern_number])

#! ----------
#!
#! Step: extend above, adding new matches for cases where there is a number-pattern
#! Note: motviaotn is to reduce the bloat in entries
# FIXME: try exiting the blewo with addional pattern-overlaps
arr_newPatterns = []
for subPattern in arr_patterns:
  assert(isinstance(subPattern, list));
  holdsA_number = False;
  for obj  in subPattern:
    if("LIKE_NUM" in obj):
      holdsA_number = True;
  if(holdsA_number == False):
    continue;
  arr_new = [];
  for obj  in subPattern:
    if("LIKE_NUM" in obj):
      arr_new.append(subPattern_number);
    else:
      arr_new.append(obj);
  arr_newPatterns.append(arr_new);
arr_patterns += arr_newPatterns;
#! ----------



#!
#! Step:
matcher.add("NumberRange", arr_patterns, on_match=__entryOf_years)  # add pattern


#arr_matches_doc = []
#!
#! Apply:
print("[tut-spacy-pattern-3.py]\t The noun-chunks in our tranning-ensabmle")
for word in [
    "Databases are interesting, though databases are not always easy to use",
    "Work related to Databases. For this position, we are also looking for:. 2-5 years’ relevant experience and IT academic background.",
    "For this position, we are also looking for:. two-five years’ relevant experience and IT academic background.",
    "For this position, we are also looking for:. to-fem years’ relevant experience and IT academic background.",
    "M.Sc / B.Sc med 2-5 års erfaring fra Telecom/Nettverksløsninger", "Vi ønsker at du allerede har 2-5 års erfaring, enten fra lignende stilling, eller fra operativt lønns- eller IT-arbeid.", "Du har minimum 2-5 års erfaring med Onsite IT Supportoppgaver.", "Teknisk utdanning (Bachelor/teknisk fagskole), men 2-3 års relevant erfaring kan erstatte formelle krav.", "Minimum 2-3 års arbeidserfaring, gjerne innen service eller andre relevante områder.", "For this position, we are also looking for:. 2-5 years’ relevant experience and IT academic background.", "With 2-10 years experience but recent graduates will be considered", " For å lykkes hos oss tror vi du. har høyere utdanning, gjerne på Masternivå og 5-10 års erfaring innen informasjonssikkerhet (fortrinnsvis fra roller som CISO, sikkerhetsarkitekt eller, konsulent/rådgiver).", "Preferably 5-10 or more years of experience with project work, but less experienced are encouraged to apply if this is something you are passionate about.", "0-10 års relevant erfaring.", "You have preferably 0-10 years of experience with project work, service or operations; new graduates are welcome to apply.", "You have preferably 0-10 years of experience with project work, service or operations; new graduates are welcome to apply.", "0-10 års relevant erfaring",
      "Minimum 2 års erfaring", "Bør ha minst fem års erfaring som utvikler.", "Minst fem års relevant erfaring", "Høyere utdannelse innen IT og minst fem års relevant erfaring.", "Minimum fem års erfaring med relevante arbeidsoppgaver. Flytende norsk skriftlig og muntlig", "Som seniorutvikler har du flere års erfaring med programvareutvikling", "Minimum 5 års praksis som Delivery Manager innen utvikling - og tekologileveranser.", "Minimum 2 års erfaring med kvalitetssikring innen IT-prosjekter.", "Minimum 2 års erfaring som utvikler.", "Minimum 1-2 års års relevant arbeidserfaring innen frontend utvikling.",  "Minimum 2 års relevant erfaring.", " Minimum 2 års erfaring med kvalitetssikring innen IT-prosjekter.", "Minimum 3 års erfaring fra tilsvarende oppgaver. ", "Minimum 5 års erfaring med backend (eksempelvis dotnet, C# og/eller Java, Spring) eller fullstack. ",  "Minimum tre års relevant arbeidserfaring som utvikler.", " Minimum ti års relevant erfaring.", "Minimum 5 års praksis som Delivery Manager innen utvikling - og teknologileveranser.", " Minimum tre års arbeidserfaring innen relevant fagområde.", "Minimum 3 års relevant erfaring.", "Minimum 2-3 års relevant arbeidserfaring, gjerne fra arbeid som omfatter tjenesteutvikling.", "Har minimum 2-4 års erfaring innenfor flere av følgende teknologier og rammeverk", "Har minimum 2-4 års erfaring innenfor flere av følgende teknologier og rammeverk", "Har minimum 2-4 års erfaring innenfor flere av følgende teknologier og rammeverk",
      #!
      #!
      "Vi ser etter en testleder med noen års erfaring innen testledelse og test av IKT-løsninger, og som motiveres av å jobbe med tjenester som gir stor nytteverdi for helsetjenesten.",
      "Fortrinnsvis noen års erfaring fra lignende arbeid, men nyutdannede er også velkommen til å søke. God digital kompetanse og interesse for digital utvikling.",
      "Vi ser etter deg som har noen års erfaring med utvikling av infrastruktur og komplekse løsninger.",
      "Noen års erfaring fra digital produkt- og tjenesteutvikling.",
      "Videre er det fordelaktig at du er/har:. Noen års erfaring med back-end .NET utvikling, herunder C, C++, C# osv.",
      "Du har noen års erfaring fra moderne utviklingsprosjekter der du har vært involvert i ulike deler av leveransene og du har interesse for et bredt sett av fagfelt (fullstack/backend). Vi tror de rette kandidatene kan kjenne seg igjen i følgende:. Høyere relevant utdanning og noen års arbeidserfaring som utvikler. ",
      "Du liker å programmere, har god teknisk forståelse og noen års erfaring som utvikler.",
      "Du må ha noen års erfaring med utvikling og arkitektur,",
      "Du må ha noen års erfaring med utvikling eller arkitektur, gjerne som løsningsarkitekt eller systemarkitekt, herunder relevant erfaring med. prinsipper for IT-arkitektur og metodeverk.",
      "Vi ønsker at du har noen års erfaring med solid kompetanse på en eller flere tjenester innenfor Microsoft 365-porteføljen. ",
      "Vi ser etter deg som har noen års erfaring fra nettverk, brannmur og virtualiserte miljøer.",
      "Vi leter etter deg som har noen års erfaring og ønsker å jobbe in-house med å løse kompliserte tekniske problemer. ",
      "For å lykkes i rollen tror vi at du kjenner deg igjen i noen av disse punktene:. Noen års erfaring som fullstack utvikler. ",
      "Det er et pluss om du har noen års relevant arbeidserfaring, men det ikke et krav.               ",
      "Noen års relevant arbeidserfaring og/eller kunnskap tilegnet fra endre arenaer er fordelaktig.               ",
      "Det ønskes noen års jobberfaring, men nyutdannede oppfordres også til å søke. ",
      "Du er en utvikler med noen års erfaring, som kan ta valg på vegne av eller sammen med teamet. Du er en fremoverlent lagspiller som må kunne diskutere tekniske løsninger med både tekniske og ikke-tekniske personer. Du liker å ta ansvar, og setter pris på at du får være med å bestemme.",
      "Egenskaper du bør ha:. Noen års erfaring som utvikler. Kjennskap til en eller flere skyplatformer. Erfaring med Docker og containere. ",
      "Om du sitter på noen års erfaring med iOS-plattformen, er det supert. Er du fersk, men har et høyt engasjement og et stort talent, er det også interessant.               ",
      "Det er et pluss om du har noen års relevant arbeidserfaring, men det ikke et krav.",
      "Du har noen års erfaring innen drift, IT-systemer og infrastruktur, og vi tror den rette kandidaten viser nysgjerrighet ovenfor nye områder og har en brennende interesse for IT. Det er en bonus om du kjenner til ITIL prosesser. ",
      "Vi ser etter deg som har noen års erfaring, vilje og tyngde til å ta ansvar for deler av vår, etter hvert ganske omfattende, portefølje av tekniske applikasjoner. Du har god kjennskap til teknologistacken vår og liker å spille på lag. ",
      "Vi tror du har:. Noen års erfaring som utvikler.",
      "Teknisk fagskole / Bachelor innen automasjon med noen års jobberfaring. Erfaring innen bygg automasjon, smarthus, IoT- internet of things.               ",
      "Selv om du kommer med noen års erfaring, prioriterer vi din videre utvikling høyt.               ",
      "Vi ønsker å styrke vår utviklingsavdeling, og søker en engasjert og løsningsorientert utvikler med noen års erfaring (er du nyutdannet, men brenner for faget er du velkommen til å sende en søknad)", #. Du trives i et hektisk og kreativt miljø, med spennende og krevende kunder.",
]:
  doc = nlp(word)
  matches = matcher(doc)
  for np in doc.noun_chunks: #! [https://stackoverflow.com/questions/36698769/chunking-with-rule-based-grammar-in-spacy?rq=1]
    print(np.text)
  # fIXME: try merging below with the "" above
  # if(arr_matches_doc != None):
  #   arr_local = []
  #   for match_id, start, end in matches:
  #     label = nlp.vocab.strings[match_id]
  #     span = doc[start:end]
  #     arr_local.append(span);
  # if(len(arr_local) > 0):
  #   doc_new = doc;
  #   #doc_new = nlp.make_doc(word)   #! Note: documetnation for class="doc" is found at [https://spacy.io/api/doc]
  #   filtered_ents = filter_spans(arr_local)
  #   doc_new.ents = filtered_ents
  #   arr_matches_doc.append(doc_new);
  #   svg = displacy.render(doc_new, style="ent", manual=True)
  #   #svg = displacy.render(doc_new, style="ent"); #, manual=True)
  #   #svg = displacy.render(doc_new, style="dep")
  #   output_path = pathlib.Path("tmp.svg") # you can keep there only "dependency_plot.svg" if you want to save it in the same folder where you run the script
  #   output_path.open("w", encoding="utf-8").write(svg)
  #span = Span(doc, start, end, label); #! [https://spacy.io/api/span#similarity]
# Serve visualization of sentences containing match with displaCy
# fIXME: update the belwo list ... when we extend our match-making efforts
colors = {"MATCH": "#F67DE3", "MEDICINE": "#7DF6D9", "MEDICALCONDITION":"#FFFFFF"}
options = {"colors": colors}
# set manual=True to make displaCy render straight from a dictionary
html = displacy.render(arr_matches, style="ent", manual=True, options= options) # FIXME: update our "nlp_findNumbersInText.py" with this visu-strateg!
output_path = pathlib.Path(os.path.join("./", "sentence.html"))
output_path.open('w', encoding="utf-8").write(html); #! [https://stackoverflow.com/questions/55723812/when-i-save-the-output-of-displacy-renderdoc-style-dep-to-a-svg-file-there]
#displacy.serve(arr_matches, style="ent", options= options, manual = True); #jupyter=True)

#!
#!
#! Step: use a different strategy, focusing on the lables:
#! Template: [https://stackoverflow.com/questions/68105495/spacy-pattern-matching-rule-formation?rq=1]
#assert(False); # FIXME: why does the below NOT work wrt. the "ruler.add_patterns(..)" <-- how should the aptterns be deifned?
#text = "I saw a red apple under a lamp in the large white building"
#nlp = spacy.blank("en")

#assert(False);  # FIXME: re-sue + rewrite the below patterns ... to saitsyfy oru ssytem ...
DURATIONS = 'week weekly biweekly daily day'.split()
patterns = [ #! Template: [https://github.com/explosion/spaCy/discussions/7430]
    {
      'id': key,
      'label': 'CHRONO',
      'pattern':
      [
        {'LOWER': {
          'IN': ['a', 'by the', 'every', 'per']
        } },
        {'LEMMA': key}  # should be LEMMA
      ][0 if not key.endswith('ly') else 1:]
  }
  for key in DURATIONS
]

# texts = [        "I water the plants daily.",        "When is the weekly meeting?"]


#lemma_config = {"mode":"lookup"}
#lemmatizer = nlp.add_pipe("lemmatizer", before="ner", config=lemma_config)
#lemmatizer.initialize()
ruler = nlp.add_pipe("entity_ruler", before="ner")
ruler.add_patterns(patterns)
#ruler = nlp.add_pipe("entity_ruler"); #! error: entityruler.py", line 302, in add_patterns    if isinstance(entry["pattern"], str): TypeError: list indices must be integers or slices, not str
#ruler.add_patterns(arr_patterns)
print("[tut-spacy-pattern-3.py]\t The enttiy labels")
for word in [
    "Databases are interesting, though databases are not always easy to use",
    "Work related to Databases. For this position, we are also looking for:. 2-5 years’ relevant experience and IT academic background.",
    "For this position, we are also looking for:. two-five years’ relevant experience and IT academic background.",
    "For this position, we are also looking for:. to-fem years’ relevant experience and IT academic background.",
    "M.Sc / B.Sc med 2-5 års erfaring fra Telecom/Nettverksløsninger", "Vi ønsker at du allerede har 2-5 års erfaring, enten fra lignende stilling, eller fra operativt lønns- eller IT-arbeid.", "Du har minimum 2-5 års erfaring med Onsite IT Supportoppgaver.", "Teknisk utdanning (Bachelor/teknisk fagskole), men 2-3 års relevant erfaring kan erstatte formelle krav.", "Minimum 2-3 års arbeidserfaring, gjerne innen service eller andre relevante områder.", "For this position, we are also looking for:. 2-5 years’ relevant experience and IT academic background.", "With 2-10 years experience but recent graduates will be considered", " For å lykkes hos oss tror vi du. har høyere utdanning, gjerne på Masternivå og 5-10 års erfaring innen informasjonssikkerhet (fortrinnsvis fra roller som CISO, sikkerhetsarkitekt eller, konsulent/rådgiver).", "Preferably 5-10 or more years of experience with project work, but less experienced are encouraged to apply if this is something you are passionate about.", "0-10 års relevant erfaring.", "You have preferably 0-10 years of experience with project work, service or operations; new graduates are welcome to apply.", "You have preferably 0-10 years of experience with project work, service or operations; new graduates are welcome to apply.", "0-10 års relevant erfaring",
      "Minimum 2 års erfaring", "Bør ha minst fem års erfaring som utvikler.", "Minst fem års relevant erfaring", "Høyere utdannelse innen IT og minst fem års relevant erfaring.", "Minimum fem års erfaring med relevante arbeidsoppgaver. Flytende norsk skriftlig og muntlig", "Som seniorutvikler har du flere års erfaring med programvareutvikling", "Minimum 5 års praksis som Delivery Manager innen utvikling - og tekologileveranser.", "Minimum 2 års erfaring med kvalitetssikring innen IT-prosjekter.", "Minimum 2 års erfaring som utvikler.", "Minimum 1-2 års års relevant arbeidserfaring innen frontend utvikling.",  "Minimum 2 års relevant erfaring.", " Minimum 2 års erfaring med kvalitetssikring innen IT-prosjekter.", "Minimum 3 års erfaring fra tilsvarende oppgaver. ", "Minimum 5 års erfaring med backend (eksempelvis dotnet, C# og/eller Java, Spring) eller fullstack. ",  "Minimum tre års relevant arbeidserfaring som utvikler.", " Minimum ti års relevant erfaring.", "Minimum 5 års praksis som Delivery Manager innen utvikling - og teknologileveranser.", " Minimum tre års arbeidserfaring innen relevant fagområde.", "Minimum 3 års relevant erfaring.", "Minimum 2-3 års relevant arbeidserfaring, gjerne fra arbeid som omfatter tjenesteutvikling.", "Har minimum 2-4 års erfaring innenfor flere av følgende teknologier og rammeverk", "Har minimum 2-4 års erfaring innenfor flere av følgende teknologier og rammeverk", "Har minimum 2-4 års erfaring innenfor flere av følgende teknologier og rammeverk",
      #!
      #!
      "Vi ser etter en testleder med noen års erfaring innen testledelse og test av IKT-løsninger, og som motiveres av å jobbe med tjenester som gir stor nytteverdi for helsetjenesten.",
      "Fortrinnsvis noen års erfaring fra lignende arbeid, men nyutdannede er også velkommen til å søke. God digital kompetanse og interesse for digital utvikling.",
      "Vi ser etter deg som har noen års erfaring med utvikling av infrastruktur og komplekse løsninger.",
      "Noen års erfaring fra digital produkt- og tjenesteutvikling.",
      "Videre er det fordelaktig at du er/har:. Noen års erfaring med back-end .NET utvikling, herunder C, C++, C# osv.",
      "Du har noen års erfaring fra moderne utviklingsprosjekter der du har vært involvert i ulike deler av leveransene og du har interesse for et bredt sett av fagfelt (fullstack/backend). Vi tror de rette kandidatene kan kjenne seg igjen i følgende:. Høyere relevant utdanning og noen års arbeidserfaring som utvikler. ",
      "Du liker å programmere, har god teknisk forståelse og noen års erfaring som utvikler.",
      "Du må ha noen års erfaring med utvikling og arkitektur,",
      "Du må ha noen års erfaring med utvikling eller arkitektur, gjerne som løsningsarkitekt eller systemarkitekt, herunder relevant erfaring med. prinsipper for IT-arkitektur og metodeverk.",
      "Vi ønsker at du har noen års erfaring med solid kompetanse på en eller flere tjenester innenfor Microsoft 365-porteføljen. ",
      "Vi ser etter deg som har noen års erfaring fra nettverk, brannmur og virtualiserte miljøer.",
      "Vi leter etter deg som har noen års erfaring og ønsker å jobbe in-house med å løse kompliserte tekniske problemer. ",
      "For å lykkes i rollen tror vi at du kjenner deg igjen i noen av disse punktene:. Noen års erfaring som fullstack utvikler. ",
      "Det er et pluss om du har noen års relevant arbeidserfaring, men det ikke et krav.               ",
      "Noen års relevant arbeidserfaring og/eller kunnskap tilegnet fra endre arenaer er fordelaktig.               ",
      "Det ønskes noen års jobberfaring, men nyutdannede oppfordres også til å søke. ",
      "Du er en utvikler med noen års erfaring, som kan ta valg på vegne av eller sammen med teamet. Du er en fremoverlent lagspiller som må kunne diskutere tekniske løsninger med både tekniske og ikke-tekniske personer. Du liker å ta ansvar, og setter pris på at du får være med å bestemme.",
      "Egenskaper du bør ha:. Noen års erfaring som utvikler. Kjennskap til en eller flere skyplatformer. Erfaring med Docker og containere. ",
      "Om du sitter på noen års erfaring med iOS-plattformen, er det supert. Er du fersk, men har et høyt engasjement og et stort talent, er det også interessant.               ",
      "Det er et pluss om du har noen års relevant arbeidserfaring, men det ikke et krav.",
      "Du har noen års erfaring innen drift, IT-systemer og infrastruktur, og vi tror den rette kandidaten viser nysgjerrighet ovenfor nye områder og har en brennende interesse for IT. Det er en bonus om du kjenner til ITIL prosesser. ",
      "Vi ser etter deg som har noen års erfaring, vilje og tyngde til å ta ansvar for deler av vår, etter hvert ganske omfattende, portefølje av tekniske applikasjoner. Du har god kjennskap til teknologistacken vår og liker å spille på lag. ",
      "Vi tror du har:. Noen års erfaring som utvikler.",
      "Teknisk fagskole / Bachelor innen automasjon med noen års jobberfaring. Erfaring innen bygg automasjon, smarthus, IoT- internet of things.               ",
      "Selv om du kommer med noen års erfaring, prioriterer vi din videre utvikling høyt.               ",
      "Vi ønsker å styrke vår utviklingsavdeling, og søker en engasjert og løsningsorientert utvikler med noen års erfaring (er du nyutdannet, men brenner for faget er du velkommen til å sende en søknad)", #. Du trives i et hektisk og kreativt miljø, med spennende og krevende kunder.",
]:
  for ent in nlp(word).ents:
    print(ent.label_, ent, sep="\t")


#displacy.serve(arr_matches, style="ent", manual=True) # FIXME: update our "nlp_findNumbersInText.py" with this visu-strateg!

if(True): #! Visualizing dependencies []
  # FIXME: merge below and above
  #nlp = spacy.load("en_core_web_sm")
  #doc = nlp("Autonomous cars shift insurance liability toward manufacturers")
  # Since this is an interactive Jupyter environment, we can use displacy.render here
  #svg = displacy.render(doc, style='dep')
  #displacy.serve(arr_matches_doc); #, style="ent", manual=True)
  #svg = displacy.render(arr_matches_doc, style='dep')
  #svg = spacy.displacy.render(doc, style="dep")
  #output_path = pathlib.Path(os.path.join("./", "sentence.svg"))
  #output_path.open('w', encoding="utf-8").write(svg); #! [https://stackoverflow.com/questions/55723812/when-i-save-the-output-of-displacy-renderdoc-style-dep-to-a-svg-file-there]
  pass;
