"""!
@file
@brief
@remarks
# FIXME: udpate the belwow based on this explraotion!
- pre: read the "tut-productGrammar.py"
- tempatel: https://www.machinelearningplus.com/spacy-tutorial-nlp/
"""
import spacy
from spacy.matcher import Matcher
nlp = spacy.load("en_core_web_sm")
#! -------------------------------------- -------------------------------------- -------------------------------------- --------------------------------------
#!
#! Taksk 1: a basic explroaton of the "spacy.matcher" API:
# FIXME: use this to update oru code (eg, "scrubWords.py")? <-- why+how+hwne?
# Initializing the matcher with vocab
matcher = Matcher(nlp.vocab)
#matcher
# Define the matching pattern
my_pattern=[{"LOWER": "version"}, {"IS_PUNCT": True}, {"LIKE_NUM": True}]

# Define the token matcher
matcher.add('VersionFinder', [ my_pattern])


# Run the Token Matcher
my_text = 'The version : 6 of the app was released about a year back and was not very sucessful. As a comeback, six months ago, version : 7 was released and it took the stage. After that , the app has has the limelight till now. On interviewing some sources, we get to know that they have outlined visiond till version : 12 ,the Ultimate.'
my_doc = nlp(my_text)

desired_matches = matcher(my_doc)
print(desired_matches);

# Extract the matches
# FIXME: can we relate this to our defineVocabularies.py normalision-effort?
for match_id, start, end in desired_matches :
  string_id = nlp.vocab.strings[match_id]
  span = my_doc[start:end]
  print(span.text)

#! -----------------------------
#! -------------------------------------- -------------------------------------- -------------------------------------- --------------------------------------
#!
#! Task 2: "Consider a text document containing queries on a travel website. You wish to extract phrases from the text that mention visiting various places."
# Parse text
text = """I visited Manali last time. Around same budget trips ? "
    I was visiting Ladakh this summer "
    I have planned visiting NewYork and other abroad places for next year"
    Have you ever visited Kodaikanal? """

doc = nlp(text)
# The below code demonstrates how to write and add this pattern to the matcher

# Initialize the matcher
matcher = Matcher(nlp.vocab)

# Write a pattern that matches a form of "visit" + place
my_pattern = [{"LEMMA": "visit"}, {"POS": "PROPN"}]

# Add the pattern to the matcher and apply the matcher to the doc
matcher.add("Visting_places", [my_pattern])
matches = matcher(doc)

# Counting the no of matches
print(" matches found:", len(matches))

# Iterate over the matches and print the span text
for match_id, start, end in matches:
  print("Match found:", doc[start:end].text)
#! -----------------------------
#! -------------------------------------- -------------------------------------- -------------------------------------- --------------------------------------
#!
#! Task 3: "Sometimes, you may have the need to choose tokens which fall under a few POS categories. Let us consider one more example of this case."
# Parse text
engineering_text = """If you study aeronautical engineering, you could specialize in aerodynamics, aeroelasticity,
composites analysis, avionics, propulsion and structures and materials. If you choose to study chemical engineering, you may like to
specialize in chemical reaction engineering, plant design, process engineering, process design or transport phenomena. Civil engineering is the professional practice of designing and developing infrastructure projects. This can be on a huge scale, such as the development of
nationwide transport systems or water supply networks, or on a smaller scale, such as the development of single roads or buildings.
specializations of civil engineering include structural engineering, architectural engineering, transportation engineering, geotechnical engineering,
environmental engineering and hydraulic engineering. Computer engineering concerns the design and prototyping of computing hardware and software.
This subject merges electrical engineering with computer science, oldest and broadest types of engineering, mechanical engineering is concerned with the design,
manufacturing and maintenance of mechanical systems. You’ll study statics and dynamics, thermodynamics, fluid dynamics, stress analysis, mechanical design and
technical drawing"""

doc = nlp(engineering_text)
# Initializing the matcher
matcher = Matcher(nlp.vocab)

# Write a pattern that matches a form of "noun/adjective"+"engineering"
my_pattern = [{"POS": {"IN": ["NOUN", "ADJ"]}}, {"LOWER": "engineering"}] #! note: the "IN" tag is the central answer to the crux (addressed in this example)

# Add the pattern to the matcher and apply the matcher to the doc
matcher.add("identify_courses", [my_pattern])
matches = matcher(doc)
print("Total matches found:", len(matches))

# Iterate over the matches and print the matching text
for match_id, start, end in matches:
    print("Match found:", doc[start:end].text)



