from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
import numpy as np
import csv
from sklearn.gaussian_process.kernels import RBF, Kernel, StationaryKernelMixin, NormalizedKernelMixin
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, ConstantKernel as C
from random import randint

# Django stuff
import os
import sys
import django
sys.path.append('/home/stuart/PycharmProjects/workspaces/language_app_project')
os.environ['DJANGO_SETTINGS_MODULE'] = 'language_app_project.settings'
django.setup()

from lang_app.models import Card, Sentence
from utils.comparer.comparer import TreeComparer

'''
Initial attempt at getting the Gaussian Process to work with the custom kernel.
Feedback from Bjorn:
- It doesn't make sense to try to plot the points on a graph, because you don't have a sensible scale.
It seems that the RBG algorithm does work in a different way.
- There should be an optimiser parameter on the GP, this should be set to zero
- You need to test the kernel outside of the GP to make sure that it is working
- You will need to make a new user function
- You can also play around with the length scale.
'''

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

        # print("x", X)
        # print("y", Y)
        # Uses looping, should be better numpy way of doing this, but this works for now
        optional = Y if Y is not None else X
        values_X = [ob[0] for ob in X]
        values_Y = [ob[0] for ob in optional]

        outer = []
        for i in values_X:
            inner = []
            for j in values_Y:
                inner.append(self.array[i, j])
            outer.append(inner)
        outer = np.array(outer)

        kernel = np.exp(-.5 * (outer**2) / self.length_scale)
        print(np.atleast_2d(kernel))
        return np.atleast_2d(kernel)

def plot(questions, to_predict, y_pred, sigma):
    '''
    This probably won't be needed
    '''
    # Plotting the results
    print("Plotting...")
    plt.plot(to_predict, ask_user(to_predict), 'r:', label=u'$user(x) = x\,\sin(x)$')  # plot the actual function line in red (colon makes dotted)
    plt.plot(questions, answers, 'r.', markersize=10, label=u'Observations')  # plot the observations
    plt.plot(to_predict, y_pred, 'b-', label=u'Prediction')
    # plt.fill(np.concatenate([to_predict, to_predict[::-1]]),
    #          np.concatenate([y_pred - 1.9600 * sigma,
    #                         (y_pred + 1.9600 * sigma)[::-1]]),
    #          alpha=.5, fc='y', ec='None', label='95% confidence interval')
    plt.xlabel('$x$')
    plt.ylabel('$f(x)$')
    plt.ylim(-10, 20)
    plt.legend(loc='upper left')
    plt.show()

# # Dummy function to model the user
# def ask_user(x):
#     return (x*0.2) * np.sin(x / 10)
#             # height      width


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


def test_kernel():
    kernel = CustomKernel()

    # take two pks and get the comparison from them directly out of the array

    for x in range(1, 101):
        a, b = randint(1, 100), randint(1, 100)
        value = kernel.array[a, b]
        # transform this via the algorithm
        transformed_value = np.exp(-.5 * (np.atleast_2d([value])**2) / 100)

        # compute this via the kernel
        other_value = kernel(np.atleast_2d([a]), np.atleast_2d([b]))
        assert transformed_value == other_value

    print('tests completed')


if __name__ == '__main__':

    # Represent the pks of some randomly selected questions that we will initally ask the user
    questions = np.atleast_2d([1, 10, 20, 50, 80]).T

    # # We get the answers by putting the questions into the dummy user function.
    answers = np.atleast_2d(ask_user(questions).ravel()).T

    # # Create the custom kernel
    kernel = CustomKernel()
    # # Or user the existing kernel for testing
    # # kernel = C(1.0, (1e-3, 1e3)) * RBF(10, (1e-2, 1e2))

    gp = GaussianProcessRegressor(kernel=kernel, optimizer=0)

    # # Fit the model using the data from the user and the questions
    # print("Fitting...")
    gp.fit(questions, answers)

    # print("Predicting...")
    # # These are the values that we are asking the gp to predict, in order to plot the result
   

    # # make predictions
    y_pred, sigma = gp.predict(to_predict, return_std=True)
    # print(y_pred)
    # print(sigma)

    # print(ask_user(np.atleast_2d([60])))

    # Just for testing, work out the average difference between the observed values and the predictions
    # user_numbers = [user[str(x)] for x in range(1, 101)]
    # predictions = [gp.predict(np.atleast_2d([x]).T)[0][0] for x in range(1, 100)]
    # total_diff = 0
    # for a, b in zip(user_numbers, predictions):
    #     total_diff += abs(float(a) - b)
    # print(total_diff / 100)

    # lets get some numbers and look at sigmas
    # y_pred, sigma = gp.predict(np.atleast_2d([range(1, 99)]).T, return_std=True)
    # print(sigma)

    # test_kernel()

    # Try and find the lowest and highest sigma values
    # lowest = sigma[0]
    # highest = sigma[0]
    # for x in sigma:
    #     if x > highest:
    #         highest = x
    #     if x < lowest:
    #         lowest = x

    # print(lowest, highest)

