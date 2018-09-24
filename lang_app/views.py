from django.http import HttpResponse
from django.shortcuts import render
from lang_app.models import Card
from random import randint
from utils.question_picker.naive_picker import NaivePicker
from utils.parser.parser import Parser
from utils.comparer.comparer import TreeComparer
from random import choice
# import csv


picker = NaivePicker()
parser = Parser()
comp = TreeComparer()


# Create your views here.
def index(request):

    context = None
    if request.method == 'GET':

        question_number = request.GET.get('question_number')
        if not question_number:
            # This is the first question so just return a random card
            all_cards = Card.objects.all()
            card = all_cards[randint(0, len(all_cards))]
        else:
            # use the question number to pick the next card
            answered_correctly = request.GET.get('answered_correctly')
            current_card = Card.objects.get(pk=question_number)
            card = picker.pick(current_card, answered_correctly)

        data = card.ask_question()

        context = {
            'question_number': card.pk,
            'question_data': data,
        }

    if request.method == 'POST':
        user_answer = request.POST.get('user_answer')

        card = Card.objects.get(pk=request.POST.get('question_number'))
        correct_bool = card.give_answer(user_answer)[0]

        context = {
            'show_answer': True,
            'question_number': card.pk,
            'question_data': card.ask_question(),
            'correct_bool': correct_bool,
            'user_answer': user_answer,
            'chunk': card.chunk,
            'chunk_translation': card.chunk_translation
        }

    return render(request, 'lang_app/template.html', context)


# Ajax listener
def get_hint(request):

    if request.method == 'GET':
        card_id = request.GET.get('card_id')
        shown_words = request.GET.get('shown_words')
        word = ""
        if card_id:
            chunk = Card.objects.get(id=int(card_id)).chunk

            if shown_words:
                # split the chunk and remove any words that have already been shown
                words = [word for word in chunk.split(' ') if word not in shown_words]
                word = choice(words) if words else ''
            else:
                word = choice([word for word in chunk.split(' ')])

        return HttpResponse(word)


# def index(request):
#     '''
#     This is another view that is used for gathering data. 

#     To test the GP script I need a more realisic user function. The best way to do this is to 
#     Actually work through the first 100 cards myself and give answers for them. It would be a
#     pain to actually have to write all of this down so I'll set up this view to ask the the questions 
#     to me and record the answers.
#     '''

#     path = '/home/stuart/PycharmProjects/workspaces/language_app_project/data/user_function.csv'

#     context = None
#     if request.method == 'GET':

#         question_number = request.GET.get('question_number')
#         if not question_number:
#             # get the number of the current question, so that we can stop the server here
#             # if needed 
#             row_count = 1
#             with open(path, 'r') as file:
#                 reader = csv.reader(file, delimiter=',')
#                 for row in reader:
#                     row_count += 1

#             # This is the first question so return the first card
#             card = Card.objects.get(pk=row_count)
#         else:
#             # use the question number to pick the next card
#             # answered_correctly = request.GET.get('answered_correctly')
#             # current_card = Card.objects.get(pk=question_number)
#             # card = picker.pick(current_card, answered_correctly)
#             card = Card.objects.get(pk=int(question_number) + 1)

#         data = card.ask_question()

#         context = {
#             'question_number': card.pk,
#             'question_data': data,
#         }

#         print("asking question: ", card.pk)

#     if request.method == 'POST':

#         user_answer = request.POST.get('user_answer')

#         card = Card.objects.get(pk=request.POST.get('question_number'))
#         correct_bool = card.give_answer(user_answer)[0]

#         # use the parser to get the tree string for the user answer
#         user_answer_tree_string = parser.parse(user_answer)[2]

#         # do the same to get the actual answer
#         actual_answer_tree_string = parser.parse(card.chunk)[2]

#         score = comp.compare_tree_strings(user_answer_tree_string, actual_answer_tree_string)
#         print("The score between these two answers was:", score)

#         # put the score and pk into the csv
#         with open(path, 'a') as file:
#             writer = csv.writer(file, delimiter=',')
#             writer.writerow([card.pk, score])


#         context = {
#             'show_answer': True,
#             'question_number': card.pk,
#             'question_data': card.ask_question(),
#             'correct_bool': correct_bool,
#             'user_answer': user_answer,
#             'chunk': card.chunk,
#             'chunk_translation': card.chunk_translation
#         }

#     return render(request, 'lang_app/template.html', context)





