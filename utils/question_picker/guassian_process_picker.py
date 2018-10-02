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

        The high level algorithm:
        - Ask the initial random questions and use these to train the model
        - Find the question that we predict them to get the most wrong
        - Ask them the question:
            - if they get it wrong:
                - find similar questions and start a practise session
            - if they get it right:
                - just add this to the model
        - After a practise session or a single right answer, go into explore mode ie find the question that
        we know the least about and ask them that

        So in a way we just alternate between explore and exploit


    '''

    def __init__(self):
        self.random_cards = []
        self.kernel = CustomKernel()
        self.gp = GaussianProcessRegressor(kernel=self.kernel, optimizer=0)
        self.number_of_cards = len(Card.objects.all())
        self.number_of_initial_questions = 3

        self.mode = 1  # 1 = exploit, 2 = explore, 3 = practise
        self.practise_session = []
        self.practise_answers = []
        self.comp = TreeComparer()

    # this is for debugging
    def print_mode(self):
        modes = ['', 'exploit', 'explore', 'practise']
        return "You are in {} mode".format(modes[self.mode])

    def pick(self):
        #  If we don't yet have the ten random cards, return a random card
        if len(self.random_cards) < self.number_of_initial_questions:
            random_pk = randint(1, self.number_of_cards)
            return Card.objects.get(pk=random_pk)

        # If we do have the random cards and the model in trained:
        else:

            '''
                Modes:
                1 = Exploit mode: Return the card that the user will struggle the most with i.e. the card with the 
                    highest prediction score.
                2 = Explore mode: Return the card where the model is least sure, i.e the card with the highest sigma score.
                3 = Practise mode: The user has answered one card wrong, create a list of similar cards and feed them back, 
                    one at a time. You will also need to keep a count of the right answers          
            '''

            if self.mode == 1:      # -- Exploit mode -- #

                # Get predictions and sigmas
                predictions, sigma = self.gp.predict(np.atleast_2d([range(1, self.number_of_cards)]).T, return_std=True)

                # Take the predictions out of the np array and into python array
                predictions = [x[0] for x in predictions]

                # Find the pk with the highest (worst) predicted score
                max_value, max_pk = predictions[0], 0
                for pk, prediction in enumerate(predictions):
                    if prediction > max_value:
                        max_value = prediction
                        max_pk = pk

                return Card.objects.get(pk=max_pk)

            elif self.mode == 2:    # -- Explore mode -- #

                # Get predictions and sigmas
                predictions, sigmas = self.gp.predict(np.atleast_2d([range(1, self.number_of_cards)]).T, return_std=True)

                # Put the sigma values into simple python array
                sigmas = [x[0] for x in sigmas]

                # Find the pk with the highest sigma (the card that we are least sure about)
                max_value, max_pk = sigmas[0], 0
                for pk, sigma in enumerate(sigmas):
                    if sigma > max_value:
                        max_value = sigma
                        max_pk = pk

                return Card.objects.get(pk=max_pk)

            else:                   # -- Practise mode -- #
                return self.practise_session.pop()

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

            '''
            Here you are no longer in the random stage. The answer can be right or wrong 
            and they can be in one of three modes. 
            Exploit mode just means that we are looking the most difficult card according to the model. If they get the question 
                right here, we don't do anything, but if they get it wrong, we enter practise mode
            
            
            If they are in explore mode, we just pick the card that we are least sure about. But what do we
                do with the answer? Nothing
            If they are in practise mode, you need to deal one of the five questions 
            
            '''

            answer_correct = answer_score == 0

            if self.mode == 1:
                '''
                This is exploit mode. 
                We selected the question that we think they would find the most difficult. 
                If they get this question right we don't need to do anything.
                If they get it wrong, we create the cards for practise mode and switch to practise mode
                '''
                if not answer_correct:
                    # Get a list of all the cards except this one
                    other_cards = [c for c in Card.objects.all() if c != card]

                    # Get a list of tuples of the pks and the comparison values
                    tuples = [(c.pk, self.comp.compare(c, card)) for c in other_cards]

                    sorted_tuples = sorted(tuples, key=lambda item: item[1])

                    # Find the first 5 where the sentence is not the same as the original card
                    practise_cards, i = [], 0
                    while len(practise_cards) < 5:
                        c = Card.objects.get(pk=sorted_tuples[i][0])
                        if c.sentence != card.sentence:
                            practise_cards.append(c)
                        i += 1

                    self.mode = 3

            elif self.mode == 2:
                '''
                This is explore mode. 
                We selected the card that we were least sure about, where the sigma value was highest. 
                If they get the question right, we don't do anything
                If they get the question wrong, we also don't do anything. 
                This aim here to just to add information to the gp
                '''
                pass
            else:  # practise mode
                '''
                This is practise mode. 
                '''

                # add the answer to the list.
                self.practise_answers.append((card.pk, answer_correct))

                # if you have asked all the questions:
                if len(self.practise_session) == 0:
                    # If they get at least three answers correct they have passed
                    passed = len([answer for answer in self.practise_answers if answer[1]]) > 3

                    # If they pass, you can switch back into expoit mode otherwise stay in practise mode
                    # Note: For the moment staying in practise mode will just mean that they will get the exact same
                    # five practise questions again. Eventually you will need to change this.
                    if passed:
                        self.mode = 1












