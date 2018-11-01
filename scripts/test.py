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

        you could pad out the indices so that they are the same length and then just chop the 
        stuff off that you don't need
        '''

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
        return np.atleast_2d(kernel)

    def new_call(self, X, Y=None):

        values_X = X[:, 0]
        values_Y = Y[:, 0] if Y is not None else values_X

        x = self.array[[values_X], :][0]
        x = x[:, [values_Y]].reshape(len(values_X), len(values_Y))
        
        kernel = np.exp(-.5 * (x**2) / self.length_scale)
        return np.atleast_2d(kernel)


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



if __name__ == '__main__':


    questions = np.atleast_2d([1, 10, 20, 50, 80]).T
    to_predict = np.atleast_2d(range(1, 10)).T

    kernel = CustomKernel()

    # x = kernel(questions, to_predict)

    # a = np.arange(9).reshape((3, 3))
    # print(a)

    # x = a[[0, 2], :]
    # y = x[:, [1]]

    # print(y)

    # questions = [0, 3, 4]
    # to_predict = [1, 3]

    # array = np.arange(25).reshape((5, 5))
    # print(array)
    # print()
    # x = array[questions, :]


    # x = x[:, to_predict]
    # print(x)

    # array = kernel.array
  

    # Here we need to take the two dimensional array and get a one dimensional array from it
    # you use the comma to select each dimension that you want. The colon accesses everything on that
    # dimension as usual in python lists. So here you are getting everything on the first dimension and 
    # the zeros on the second dimension
    # question = questions[:, 0]
    # to_predic = to_predict[:, 0]


    # Next we need to use the two arrays that we have just created as indices into the array
    # when we put an array into a slice, it uses the values in the array as indices, so here we are saying
    # use each fo the values in questions as indeceis of the array and get the whole dimenesion at each index
    # 
    # x = array[[question], :][0]
    # x = x[:, [to_predic]].reshape(len(question), len(to_predic))
    # # print(x)

    # actual_thing = kernel(questions, to_predict)
    
    # print(actual_thing)    

    # print(x == actual_thing)


    '''
    ^^^^This stuff above should actually work^^^^

    The last time I was looking at this, I was trying to get the custom kernal working using a more numpy approach
    instead of the looping. How did I do this? 
    '''
    
    
    a = kernel(questions, to_predict)
    print(a)

    b = kernel.new_call(questions, to_predict)
    print(b)

    print(a == b)
 