#! -----------------------------
#! -------------------------------------- -------------------------------------- -------------------------------------- --------------------------------------
#!
#! Task 4: "Phrase Matcher. Using Matcher of spacy you can identify token patterns as seen above. But when you have a phrase to be matched, using Matcher will take a lot of time and is not efficient."
from spacy.matcher import PhraseMatcher
# PhraseMatcher
matcher = PhraseMatcher(nlp.vocab)
#! As we use it generally in case of long list of terms, it’s better to first store the terms in a list as shown below
# Terms to match
terms_list = ['Bruce Wayne', 'Tony Stark', 'Batman', 'Harry Potter', 'Severus Snape']
# Make a list of docs
patterns = [nlp.make_doc(text) for text in terms_list]
# The inputs for the function are – A custom ID for your matcher, optional parameter for callable function, pattern list.
matcher.add("phrase_matcher",  [*patterns])
# Matcher Object
fictional_char_doc = nlp("""Superman (first appearance: 1938)  Created by Jerry Siegal and Joe Shuster for Action Comics #1 (DC Comics).Mickey Mouse (1928)  Created by Walt Disney and Ub Iworks for Steamboat Willie.Bugs Bunny (1940)  Created by Warner Bros and originally voiced by Mel Blanc.Batman (1939) Created by Bill Finger and Bob Kane for Detective Comics #27 (DC Comics).
Dorothy Gale (1900)  Created by L. Frank Baum for novel The Wonderful Wizard of Oz. Later portrayed by Judy Garland in the 1939 film adaptation.Darth Vader (1977) Created by George Lucas for Star Wars IV: A New Hope.The Tramp (1914)  Created and portrayed by Charlie Chaplin for Kid Auto Races at Venice.Peter Pan (1902)  Created by J.M. Barrie for novel The Little White Bird.
Indiana Jones (1981)  Created by George Lucas for Raiders of the Lost Ark. Portrayed by Harrison Ford.Rocky Balboa (1976)  Created and portrayed by Sylvester Stallone for Rocky.Vito Corleone (1969) Created by Mario Puzo for novel The Godfather. Later portrayed by Marlon Brando and Robert DeNiro in Coppola’s film adaptation.Han Solo (1977) Created by George Lucas for Star Wars IV: A New Hope.
Portrayed most famously by Harrison Ford.Homer Simpson (1987)  Created by Matt Groening for The Tracey Ullman Show, later The Simpsons as voiced by Dan Castellaneta.Archie Bunker (1971) Created by Norman Lear for All in the Family. Portrayed by Carroll O’Connor.Norman Bates (1959) Created by Robert Bloch for novel Psycho.  Later portrayed by Anthony Perkins in Hitchcock’s film adaptation.King Kong (1933)
Created by Edgar Wallace and Merian C Cooper for the film King Kong.Lucy Ricardo (1951) Portrayed by Lucille Ball for I Love Lucy.Spiderman (1962)  Created by Stan Lee and Steve Ditko for Amazing Fantasy #15 (Marvel Comics).Barbie (1959)  Created by Ruth Handler for the toy company Mattel Spock (1964)  Created by Gene Roddenberry for Star Trek. Portrayed most famously by Leonard Nimoy.
Godzilla (1954) Created by Tomoyuki Tanaka, Ishiro Honda, and Eiji Tsubaraya for the film Godzilla.The Joker (1940)  Created by Jerry Robinson, Bill Finger, and Bob Kane for Batman #1 (DC Comics)Winnie-the-Pooh (1924)  Created by A.A. Milne for verse book When We Were Young.Popeye (1929)  Created by E.C. Segar for comic strip Thimble Theater (King Features).Tarzan (1912) Created by Edgar Rice Burroughs for the novel Tarzan of the Apes.Forrest Gump (1986)  Created by Winston Groom for novel Forrest Gump.  Later portrayed by Tom Hanks in Zemeckis’ film adaptation.Hannibal Lector (1981)  Created by Thomas Harris for the novel Red Dragon. Portrayed most famously by Anthony Hopkins in the 1991 Jonathan Demme film The Silence of the Lambs.
Big Bird (1969) Created by Jim Henson and portrayed by Carroll Spinney for Sesame Street.Holden Caulfield (1945) Created by J.D. Salinger for the Collier’s story “I’m Crazy.”  Reworked into the novel The Catcher in the Rye in 1951.Tony Montana (1983)  Created by Oliver Stone for film Scarface.  Portrayed by Al Pacino.Tony Soprano (1999)  Created by David Chase for The Sopranos. Portrayed by James Gandolfini.
The Terminator (1984)  Created by James Cameron and Gale Anne Hurd for The Terminator. Portrayed by Arnold Schwarzenegger.Jon Snow (1996)  Created by George RR Martin for the novel The Game of Thrones.  Portrayed by Kit Harrington.Charles Foster Kane (1941)  Created and portrayed by Orson Welles for Citizen Kane.Scarlett O’Hara (1936)  Created by Margaret Mitchell for the novel Gone With the Wind. Portrayed most famously by Vivien Leigh
for the 1939 Victor Fleming film adaptation.Marty McFly (1985) Created by Robert Zemeckis and Bob Gale for Back to the Future. Portrayed by Michael J. Fox.Rick Blaine (1940)  Created by Murray Burnett and Joan Alison for the unproduced stage play Everybody Comes to Rick’s. Later portrayed by Humphrey Bogart in Michael Curtiz’s film adaptation Casablanca.Man With No Name (1964)  Created by Sergio Leone for A Fistful of Dollars, which was adapted from a ronin character in Kurosawa’s Yojimbo (1961).  Portrayed by Clint Eastwood.Charlie Brown (1948)  Created by Charles M. Shultz for the comic strip L’il Folks; popularized two years later in Peanuts.E.T. (1982)  Created by Melissa Mathison for the film E.T.: the Extra-Terrestrial.Arthur Fonzarelli (1974)  Created by Bob Brunner for the show Happy Days. Portrayed by Henry Winkler.)Phillip Marlowe (1939)  Created by Raymond Chandler for the novel The Big Sleep.Jay Gatsby (1925)  Created by F. Scott Fitzgerald for the novel The Great Gatsby.Lassie (1938) Created by Eric Knight for a Saturday Evening Post story, later turned into the novel Lassie Come-Home in 1940, film adaptation in 1943, and long-running television show in 1954.  Most famously portrayed by the dog Pal.
Fred Flintstone (1959)  Created by William Hanna and Joseph Barbera for The Flintstones. Voiced most notably by Alan Reed. Rooster Cogburn (1968)  Created by Charles Portis for the novel True Grit. Most famously portrayed by John Wayne in the 1969 film adaptation. Atticus Finch (1960)  Created by Harper Lee for the novel To Kill a Mockingbird.  (Appeared in the earlier work Go Set A Watchman, though this was not published until 2015)  Portrayed most famously by Gregory Peck in the Robert Mulligan film adaptation. Kermit the Frog (1955)  Created and performed by Jim Henson for the show Sam and Friends. Later popularized in Sesame Street (1969) and The Muppet Show (1976) George Bailey (1943)  Created by Phillip Van Doren Stern (then as George Pratt) for the short story The Greatest Gift. Later adapted into Capra’s It’s A Wonderful Life, starring James Stewart as the renamed George Bailey. Yoda (1980) Created by George Lucas for The Empire Strikes Back. Sam Malone (1982)  Created by Glen and Les Charles for the show Cheers.  Portrayed by Ted Danson. Zorro (1919)  Created by Johnston McCulley for the All-Story Weekly pulp magazine story The Curse of Capistrano.Later adapted to the Douglas Fairbanks’ film The Mark of Zorro (1920).Moe, Larry, and Curly (1928)  Created by Ted Healy for the vaudeville act Ted Healy and his Stooges. Mary Poppins (1934)  Created by P.L. Travers for the children’s book Mary Poppins. Ron Burgundy (2004)  Created by Will Ferrell and Adam McKay for the film Anchorman: The Legend of Ron Burgundy.  Portrayed by Will Ferrell. Mario (1981)  Created by Shigeru Miyamoto for the video game Donkey Kong. Harry Potter (1997)  Created by J.K. Rowling for the novel Harry Potter and the Philosopher’s Stone. The Dude (1998)  Created by Ethan and Joel Coen for the film The Big Lebowski. Portrayed by Jeff Bridges.
Gandalf (1937)  Created by J.R.R. Tolkien for the novel The Hobbit. The Grinch (1957)  Created by Dr. Seuss for the story How the Grinch Stole Christmas! Willy Wonka (1964)  Created by Roald Dahl for the children’s novel Charlie and the Chocolate Factory. The Hulk (1962)  Created by Stan Lee and Jack Kirby for The Incredible Hulk #1 (Marvel Comics) Scooby-Doo (1969)  Created by Joe Ruby and Ken Spears for the show Scooby-Doo, Where Are You! George Costanza (1989)  Created by Larry David and Jerry Seinfeld for the show Seinfeld.  Portrayed by Jason Alexander.Jules Winfield (1994)  Created by Quentin Tarantino for the film Pulp Fiction. Portrayed by Samuel L. Jackson. John McClane (1988)  Based on the character Detective Joe Leland, who was created by Roderick Thorp for the novel Nothing Lasts Forever. Later adapted into the John McTernan film Die Hard, starring Bruce Willis as McClane. Ellen Ripley (1979)  Created by Don O’cannon and Ronald Shusett for the film Alien.  Portrayed by Sigourney Weaver. Ralph Kramden (1951)  Created and portrayed by Jackie Gleason for “The Honeymooners,” which became its own show in 1955.Edward Scissorhands (1990)  Created by Tim Burton for the film Edward Scissorhands.  Portrayed by Johnny Depp.Eric Cartman (1992)  Created by Trey Parker and Matt Stone for the animated short Jesus vs Frosty.  Later developed into the show South Park, which premiered in 1997.  Voiced by Trey Parker.
Walter White (2008)  Created by Vince Gilligan for Breaking Bad.  Portrayed by Bryan Cranston. Cosmo Kramer (1989)  Created by Larry David and Jerry Seinfeld for Seinfeld.  Portrayed by Michael Richards.Pikachu (1996)  Created by Atsuko Nishida and Ken Sugimori for the Pokemon video game and anime franchise.Michael Scott (2005)  Based on a character from the British series The Office, created by Ricky Gervais and Steven Merchant.  Portrayed by Steve Carell.Freddy Krueger (1984)  Created by Wes Craven for the film A Nightmare on Elm Street. Most famously portrayed by Robert Englund.
Captain America (1941)  Created by Joe Simon and Jack Kirby for Captain America Comics #1 (Marvel Comics)Goku (1984)  Created by Akira Toriyama for the manga series Dragon Ball Z.Bambi (1923)  Created by Felix Salten for the children’s book Bambi, a Life in the Woods. Later adapted into the Disney film Bambi in 1942.Ronald McDonald (1963) Created by Williard Scott for a series of television spots.Waldo/Wally (1987) Created by Martin Hanford for the children’s book Where’s Wally? (Waldo in US edition) Frasier Crane (1984)  Created by Glen and Les Charles for Cheers.  Portrayed by Kelsey Grammar.Omar Little (2002)  Created by David Simon for The Wire.Portrayed by Michael K. Williams.
Wolverine (1974)  Created by Roy Thomas, Len Wein, and John Romita Sr for The Incredible Hulk #180 (Marvel Comics) Jason Voorhees (1980)  Created by Victor Miller for the film Friday the 13th. Betty Boop (1930)  Created by Max Fleischer and the Grim Network for the cartoon Dizzy Dishes. Bilbo Baggins (1937)  Created by J.R.R. Tolkien for the novel The Hobbit. Tom Joad (1939)  Created by John Steinbeck for the novel The Grapes of Wrath. Later adapted into the 1940 John Ford film and portrayed by Henry Fonda.Tony Stark (Iron Man) (1963)  Created by Stan Lee, Larry Lieber, Don Heck and Jack Kirby for Tales of Suspense #39 (Marvel Comics)Porky Pig (1935)  Created by Friz Freleng for the animated short film I Haven’t Got a Hat. Voiced most famously by Mel Blanc.Travis Bickle (1976)  Created by Paul Schrader for the film Taxi Driver. Portrayed by Robert De Niro.
Hawkeye Pierce (1968)  Created by Richard Hooker for the novel MASH: A Novel About Three Army Doctors.  Famously portrayed by both Alan Alda and Donald Sutherland. Don Draper (2007)  Created by Matthew Weiner for the show Mad Men.  Portrayed by Jon Hamm. Cliff Huxtable (1984)  Created and portrayed by Bill Cosby for The Cosby Show. Jack Torrance (1977)  Created by Stephen King for the novel The Shining. Later adapted into the 1980 Stanley Kubrick film and portrayed by Jack Nicholson. Holly Golightly (1958)  Created by Truman Capote for the novella Breakfast at Tiffany’s.  Later adapted into the 1961 Blake Edwards films starring Audrey Hepburn as Holly. Shrek (1990)  Created by William Steig for the children’s book Shrek! Later adapted into the 2001 film starring Mike Myers as the titular character. Optimus Prime (1984)  Created by Dennis O’Neil for the Transformers toy line.Sonic the Hedgehog (1991)  Created by Naoto Ohshima and Yuji Uekawa for the Sega Genesis game of the same name.Harry Callahan (1971)  Created by Harry Julian Fink and R.M. Fink for the movie Dirty Harry.  Portrayed by Clint Eastwood.Bubble: Hercule Poirot, Tyrion Lannister, Ron Swanson, Cercei Lannister, J.R. Ewing, Tyler Durden, Spongebob Squarepants, The Genie from Aladdin, Pac-Man, Axel Foley, Terry Malloy, Patrick Bateman
Pre-20th Century: Santa Claus, Dracula, Robin Hood, Cinderella, Huckleberry Finn, Odysseus, Sherlock Holmes, Romeo and Juliet, Frankenstein, Prince Hamlet, Uncle Sam, Paul Bunyan, Tom Sawyer, Pinocchio, Oliver Twist, Snow White, Don Quixote, Rip Van Winkle, Ebenezer Scrooge, Anna Karenina, Ichabod Crane, John Henry, The Tooth Fairy,
Br’er Rabbit, Long John Silver, The Mad Hatter, Quasimodo """)


