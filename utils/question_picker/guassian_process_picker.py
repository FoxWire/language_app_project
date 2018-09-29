from utils.comparer.comparer import TreeComparer
from lang_app.models import Card
from random import randint
from tqdm import tqdm
import json
from utils.kernels.custom_kernel import CustomKernel
from sklearn.gaussian_process import GaussianProcessRegressor
import numpy as np


class GaussianProcessPicker:
    '''
        The naive picker just picks the next most similar card that doesn't have the same sentence
        as the previous card if the user gets the question wrong and a random card if they get it right.

        The GP picker will use the gaussian process to work out which card should come next. This will be the simplest
        implementation of the GP. The pick method returns random questions, until it has ten, then it uses the gp to
        find the card that the user will find the hardest.

        The update method is called each time the user posts an answer. It adds cards to the list until it has ten, once
        it has ten, it will train the model. If the model is trained on the initial ten cards, it will fit the model to
        any additional cards that come in.

        This is just fleshed out at the moment and still needs to be completed.

        What should be the algorithm here? If they get the question right, we can explore other areas that they need to look at.
        But if they get the question wrong, they we know that they need to practise these types of questions. We can explore using the gp
        and we can get the similar questions from the tree comparer.

        the gp gives us the ability to guess how what their score will be for each question and tells us how accurate this guess might be.

        so if they get an answer right, we find the question that we are least sure about and ask that question. If they get it wrong, then they need to
        practise, so we can find similar questions and ask them. we don't need to use the tree comparision for this though, we can use the gp to tell us
        what questions they will find easy. I think we will want to combine the knowledge from the gp and the tree comparision. we will then know what are
        similar questions and how likely it is that they will get the question right.
    '''

    def __init__(self):
        self.random_cards = []
        self.kernel = CustomKernel()
        self.gp = GaussianProcessRegressor(kernel=self.kernel, optimizer=0)
        self.number_of_cards = len(Card.objects.all())
        self.number_of_initial_questions = 10

    def pick(self):
        #  returns random cards until it has ten
        if len(self.random_cards) < self.number_of_initial_questions:
            random_pk = randint(1, self.number_of_cards)
            return Card.objects.get(pk=random_pk)
        # We now have ten items and the model has been trained
        else:
            # Here we can work out the prediction that the model will make so far and we
            # also have the confidence that we have in our prediciton, for the moment, we
            # will just ignore the sigma

            # get the card with the lowest prediction
            predictions, sigma = self.gp.predict(np.atleast_2d([range(1, self.number_of_cards)]).T, return_std=True)
            return  # the card with the lowest prediction

    def update(self, card, answer_score):
        # This is called each time the user provides an answer

        # Add the card and answer to the list if we don't already have ten
        if len(self.random_cards) < self.number_of_initial_questions:
            self.random_cards.append((card.pk, answer_score))
            # If you now have ten, train the gp
            if len(self.random_cards) == self.number_of_initial_questions:

                questions = np.atleast_2d([x[0] for x in self.random_cards]).T
                answers = np.atleast_2d([x[1] for x in self.random_cards]).T
                self.gp.fit(questions, answers)
        else:
            # You have the ten initial answers and the model is trained so you can fit the single answer
            question = np.atleast_2d([card.pk]).T
            answer = np.atleast_2d([answer_score]).T
            self.gp.fit(question, answer)






