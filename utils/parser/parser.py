import os
from nltk.parse import stanford
import nltk
from scipy.spatial import distance
import re
import json
from language_app_project.settings import BASE_DIR

text = '''
S - simple declarative clause, i.e. one that is not introduced by a (possible empty) subordinating conjunction or a wh-word and that does not exhibit subject-verb inversion.
SBAR -ADJP - Adjective Phrase.
ADVP - Adverb Phrase.
CONJP - Conjunction Phrase.
FRAG - Fragment.
INTJ - Interjection. Corresponds approximately to the part-of-speech tag UH.
LST - List marker. Includes surrounding punctuation.
NAC - Not a Constituent; used to show the scope of certain prenominal modifiers within an NP.
NP - Noun Phrase. 
NX - Used within certain complex NPs to mark the head of the NP. Corresponds very roughly to N-bar level but used quite differently.
PP - Prepositional Phrase.
PRN - Parenthetical. 
PRT - Particle. Category for words that should be tagged RP. 
QP - Quantifier Phrase (i.e. complex measure/amount phrase); used within NP.
RRC - Reduced Relative Clause. 
UCP - Unlike Coordinated Phrase. 
VP - Vereb Phrase. 
WHADJP - Wh-adjective Phrase. Adjectival phrase containing a wh-adverb, as in how hot.
WHAVP - Wh-adverb Phrase. Introduces a clause with an NP gap. May be null (containing the 0 complementizer) or lexical, containing a wh-adverb such as how or why.
WHNP - Wh-noun Phrase. Introduces a clause with an NP gap. May be null (containing the 0 complementizer) or lexical, containing some wh-word, e.g. who, which book, whose daughter, none of which, or how many leopards.
WHPP - Wh-prepositional Phrase. Prepositional phrase containing a wh-noun phrase (such as of which or by whose authority) that either introduces a PP gap or is contained by a WHNP.
X - Unknown, uncertain, or unbracketable. X is often used for bracketing typos and in bracketing the...the-constructions. Clause introduced by a (possibly empty) subordinating conjunction.
SBARQ - Direct question introduced by a wh-word or a wh-phrase. Indirect questions and relative clauses should be bracketed as SBAR, not SBARQ.
SINV - Inverted declarative sentence, i.e. one in which the subject follows the tensed verb or modal.
SQ - Inverted yes/no question, or main clause of a wh-question, following the wh-phrase in SBARQ.

'''


class Parser:

    '''
    This class has one main method that will take a sentence and return a tuple of:
        - the sentence
        - the list of chunks for that sentence
        - and the parse tree as a string

    It will cache the results of parse in a json file
    '''

    def __init__(self):
        self.parser = stanford.StanfordParser()
        self.cache_file = os.path.join(BASE_DIR, 'utils/parser/sentence_chunker_cache.json')
        self.labels_file = 'higher_level_labels.txt'
        # self.all_labels = self.load_labels()

    # def load_labels(self):
    #
    #     '''
    #     Reads in the labels from a text file. These are only the labels that feature higher up in
    #     the parse tree hierarchies and so represent the 'deeper' structure of the sentence.
    #     '''
    #
    #     with open(self.labels_file) as data_file:
    #         all_labels = {line.split('-')[0].strip() for line in data_file.read().split('\n')}

    def parse(self, sentence):
        '''
        This method takes a sentence and returns three pieces of data. The sentence itself,
        the chunks of the sentence and the tree string.
        The method is called once when only the chunks are needed and once for the other two pieces of
        data. At some point this should be refactored into two methods (that may share the use of one
        underlying 'parse' method)
        '''

        # Check if you have already chunked this sentence
        result = self._check_cache(sentence)
        if result:
            # print("***   INFO: Sentences retrieved from cache   ***")
            return sentence, result['chunks'], result['tree_string']

        # Only attempt to chunk the sentence if it's not in the cache
        else:
            # print("***   INFO: Parsing sentences. This may take some time.   ***")

            # Get the parse tree
            tree = next(self.parser.raw_parse(sentence))
            # get the number of parts of speech in this sentence
            no_of_pos = len(tree.leaves())

            # Get all the subtrees flattened as tuples
            phrases = [(sub.flatten().label(), sub.leaves()) for sub in tree.subtrees()]

            # Convert the text ^^^above^^^ into a set of labels
            all_labels = {line.split('-')[0].strip() for line in text.split('\n')}

            # Filter on the set of labels. This means that you only use the
            # 'higher level' trees that are specified in the text.
            chunks = [phrase for phrase in phrases if phrase[0] in all_labels]

            # filter out the one word phrases and the full sentence
            chunks = [chunk for chunk in chunks if 1 < len(chunk[1]) < no_of_pos]

            # Use regex to rebuild the lists of leaves into strings.
            formatted_chunks = []
            for chunk in chunks:
                regex = r''
                for leaf in chunk[1]:
                    regex += leaf + '\s*'

                result = re.search(regex, sentence)
                if not result:
                    print("***   INFO: Regex: {} didn't match sentence {}   ***".format(regex, sentence))
                else:
                    formatted_chunks.append(result.group())

            # remove any duplicates
            formatted_chunks = list(set(formatted_chunks))

            parsed_object = (sentence, formatted_chunks, str(tree))
            self._write_to_cache(parsed_object)

            return parsed_object

    # def get_tree_string(self, chunk):
    #     results = self._check_cache(chunk)
    #     if results and results.get('tree_string'):
    #         return results['tree_string']
    #     else:
    #         chunks = self.get_chunks(chunk)
    #         return self.get_tree_string(chunk)
    #
    # def get_labels(self, sentence):
    #     results = self._check_cache(sentence)
    #     if results:
    #         return results['labels']
    #     else:
    #         # If the chunk or sentence that is passed in is not in the cache, you will need to parse it
    #         #  the get chunks method actually does the parsing and caching, so you can just call it
    #         #  (ignore the chunks that come back) and then recursively call the get labels method again
    #         chunks = self.get_chunks(sentence)
    #         return self.get_labels(sentence)

    def _check_cache(self, sentence):

        # Read from the cache file
        with open(self.cache_file) as data_file:
            cache = json.loads(data_file.read())

            return cache.get(sentence)

    def _write_to_cache(self, parsed_object):

        # Read from the cache file
        with open(self.cache_file) as data_file:
            cache = json.loads(data_file.read())

            # Add the new entry to the cache
            entry = {
                'chunks': parsed_object[1],
                'tree_string': parsed_object[2]
            }
            cache[parsed_object[0]] = entry

        # write to the cache file again
        with open(self.cache_file, 'w') as cache_file:
            json.dump(cache, cache_file, indent=4)


if __name__ == '__main__':
    parser = Parser()
    chunks = parser.parse("This is a test sentence")
    print(chunks)



