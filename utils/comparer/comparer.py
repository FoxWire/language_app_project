# Django stuff
import os
import sys
import django
sys.path.append('/home/stuart/PycharmProjects/workspaces/language_app_project')
os.environ['DJANGO_SETTINGS_MODULE'] = 'language_app_project.settings'
django.setup()

from nltk.parse import stanford
import nltk
from scipy.spatial import distance
from zss import simple_distance, Node
from lang_app.models import Card, Sentence
import re


class TreeComparer():
    '''
    This class uses the zzs algorithm to work out the similarity between
    two trees. The comparison should mean that the structure will be compared.
    I have also left the leaves of the trees intact, so they are also part of the comparison.
    This could be desirable for finding sentences with the same words, there could be some focus on
    vocabulary.

    Each card will need to store a string representation of the chunk as a tree.

    You need to change the compare method so that it compares the sentences with the words removed.
    This means that you are comparing the questions and not the sentences. To do this you need to
    get the parse tree for the whole sentence and then black out the words that are missing
    the nodes for the words

    Maybe the easiest thing is to change the words in the sentence and then reparse them.

    '''

    def __init__(self):
        self.parser = stanford.StanfordParser()

    def compare_tree_strings(self, tree_string_a, tree_string_b, ignore_leaves=False):
        '''
        Gets the difference between two parse trees using the zss comparison algorithm
        :param tree_string_a:
        :param tree_string_b:
        :param ignore_leaves:
        :return:
        '''
        zss_tree_a = self.convert_parse_tree_to_zss_tree(tree_string_a, ignore_leaves=ignore_leaves)
        zss_tree_b = self.convert_parse_tree_to_zss_tree(tree_string_b, ignore_leaves=ignore_leaves)
        return simple_distance(zss_tree_a, zss_tree_b)

    def compare(self, card_a, card_b):
        # zss_tree_a = self.convert_parse_tree_to_zss_tree(card_a.chunk_tree_string)
        # zss_tree_b = self.convert_parse_tree_to_zss_tree(card_b.chunk_tree_string)
        # return simple_distance(zss_tree_a, zss_tree_b)

        # You only need to run the remove chunk function if the cards doesn't already have the correct data
        parse_tree_a = card_a.question_tree_string
        if not parse_tree_a:
            parse_tree_a = self.remove_chunk_from_parse_tree(card_a)

        parse_tree_b = card_b.question_tree_string
        if not parse_tree_b:
            parse_tree_b = self.remove_chunk_from_parse_tree(card_b)

        return self.compare_tree_strings(parse_tree_a, parse_tree_b, ignore_leaves=True)

    # def convert_parse_tree_to_python_tree(self, tree_as_string):
    #     '''
    #     This is an alternative method to the one below, the converts a parse tree string
    #     to a 'python tree' ie a list of lists. This is not used at the moment, but may be useful
    #     later.
    #     '''
    #
    #     tree_as_list = [item.strip() for item in re.split(r'([\(\)])', tree_as_string) if item.strip()]
    #     tree_as_list = tree_as_list[2:-1]
    #
    #     stack = [['ROOT', []]]
    #     root = stack[0]
    #     # Iterate over the list
    #     for i, item in enumerate(tree_as_list):
    #         if item == '(':
    #             # If the node doesn't have children
    #             match = re.search(r'[A-Z]+[ ][A-Za-z]+', tree_as_list[i + 1])
    #             if match:
    #                 label = match.group().split(' ')
    #                 node = [label[0], label[1]]
    #             else:
    #                 node = [tree_as_list[i + 1], []]
    #
    #             # Add the node to the children of the current item
    #             stack[-1][1].append(node)
    #             # Then add the node to the stack itself
    #             stack.append(node)
    #         elif item == ')':
    #             # this node has no children so just pop it from the stack
    #             stack.pop()
    #     return root

    def convert_parse_tree_to_zss_tree(self, tree_as_string, ignore_leaves=False):
        '''
        The ignore leaves argument will create a tree where the words in the sentence
        are not included. This will only represent sentence structure. 
        '''

        print(type(tree_as_string))
        print("one")
        tree_as_list = [item.strip() for item in re.split(r'([\(\)])', tree_as_string) if item.strip()]
        print("two")
        print(tree_as_list)
        tree_as_list = tree_as_list[2:-1]

        stack = [Node('ROOT')]
        root_node = stack[0]
        # Iterate over the list
        for i, item in enumerate(tree_as_list):
            if item == '(':
                # match the string for each item
                match = re.search(r'[A-Z]+[ ][A-Za-z]+', tree_as_list[i + 1])
                if match:
                    # if match, node has no children
                    label = match.group().split(' ')
                    node = Node(label[0]).addkid(Node(label[1])) if not ignore_leaves else Node(label[0])
                else:
                    # otherwise node has children
                    node = Node(tree_as_list[i + 1])
                # Add the node to the children of the current item
                stack[-1].addkid(node)
                # Then add the node to the stack itself
                stack.append(node)
            elif item == ')':
                # this node has no children so just pop it from the stack
                stack.pop()
        return root_node

    def remove_chunk_from_parse_tree(self, card):
        '''
        This needs to find out what the pos of the word in the gap is and
        put a different label down if it is a verb.
        '''



        # Get the parse tree for the whole sentence
        parse_tree = card.sentence.sentence_tree_string



        # Get the words and their tags for each word in the chunk
        token_tups = [tuple(token[1:-1].split(' ')) for token in re.findall(r'\([A-Z$.,:]+ [\w\'&\.\-:]+\)', card.chunk_tree_string)]

        # Build up a regex to match the chunk from the parse tree
        regex_string = r'[\sA-Z$.,:]+'
        for token in token_tups:
            r = token[1] + '[()\sA-Z$.,:]*'
            regex_string += r



        # Extract the chunk from the parse tree and make a copy
        extracted = re.findall(regex_string, parse_tree)[0]
        copy = extracted

        # replace the chunks in the copy with dummy values for verb and non verb
        for token in token_tups:
            insert_label = "VERB verb" if token[0].startswith("V") else "NON-VERB non-verb"
            copy = re.sub(r'[A-Z$.,:]+ {}'.format(token[1]), insert_label, copy)

        # Put the changes back into the original parse tree
        parse_tree = parse_tree.replace(extracted, copy)

        return parse_tree


if __name__ == '__main__':
   for c in Card.objects.all()[:100]:
       print(c.pk)




