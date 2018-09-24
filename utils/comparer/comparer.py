import os
from nltk.parse import stanford
import nltk
from scipy.spatial import distance
from zss import simple_distance, Node
import re


class TreeComparer():
    '''
    This class uses the zzs algorithm to work out the similarity between
    two trees. The comparison should mean that the structure will be compared.
    I have also left the leaves of the trees intact, so they are also part of the comparison.
    This could be desirable for finding sentences with the same words, there could be some focus on
    vocabulary.

    Each card will need to store a string representation of the chunk as a tree.
    '''

    def __init__(self):
        self.parser = stanford.StanfordParser()

    def compare_tree_strings(self, tree_string_a, tree_string_b, ignore_leaves=False):
        zss_tree_a = self.convert_parse_tree_to_zss_tree(tree_string_a, ignore_leaves=ignore_leaves)
        zss_tree_b = self.convert_parse_tree_to_zss_tree(tree_string_b, ignore_leaves=ignore_leaves)
        return simple_distance(zss_tree_a, zss_tree_b)

    def compare(self, card_a, card_b):
        zss_tree_a = self.convert_parse_tree_to_zss_tree(card_a.tree_string)
        zss_tree_b = self.convert_parse_tree_to_zss_tree(card_b.tree_string)
        return simple_distance(zss_tree_a, zss_tree_b)

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

        tree_as_list = [item.strip() for item in re.split(r'([\(\)])', tree_as_string) if item.strip()]
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


if __name__ == '__main__':
    comp = TreeComparer()
    sentence = "This is a sentence"


