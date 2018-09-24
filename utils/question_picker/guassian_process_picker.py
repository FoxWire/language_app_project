from utils.comparer.comparer import TreeComparer
from lang_app.models import Card
from random import randint
from tqdm import tqdm
import json


class GaussianProcessPicker:
    '''
        The naive picker just picks the next most similar card that doesn't have the same sentence
        as the previous card if the user gets the question wrong and a random card if they get it right.

        The GP picker will use the gaussian process to work out which card should come next. This will be the simplest
        implementation of the GP:
        - ask the user ten random questions
        - fit the model to the questions
        - then find the question that they are most likely to get wrong and ask that.
        - retrain the model on that.


    '''

    def __init__(self):
        pass

    def pick(self, card, answered_correctly):
        pass





