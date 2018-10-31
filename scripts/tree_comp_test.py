

from lang_app.models import Card, Sentence
from utils.comparer.comparer import TreeComparer
from utils.parser.parser import Parser

'''
I am using the tree comparison algo to mark and score the user's answers. 
If you have the exact same sentence, you will get a score of 0
If you replace one word with another of the same type, (verb) then you will be only one point out.
When you go outside of that, you are changing the structure of the tree and that will mean you get more points 
in differnce. 

So what does that mean? Is it good to use the tree comparison for marking? 
Does it make a difference if we put the chunks into the complete sentences or not?

'''

# Here are two example sentences
sentence_a = "We were swimming with her today."
# chunk_a = "I'm daft and that's about it."

sentence_b = "We were speaking with her today."
# chunk_b = "I'm stupid and that's it."



parser = Parser()
comp = TreeComparer()

a_parsed = parser.parse(sentence_a)[2]

b_parsed = parser.parse(sentence_b)[2]

x = comp.compare_tree_strings(a_parsed, b_parsed, ignore_leaves=True)
print(x)