character_matches = matcher(fictional_char_doc)
# Matching positions
print(character_matches);
# Matched items
for match_id, start, end in character_matches:
    span = fictional_char_doc[start:end]
    print(span.text)

#!
#! Note: "Another useful feature of PhraseMatcher is that while intializing the matcher, you have an option to use the parameter attr, using which you can set rules for how the matching has to happen":
# Using the attr parameter as 'LOWER'
case_insensitive_matcher = PhraseMatcher(nlp.vocab, attr="LOWER")

# Creating doc &amp; pattern
my_doc=nlp('I wish to visit new york city')
terms=['New York']
pattern=[nlp(term) for term in terms]

# adding pattern to the matcher
case_insensitive_matcher.add("matcher", [*pattern])

# applying matcher to the doc
my_matches=case_insensitive_matcher(my_doc)

for match_id,start,end in my_matches:
  span=my_doc[start:end]
  print(span.text)

# You want to extract the channels (in the form of ddd.d)
my_doc = nlp('From 8 am , Mr.X will be speaking on your favorite chanel 191.1. Afterward there shall be an exclusive interview with actor Vijay on channel 194.1 . Hope you are having a great day. Call us on 666666')
# Let us create the pattern. You need to pass an example radio channel of the desired shape as pattern to the matcher.
pattern=nlp('154.6')

