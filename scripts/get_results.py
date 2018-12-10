# Django stuff
import os
import sys
import django
sys.path.append('/home/stuart/PycharmProjects/workspaces/language_app_project')
os.environ['DJANGO_SETTINGS_MODULE'] = 'language_app_project.settings'
django.setup()

from lang_app.models import Question, Block, Session, UserState, Sentence, QandA
from utils.policies.policies import PolicyOne, PolicyTwo, PolicyThree
import re
from random import randint, shuffle
from utils.matrix_wrapper import MatrixWrapper
from tqdm import tqdm

from django.contrib.auth.models import User
import json

from language_app_project.settings import BASE_DIR
from anytree import Node, RenderTree, PreOrderIter

'''
What do you want to know? 

which policy performed the best?

'''

path = os.path.join(BASE_DIR, 'data', 'session_data')

user_data = {}
for user_name in os.listdir(path):
    for session in os.listdir(os.path.join(path, user_name)):
        with open(os.path.join(path, user_name, session), 'r') as file:
            data = json.loads(file.read())
            user_name = data['user_name']
            if user_name not in user_data:
                user_data[user_name] = [data]
            else:
                user_data[user_name].append(data)

# # For get the scores for each session
# for user_name, sessions in user_data.items():
#     for session in sessions:
#         correct = 0
#         total = 0
#         for block in session['block_data']:
#             for qanda in block['qanda_data']:
#                 if qanda['answer_correct']:
#                     correct += 1
#                 total += 1
#         print("For policy {} {} got {}/{}".format(session['policy_id'], user_name, correct, total))
#
# # what was the improvement over the course of each policy
# for user_name, sessions in user_data.items():
#     for session in sessions:
#         for block in session['block_data']:
#             correct = 0
#             total = 0
#             for qanda in block['qanda_data']:
#                 if qanda['answer_correct']:
#                     correct += 1
#                 total += 1
#             print("For block {} in policy {} {} got {}/{}".format(block['block_id'], session['policy_id'], user_name, correct, total))
#     print("")


'''
Next try to recreate the trail of exploit questions. 
Each time you need to look at all of the failed questions for the whole session
Look at the ones they got wrong in the initial section
then look at the ones in the next section that they got wrong which ones are similar?
'''

matrix = MatrixWrapper()

# Francesco session two
session_2 = None
for session in user_data['fra']:
    if session['policy_id'] == 2:
        session_2 = session


# Get the failed questions from the first block
first_block = session_2['block_data'][0]['qanda_data']
wrong_answers_first_block = [qanda for qanda in first_block if not qanda['answer_correct']]

# Get the exploit questions from the next block and see which ones are similar to the ones in the first block
exploit_from_next_block = [qanda for qanda in session_2['block_data'][1]['qanda_data'] if qanda['qanda_type'] == 'exploit']

# which of the first ones matches up to the other second ones
for first in wrong_answers_first_block:
    lowest_value = 100
    lowest_pk = 0
    for next in exploit_from_next_block:
        value = matrix.get_value(first['qanda_pk'], next['qanda_pk'], pk=True)
        if value < lowest_value:
            lowest_value = value
            lowest_pk = next['qanda_pk']
    print("{} -> {}".format(first['qanda_pk'], lowest_pk))
print('---')


# Get all of the wrong explore questions
wrong_explore = []
for block in session_2['block_data']:
    for qanda in block['qanda_data']:
        if qanda['qanda_type'] == 'explore' and not qanda['answer_correct']:
            wrong_explore.append(Node( { 'qanda_pk': qanda['qanda_pk'], 'question_pk':qanda['question_pk'], 'qanda_correct': qanda['answer_correct']}))


'''
Here you want to look at each of the exploit questions that occur in each block. You know that an exploit question
must have been generated because of a failed explore question and you have those already in the list.
For each exploit question, you can look at the failed explore ones  (which are all potential parents) and iterate over them
each time getting their next would be suggestion and comparing that to the the one you have.

If they get one of the exploit questions right, you can't keep adding to it
'''

# Iterate over all the questions in the session
for index, block in enumerate(session_2['block_data']):
    # the nodes to add at the end of each block
    nodes_to_add = []

    for qanda in block['qanda_data']:

        # Only look at the exploit ones
        if qanda['qanda_type'] == 'exploit':

            # Get a list of all the seen question pks up to this point
            seen_questions = [qanda['question_pk'] for block in session_2['block_data'][:index] for qanda in block['qanda_data']]

            # For each of the possible parents, find out what they could have suggested
            suggested_pks = []
            for root in wrong_explore:
                for node in PreOrderIter(root):

                    # For each potential parent, get the next questions that it would have suggested

                    # Note: here you would have to check that the exploit quesiton was answered wrong

                    # For each node you need to find the sentence that it would have suggested
                    similar_pks = matrix.get_similar_question_pks(node.name['question_pk'])
                    potential_parent = Question.objects.get(pk=node.name['question_pk'])

                    for pk in similar_pks:
                        question = Question.objects.get(pk=pk)
                        if pk not in seen_questions and question.sentence.sentence != potential_parent.sentence.sentence:
                            suggested_pks.append((pk, node, qanda['answer_correct']))
                            break

            # Find the suggested question that matches the one you are looking for
            for pk, node, correct in suggested_pks:
                if pk == qanda['question_pk']:

                    # If the parent was a wrong answer, add the new node
                    if not node.name['qanda_correct']:
                        nodes_to_add.append(({'qanda_pk': qanda['qanda_pk'], 'question_pk': qanda['question_pk'], 'qanda_correct': correct}, node))

    for item in nodes_to_add:
        n = Node(item[0], parent=item[1])




count = 0
for tree in wrong_explore:
    print()
    for pre, fill, node in RenderTree(tree):
        print("%s%s" % (pre, node.name))
        count += 1

print(count)

# how many explore ones did he get right?

count = 0
for block in session_2['block_data']:
    for qanda in block['qanda_data']:
        if qanda['qanda_type'] == 'explore':
            count += 1

print(count)
