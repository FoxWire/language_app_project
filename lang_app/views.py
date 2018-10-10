from django.http import HttpResponse
from django.shortcuts import render
from lang_app.models import Card
from random import randint
from utils.question_picker.naive_picker import NaivePicker
from utils.parser.parser import Parser
from utils.comparer.comparer import TreeComparer
from random import choice
import csv


picker = NaivePicker()
parser = Parser()
comp = TreeComparer()


# Create your views here.
# def index(request):
#
#     context = None
#     if request.method == 'GET':
#
#         question_number = request.GET.get('question_number')
#         if not question_number:
#             # This is the first question so just return a random card
#             all_cards = Card.objects.all()
#             card = all_cards[randint(0, len(all_cards))]
#         else:
#             # use the question number to pick the next card
#             answered_correctly = request.GET.get('answered_correctly')
#             current_card = Card.objects.get(pk=question_number)
#             card = picker.pick(current_card, answered_correctly)
#
#         data = card.ask_question()
#
#         context = {
#             'question_number': card.pk,
#             'question_data': data,
#         }
#
#     if request.method == 'POST':
#         user_answer = request.POST.get('user_answer')
#
#         card = Card.objects.get(pk=request.POST.get('question_number'))
#         correct_bool = card.give_answer(user_answer)[0]
#
#         context = {
#             'show_answer': True,
#             'question_number': card.pk,
#             'question_data': card.ask_question(),
#             'correct_bool': correct_bool,
#             'user_answer': user_answer,
#             'chunk': card.chunk,
#             'chunk_translation': card.chunk_translation
#         }
#
#     return render(request, 'lang_app/template.html', context)


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


def index(request):
    '''
    The random numbers are read in from file each time. When you get a new question, you look for the last line
    in the user function file and then reference that line in the random numbers.

    This is how you maintain the order.
    '''

    rand_nums = [None,]   # dummy value to get counting from 1
    # Read in the data to a list
    with open("/home/stuart/PycharmProjects/workspaces/language_app_project/data/rand_nums.csv", 'r') as file:
        reader = csv.reader(file, delimiter='\n')
        for row in reader:
            rand_nums.append(row[0])

    path = '/home/stuart/PycharmProjects/workspaces/language_app_project/data/user_function_c.csv'
    context = None
    if request.method == 'GET':

        # get the number of the current question, so that we can stop the server here
        # if needed
        row_count = 1
        with open(path, 'r') as file:
            reader = csv.reader(file, delimiter=',')
            for row in reader:
                row_count += 1

        # Use the row number to get the pk from the list
        pk = rand_nums[row_count]
        card = Card.objects.get(pk=pk)

        data = card.ask_question()

        context = {
            'question_number': card.pk,
            'question_data': data,
        }

        print("asking question: ", card.pk)

    if request.method == 'POST':

        user_answer = request.POST.get('user_answer')

        card = Card.objects.get(pk=request.POST.get('question_number'))
        correct_bool = card.give_answer(user_answer)[0]

        # use the parser to get the tree string for the user answer
        user_answer_tree_string = parser.parse(user_answer)[2]

        # do the same to get the actual answer
        actual_answer_tree_string = parser.parse(card.chunk)[2]

        score = comp.compare_tree_strings(user_answer_tree_string, actual_answer_tree_string)
        print("The score between these two answers was:", score)

        # put the score and pk into the csv
        with open(path, 'a') as file:
            writer = csv.writer(file, delimiter=',')
            writer.writerow([card.pk, score])

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