# Initializing the matcher and adding pattern
pincode_matcher= PhraseMatcher(nlp.vocab,attr="SHAPE")
pincode_matcher.add("pincode_matching", [pattern])

# Applying matcher on doc
matches = pincode_matcher(my_doc)

# Printing the matched phrases
for match_id, start, end in matches:
  span = my_doc[start:end]
  print(span.text)

#! -----------------------------
#! -------------------------------------- -------------------------------------- -------------------------------------- --------------------------------------
#!
#! Task 5: "Entity Ruler. Entity Ruler is intetesting and very useful":
#! - "While trying to detect entities, some times certain names or organizations are not recognized by default. It might be because they are small scale or rare. Wouldn’t it be better to improve accuracy of our doc.ents_ method ?"
#! - "spaCy provides a more advanced component EntityRuler that let’s you match named entities based on pattern dictionaries. Overall, it makes Named Entity Recognition more efficient."

# "It is a pipeline supported component and can be imported as shown below"
from spacy.pipeline import EntityRuler

#! Initialize the EntityRuler as shown below

# Initialize
#ruler = EntityRuler(nlp)
# Add entity ruler to the NLP pipeline.
# NLP pipeline is a sequence of NLP tasks that spaCy performs for a given text
# More on pipelines coming in future section in this post.
#nlp.add_pipe(ruler)
ruler = nlp.add_pipe("entity_ruler")
# My label will be WORK_OF_ART and pattern will contain the book names I wish to add. Below code demonstrates the same.
pattern=[{"label": "WORK_OF_ART", "pattern": "My guide to statistics"}]
# You can add pattern to the ruler through add_patterns() function
ruler.add_patterns(pattern)

