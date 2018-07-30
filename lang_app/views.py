from django.shortcuts import render
from lang_app.models import Card
from random import randint


# Create your views here.
def index(request):

    if request.method == 'GET':

        # Get a random card
        all_cards = Card.objects.all()

        card = all_cards[randint(0, len(all_cards))]
        context = {
            'question_number': card.pk,
            'question': card.ask_question()
        }

        return render(request, 'lang_app/question.html', context)
    #
    # if request.method == 'POST':
    #     answer = request.POST.get('answer')
    #
    #     card = Card.objects.get(pk=request.POST.get('question_number'))
    #     correct_bool = card.give_answer(answer)[0]
    #
    #     context = {
    #         'correct_bool': correct_bool,
    #         'card': card,
    #         'answer': answer,
    #         'question': card.ask_question()
    #     }

        return render(request, 'lang_app/template.html', {})



