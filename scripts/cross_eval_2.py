from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
import numpy as np
import csv
from sklearn.gaussian_process.kernels import RBF, Kernel, StationaryKernelMixin, NormalizedKernelMixin
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, ConstantKernel as C
from random import randint, shuffle
from sklearn.model_selection import train_test_split, cross_val_score

# Django stuff
# import os
# import sys
# import django
# sys.path.append('/home/stuart/PycharmProjects/workspaces/language_app_project')
# os.environ['DJANGO_SETTINGS_MODULE'] = 'language_app_project.settings'
# django.setup()

# from lang_app.models import Card, Sentence
# from utils.comparer.comparer import TreeComparer



class CustomKernel(StationaryKernelMixin, NormalizedKernelMixin, Kernel):

    def __init__(self, length_scale=100):

        # Read the csv into memory, there should only be 100 items in it at the moment. 
        path = '/home/stuart/PycharmProjects/workspaces/language_app_project/data/matrix_100.csv'
        array = []
        with open(path, 'r') as file:
            reader = csv.reader(file, delimiter=',')
            for row in reader:
                float_row = [float(r) for r in row]
                array.append(float_row)
        self.array = np.array(array)
        self.length_scale = length_scale
        

    def __call__(self, X, Y=None):
        '''
        Implements this:
        k(xx_i, xx_j) = exp( -1/2 (d(xx_i, xx_j )^2) / length_scale )

        Returns an np array. This is used in the fitting and predicting parts of the GP.
        When fitting, only the X argument is provided. In this case we make an array of the 
        disances (in terms of the similarity function) of all the X values from all other 
        X values. If the Y argument is provided, we can assume that we are predicing,
        meaning that we should work out the distances between all X and all Y values.

        In each case we use the values in X (and Y) as indices into the array of precomputed
        distances.        
        '''

        values_X = X[:, 0]
        values_Y = Y[:, 0] if Y is not None else values_X

        x = self.array[[values_X], :][0]
        x = x[:, [values_Y]].reshape(len(values_X), len(values_Y))
        
        kernel = np.exp(-.5 * (x**2) / self.length_scale)
        return np.atleast_2d(kernel)

# Read in the precomputed user answers to the 100 questions
def read_user_data():
    dict = {}
    path = '/home/stuart/PycharmProjects/workspaces/language_app_project/data/user_function.csv'
    with open(path, 'r') as file:
        reader = csv.reader(file, delimiter=',')
        for row in reader:
            dict[row[0]] = row[1]
    return dict

user = read_user_data()

def ask_user(x):
    y_values = [float(user[str(val[0])]) for val in x]
    return np.atleast_2d(y_values).T

def evaluate():

    # Create the kernel and the GP
    kernel = CustomKernel()
    gp = GaussianProcessRegressor(kernel=kernel, optimizer=0, alpha=1)

    # Get all of the availiable questions
    questions = np.atleast_2d(range(1, 100)).T

    # Get answers to all of the questions
    answers = np.atleast_2d(ask_user(questions).ravel()).T

    scores = []
    number_of_folds = 1
    for i in range(number_of_folds):

        # Split the data
        X_train, X_test, y_train, y_test = train_test_split(questions, answers, 
                                                            test_size=0.1, random_state=randint(1, 100))
        # Fit the data
        gp.fit(X_train, y_train)

        # make predictions
        predictions, sigma = gp.predict(X_test, return_std=True)

            for x in predictions:
                print(x)
        
        # get the mean squared error
        mse = ((predictions - y_test)**2).mean()
        scores.append(mse)

    # convert the scores array to np array
    scores = np.array(scores)
    print(scores)
    # print the mean score over all of the folds
    print("Accuracy: %0.2f (+/- %0.2f)" % (scores.mean(), scores.std() * 2))


if __name__ == '__main__':
   print("Evaluation:")   
   evaluate()