# Extract the custom entity type
doc = nlp(" I recently published my work fanfiction by Dr.X . Right now I'm studying the book of my friend .You should try My guide to statistics for clear concepts.")
print([(ent.text, ent.label_) for ent in doc.ents])

# Summary: You have successfuly enhanced the named entity recoginition. It is possible to train spaCy to detect new entities it has not seen as well.

#! -----------------------------
#! -------------------------------------- -------------------------------------- -------------------------------------- --------------------------------------
#!
#! Task 6: "Word Vectors and similarity"
# - "Word Vectors are numerical vector representations of words and documents. The numeric form helps understand the semantics about the word and can be used for NLP tasks such as classification."
# - "Because, vector representation of words that are similar in meaning and context appear closer together."
# - "spaCy models support inbuilt vectors that can be accessed through directly through the attributes of Token and Doc. How can you check if the model supports tokens with vectors ?"
# - "First, load a spaCy model of your choice. Here, I am using the medium model for english en_core_web_md. Next, tokenize your text document with nlp boject of spacy model."

#! pre: "pythonr -m spacy download en_core_web_md"
# Check if word vector is available
import spacy

# Loading a spacy model
#nlp = spacy.load("en_core_web_md")
tokens = nlp("I am an excellent cook")
for token in tokens:
  print(token.text ,' ',token.has_vector)

