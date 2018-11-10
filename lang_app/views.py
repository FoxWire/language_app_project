from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from lang_app.models import Card, UserState
from lang_app.forms import UserForm, UserProfileForm
from utils.question_picker.picker import Picker
from utils.parser.parser import Parser
from utils.parser.lemmatizer import Lemmatizer
from utils.comparer.comparer import TreeComparer
from random import choice
import csv
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse


# picker = Picker()
# parser = Parser()
# comp = TreeComparer()
# lem = Lemmatizer()


# def register(request):
#
#     # Boolean value signals to the template if registration was completed successfully
#     # initially set to false, it will be flipped to true if registration is completed
#     registered = False
#
#     # If post request
#     if request.method == 'POST':
#
#         # Take the post data from the request and attempt to populate
#         # the form instances with it
#         user_form = UserForm(data=request.POST)
#         profile_form = UserProfileForm(data=request.POST)
#
#         # Check that the forms are valid
#         if user_form.is_valid() and profile_form.is_valid():
#
#             user = user_form.save()
#             user.set_password(user.password)
#             user.save()
#
#             profile = profile_form.save(commit=False)
#             profile.user = user
#
#             # if 'picture' in request.FILES:
#             #     profile.picture = request.FILES['picture']
#
#             profile.save()
#
#             registered = True
#
#         else:
#             print(user_form.errors, profile_form.errors)
#
#     else:
#         # If get request:
#         # Just create two blank form objects to return to the template
#         user_form = UserForm()
#         profile_form = UserProfileForm()
#
#     context_dict = {'user_form': user_form,
#                     'profile_form': profile_form,
#                     'registered': registered
#                     }
#
#     return render(request, 'lang_app/registration_form.html', context_dict)


# def user_login(request):
#
#     if request.method == 'POST':
#
#         # If this is a post request, get the username and password
#         username = request.POST.get('username')
#         password = request.POST.get('password')
#
#         # Authenticate the details, if the details are correct, a user object is returns else None
#         user = authenticate(username=username, password=password)
#
#         # If the user exists and their account is active, login and redirect to the main page
#         if user:
#             if user.is_active:
#                 login(request, user)
#                 return HttpResponseRedirect(reverse('index'))
#             else:
#                 return HttpResponse("Your Rango account is disabled")
#         else:
#             print("Invalid login details: {0} {1}".format(username, password))
#             return HttpResponse("Invalid login details supplied")
#
#     # If this is a get request, render the login page
#     else:
#         return render(request, 'lang_app/login.html', {})


@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))

# This is the normal index
# @login_required
def index(request):

    '''

    This is the view that deals with the main user interaction of the application

    '''

    context = None
    if request.method == 'GET':
        # Get the user and get the user state
        user = request.user
        for u in UserState.objects.all():
            print(u)
        print('end')



        pass

    if request.method == 'POST':
        pass

        # take the answer from the user and pass it to the picker for marking etc



        # user_answer = request.POST.get('user_answer')
        #
        # card = Card.objects.get(pk=request.POST.get('question_number'))
        # correct_bool = card.give_answer(user_answer)[0]
        #
        # context = {
        #     'show_answer': True,
        #     'question_number': card.pk,
        #     'question_data': card.ask_question(),
        #     'correct_bool': correct_bool,
        #     'user_answer': user_answer,
        #     'chunk': card.chunk,
        #     'chunk_translation': card.chunk_translation
        # }

    return render(request, 'lang_app/index.html', context)


# # Ajax listener
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


# def authenticate_user(request):
#     return render(request, 'lang_app/authenticate.html', context={})


# This is the test index that will record your answers
# @login_required
# def index(request):
#     '''
#     The random numbers are read in from file each time. When you get a new question, you look for the last line
#     in the user function file and then reference that line in the random numbers.
#
#     This is how you maintain the order.
#     '''
#
#     print(settings.BASE_DIR)
#
#     rand_nums = [None,]   # dummy value to get counting from 1
#     # Read in the data to a list
#     with open(settings.BASE_DIR + "/data/new_random_nums.csv", 'r') as file:
#         reader = csv.reader(file, delimiter='\n')
#         for row in reader:
#             rand_nums.append(row[0])
#
#     path = settings.BASE_DIR + '/data/third_user_function.csv'
#     context = None
#     if request.method == 'GET':
#
#         # get the number of the current question, so that we can stop the server here
#         # if needed
#         row_count = 1
#         with open(path, 'r') as file:
#             reader = csv.reader(file, delimiter=',')
#             for row in reader:
#                 row_count += 1
#
#         # Use the row number to get the pk from the list
#         pk = rand_nums[row_count]
#         card = Card.objects.get(pk=pk)
#
#         data = card.ask_question()
#
#         context = {
#             'question_number': card.pk,
#             'question_data': data,
#             'required_words': lem.lemmatize(card),
#         }
#
#         print("asking question: ", card.pk)
#
#     if request.method == 'POST':
#
#         if request.POST.get("second_post") == 'False':
#             # The first post takes the answer that they have entered and deals with it
#
#             '''
#             this is the part where you need to change how the marking is done
#             get the question answer string from the user and place it in the sentence
#             then you can parse it an compare it it with the parse tree of the whole sentence
#             '''
#
#             user_answer = request.POST.get('user_answer')
#
#             card = Card.objects.get(pk=request.POST.get('question_number'))
#             correct_bool = card.give_answer(user_answer)[0]
#
#             # use the parser to get the tree string for the user answer
#             # user_answer_tree_string = parser.parse(user_answer)[2]
#
#             # do the same to get the actual answer
#             # actual_answer_tree_string = parser.parse(card.chunk)[2]
#
#             # score = comp.compare_tree_strings(user_answer_tree_string, actual_answer_tree_string)
#
#             # create the whole sentence using the users answer
#             x = card.sentence.sentence.split(card.chunk)
#             complete_user_answer = " ".join([x[0], user_answer, x[1]])
#
#             user_answer_tree_string = str(parser.parse(complete_user_answer)[2])
#
#
#             score = comp.compare_tree_strings(user_answer_tree_string, card.sentence.sentence_tree_string)
#             print("The score between these two answers was:", score)
#
#             # put the score and pk into the csv
#             with open(path, 'a') as file:
#                 writer = csv.writer(file, delimiter=',')
#                 writer.writerow([card.pk, score, user_answer])
#
#             context = {
#                 'show_answer': True,
#                 'question_number': card.pk,
#                 'question_data': card.ask_question(),
#                 'correct_bool': correct_bool,
#                 'user_answer': user_answer,
#                 'chunk': card.chunk,
#                 'chunk_translation': card.chunk_translation
#             }
#         else:
#             # the second post takes the difficulty rating and adds it to the other thing
#             rating = request.POST.get("rating")
#             question_no = request.POST.get("question_number")
#
#             # just read everything from the csv file into memory
#             data = []
#             with open(path, 'r') as file:
#                 for row in csv.reader(file, delimiter=','):
#                     data.append(row)
#
#             # and then loop over add the stuff that you want to add
#             with open(path, 'w') as file:
#                 writer = csv.writer(file, delimiter=',')
#                 for d in data:
#                     if d[0] == question_no:
#                         writer.writerow([d[0], d[1], d[2], rating])
#                     else:
#                         writer.writerow(d)
#
#             # then I think you can just redirect to the get
#             redirect = "?question_number={0}&answered_correctly={1}".format(question_no, request.POST.get("answered_correctly"))
#             return HttpResponseRedirect(redirect)
#
#     return render(request, 'lang_app/index.html', context)