# Check if word vector is available
tokens=nlp("I wish to go to hogwarts lolXD ")
for token in tokens:
  print(token.text,' ',token.has_vector)

# Extract the word Vector
tokens=nlp("I wish to go to hogwarts lolXD ")
for token in tokens:
  print(token.text,' ',token.vector_norm)

#!
#! SubTask: "How to find similarity of two tokens?":
# Compute Similarity
token_1=nlp("bad")
token_2=nlp("terrible")
#! Then calcuate it:
similarity_score=token_1.similarity(token_2)
print(similarity_score)

# Let me show you an example of how similarity() function on docs can help in text categorization.
review_1=nlp(' The food was amazing')
review_2=nlp('The food was excellent')
review_3=nlp('I did not like the food')
review_4=nlp('It was very bad experience')

score_1=review_1.similarity(review_2)
print('Similarity between review 1 and 2',score_1)

score_2=review_3.similarity(review_4)
print('Similarity between review 3 and 4',score_2)

# You can also check if two tokens or docs are related (includes both similar side and opposite sides) or completely irrelevant.

# Compute Similarity between texts
pizza=nlp('pizza')
burger=nlp('burger')
chair=nlp('chair')

print('Pizza and burger  ',pizza.similarity(burger))
print('Pizza and chair  ',pizza.similarity(chair))

#! -----------------------------
#! -------------------------------------- -------------------------------------- -------------------------------------- --------------------------------------
#!
#! Task 7: "Merging and Splitting Tokens with retokenize":
#   - "When nlp object is called on a text document, spaCy first tokenizes the text to produce a Docobject. The Tokenizer is the pipeline component responsible for segmenting the text into tokens."
#   - "Sometime tokenization splits a combined word into two tokens instead of keeping it as one unit."
#   - "Consider the below case, you have a text document on a film ‘John Wick’."
#   - ""


# Printing tokens of a text
text="John Wick is a 2014 American action thriller film directed by Chad Stahelski"
doc=nlp(text)
for token in doc:
  print(token.text)


#! Challenge: "So, How to combine the tokens?"
#! Answer: "spaCy provides Doc.retokenize , a context manager that allows you to merge and split tokens. For merging two or more tokens , you can make use of the retokenizer.merge() function."
# Using retokenizer.merge()
with doc.retokenize() as retokenizer:
    attrs = {"POS": "PROPN"}
    retokenizer.merge(doc[0:2], attrs=attrs) # FIXME: this uses only ngram=2? ... if yes, possilbe makign this even mroe flexible?

for token in doc:
  print(token.text)

# You can also verify if John wick has been assigned ‘PROPN’ pos tag through below code.

# Printing tokens after merging
for token in doc:
  print(token.text,token.pos_)

#!
#! SubTask: "You have seen how to merge tokens. Now, let us have a look at how to split tokens. Consider below text."
text = 'I purchased the trendy OnePlus7'
# Splitting tokens using retokenizer.split()
doc=nlp('I purchased the trendy OnePlus7 ')
with doc.retokenize() as retokenizer:
    heads = [(doc[3], 1), doc[2]]
    retokenizer.split(doc[4], ["OnePlus", "7"],heads=heads)

for token in doc:
  print(token.text)


#! -----------------------------
#! -------------------------------------- -------------------------------------- -------------------------------------- --------------------------------------
#!
#! Task 8: "spaCy pipelines
#   - "You have used tokens and docs in many ways till now. In this section, let’s dive deeper and understand the basic pipeline behind this."
#   - "When you call the nlp object on spaCy, the text is segmented into tokens to create a Doc object. Following this, various process are carried out on the Doc to add the attributes like POS tags, Lemma tags, dependency tags,etc.."
#   - "This is referred as the Processing Pipeline"
#   - ""
#   - ""
"""
The built-in pipeline components of spacy are :
    Tokenizer : It is responsible for segmenting the text into tokens are turning a Doc object. This the first and compulsory step in a pipeline.
    Tagger : It is responsible for assigning Part-of-speech tags. It takes a Doc as input and createsDoc[i].tag
    DependencyParser : It is known as parser. It is responsible for assigning the dependency tags to each token. It takes a Doc as input and returns the processed Doc
    EntityRecognizer : This component is referred as ner. It is responsible for identifying named entities and assigning labels to them.
    TextCategorizer : This component is called textcat. It will assign categories to Docs.
    EntityRuler : This component is called * entity_ruler*.It is responsible for assigning named entitile based on pattern rules. Revisit Rule Based Matching to know more.
    Sentencizer : This component is called **sentencizer** and can perform rule based sentence segmentation.
    merge_noun_chunks : It is called mergenounchunks. This component is responsible for merging all noun chunks into a single token. It has to be add in the pipeline after tagger and parser.
"""
# Inspect a pipeline
import spacy
nlp = spacy.load("en_core_web_sm")
print(nlp.pipe_names)

#  Check if pipeline component present
print(nlp.has_pipe('textcat'));
# Add new pipeline component
if(not nlp.has_pipe('textcat')):
  nlp.add_pipe("textcat", before="ner") # nlp.create_pipe('textcat'))
print(nlp.pipe_names)
# Adding a pipeline component
#nlp.add_pipe(nlp.create_pipe('textcat'),before='ner')
print(nlp.pipe_names);


# Printing the components initially
print(' Pipeline components present initially')
print(nlp.pipe_names)

# Removing a pipeline component and printing
nlp.remove_pipe("textcat")
print('After removing the textcat pipeline')
print(nlp.pipe_names)

# Renaming pipeline components
nlp.rename_pipe(old_name='ner',new_name='my_custom_ner')
print(nlp.pipe_names);
#! -----------------------------
#! -------------------------------------- -------------------------------------- -------------------------------------- --------------------------------------
#!
#! Task 9: "Methods for Efficient processing"
#   - "While dealing with huge amount of text data , the process of converting the text into processed Doc ( passing through pipeline components) is often time consuming."
#   - "In this section , you’ll learn various methods for different situations to help you reduce computational expense."
#   - "Let’s say you have a list of text data , and you want to process them into Doc onject. The traditional method is to call nlp object on each of the text data . Below is the given list."
#   - ""
#   - ""
list_of_text_data=['In computer science, artificial intelligence (AI), sometimes called machine intelligence, is intelligence demonstrated by machines, in contrast to the natural intelligence displayed by humans and animals.','Leading AI textbooks define the field as the study of "intelligent agents": any device that perceives its environment and takes actions that maximize its chance of successfully achieving its goals.','Colloquially, the term "artificial intelligence" is often used to describe machines (or computers) that mimic "cognitive" functions that humans associate with the human mind, such as "learning" and "problem solving','As machines become increasingly capable, tasks considered to require "intelligence" are often removed from the definition of AI, a phenomenon known as the AI effect.','The term military simulation can cover a wide spectrum of activities, ranging from full-scale field-exercises,[2] to abstract computerized models that can proceed with little or no human involvement','As a general scientific principle, the most reliable data comes from actual observation and the most reliable theories depend on it.[4] This also holds true in military analysis','Any form of training can be regarded as a "simulation" in the strictest sense of the word (inasmuch as it simulates an operational environment); however, many if not most exercises take place not to test new ideas or models, but to provide the participants with the skills to operate within existing ones.','ull-scale military exercises, or even smaller-scale ones, are not always feasible or even desirable. Availability of resources, including money, is a significant factor—it costs a lot to release troops and materiel from any standing commitments, to transport them to a suitable location, and then to cover additional expenses such as petroleum, oil and lubricants (POL) usage, equipment maintenance, supplies and consumables replenishment and other items','Moving away from the field exercise, it is often more convenient to test a theory by reducing the level of personnel involvement. Map exercises can be conducted involving senior officers and planners, but without the need to physically move around any troops. These retain some human input, and thus can still reflect to some extent the human imponderables that make warfare so challenging to model, with the advantage of reduced costs and increased accessibility. A map exercise can also be conducted with far less forward planning than a full-scale deployment, making it an attractive option for more minor simulations that would not merit anything larger, as well as for very major operations where cost, or secrecy, is an issue']
# %%timeit
docs = [nlp(text) for text in list_of_text_data]

# disabling loading of components
nlp = spacy.load("en_core_web_sm", disable=["tagger", "parser"])
print(nlp.has_pipe('tagger'))
print(nlp.has_pipe('parser'))

# Below code passes a list of pipeline components to be disabled temporarily to the argument diable.
nlp=spacy.load('en_core_web_sm')
for doc in nlp.pipe(list_of_text_data, disable=["ner", "parser"]):
  print(doc.is_tagged)

# ---
# The below example demonstrates how to disable tagger and ner in a block of code.
nlp=spacy.load('en_core_web_sm')
# Block where pipelines are disabled
with nlp.disable_pipes("tagger", "ner"):
    print('-- Inside the block--')
    doc = nlp(" The pandemic has disrupted the lives of may")
    print(doc.is_nered)

# The block has ended ,
print('-- outside the block--')
doc = nlp("I will be tagged and parsed")
doc.is_nered

#! -----------------------------
#! -------------------------------------- -------------------------------------- -------------------------------------- --------------------------------------
#!
#! Task 10: "Creating custom pipeline components"
#   - "We know that a pipeline component takes the Doc as input, performs functions, adds attributes to the doc and returns a Processed Doc. Here, we shall see how to create your own pipeline component or custom pipeline component."
#   - "Custom pipeline components let you add your own function to the spaCy pipeline that is executed when you call the nlpobject on a text."
#   - "Steps to create a custom pipeline component": "First, write a function that takes a Doc as input, performs neccessary tasks and returns a new Doc. Then, add this function to the spacy pipeline through nlp.add_pipe() method.":
"""
The parameters of add_pipe you have to provide :
1.    component : You have to pass the function_name as input . This serves as our component
2.    name : You can assign a name to the component. The component can be called using this name. If you don’t provide any ,the function_name will be taken as name of the component
3.    first,last : If you want the new component to be added first or last ,you can setfirst=True or last=True accordingly.
4.    before , after : If you want to add the component specifically before or after another component , you can use these arguments.
"""
#   - ""
#   - ""
#   - ""

assert(False) # FIXME: get the below rule-based custom-matcher to work <-- pre: descirbe how our algorithm-tranier works

# Define the custom component that prints the doc length and named entities.
def my_custom_component(doc):
    doc_length = len(doc)
    print(' The no of tokens in the document ', doc_length)
    named_entity=[token.label_ for token in doc.ents]
    print(named_entity)
    # Return the doc
    return doc


# Load the small English model
nlp = spacy.load("en_core_web_sm")

# Add the component in the pipeline after ner
nlp.add_pipe(my_custom_component, after='ner')
print(nlp.pipe_names)
#

# Call the nlp object on your text
doc = nlp(" The Hindu Newspaper has increased the cost. I usually read the paper on my way to Delhi railway station ")

#!
#! SubTask: "Pipeline component example"
#! - what: "Let’s level up and try implementing more complex case."
#! - why: "Consider you have a doc and you want to add a pipeline component that can find some book names present and add add them to doc.ents."
# FIXME: try using the below ... AFTER having playing around wiuht the rule-based mahcign-example(s):
# Importing PhraseMatcher from spacy and intialize with a model's vocab
from spacy.matcher import PhraseMatcher
nlp = spacy.load("en_core_web_sm")
matcher = PhraseMatcher(nlp.vocab)

# List of book names to be matched
book_names = ['Pride and prejudice','Mansfield park','The Tale of Two cities','Great Expectations']

# Creating pattern - list of docs through nlp.pipe() to save time
book_patterns = list(nlp.pipe(book_names))

# Adding the pattern to the matcher
matcher.add("identify_books", *book_patterns)

# Import Span to slice the Doc
from spacy.tokens import Span

# Define the custom pipeline component
def identify_books(doc):
    # Apply the matcher to YOUR doc
    matches = matcher(doc)
    # Create a Span for each match and assign them under label "BOOKS"
    spans = [Span(doc, start, end, label="BOOKS") for match_id, start, end in matches]
    # Store the matched spans in doc.ents
    doc.ents = spans
    return doc
# Adding the custom component to the pipeline after the "ner" component
nlp.add_pipe(identify_books, after="ner")
print(nlp.pipe_names)

# Calling the nlp object on the text
doc = nlp("The library has got several new copies of Mansfield park and Great Expectations . I have filed a suggestion to buy more copies of The Tale of Two cities ")

# Printing entities and their labels to verify
print([(ent.text, ent.label_) for ent in doc.ents])
#! -----------------------------
#! -------------------------------------- -------------------------------------- -------------------------------------- --------------------------------------
#!
#! Task 11:
#   - ""
#   - ""
#   - ""

#! -----------------------------
#! -------------------------------------- -------------------------------------- -------------------------------------- --------------------------------------
#!
#! Task 12:
#   - ""
#   - ""
#   - ""
#! -----------------------------
#! -------------------------------------- -------------------------------------- -------------------------------------- --------------------------------------
#!
#! Task :
