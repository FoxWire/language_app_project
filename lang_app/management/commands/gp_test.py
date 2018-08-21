from django.core.management.base import BaseCommand, CommandError
from lang_app.models import Card, Sentence
from utils.comparer.comparer import TreeComparer
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
import numpy as np
import csv
from sklearn.gaussian_process.kernels import RBF, Kernel, StationaryKernelMixin, NormalizedKernelMixin
from random import uniform
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, ConstantKernel as C
'''
This is an inital attempt to get the machine learning stuff working with the rest of the django project.
At the moment, I think I have the kernel working the way it should - there are no errors. 
The kernel is called in the fit function of the GP. The fit function should take questions and answers
and work out the connection between these but the kernel doesn't need to worry about the answers,
or at least I dont' think it does anyway.

It seems like the kernel is also called during the prediction stage. Where it then takes two arguments and 
I haven't yet accounted for that. 


The kernel has an X and Y argument:
when fitting:       x = the questions
                    y = None
when predicting:    x = to_predict
                    y = the questions 

So when it is predicting, it puts the stuff values that we want to predict with the original
questions that we took into the kernel. What does the kernel do with the questions when predicting? 

Getting some differnt errors now. You need to understand what the kernel is doing in each of the operations.

'''


# Dummy function to model the user
def ask_user(x):
    return (x*0.2) * np.sin(x / 10)
            # height      width

class Command(BaseCommand):

    def handle(self, *args, **options):

        # These are the pks of some randomly selected questions that we are asking the user. 
        questions = np.atleast_2d([1, 10, 20, 50, 80]).T

        # We get the answers by putting the questions the dummy user function.
        answers = np.atleast_2d(ask_user(questions).ravel()).T
    
        # Create the custom kernel and GP
        kernel = CustomKernel()
        # kernel = C(1.0, (1e-3, 1e3)) * RBF(10, (1e-2, 1e2))
        gp = GaussianProcessRegressor(kernel=kernel, n_restarts_optimizer=2)

        # Fit the model using the data from the user and the questions
        print("Fitting...")
        gp.fit(questions, answers)

        print("Predicting...")
        # These are the values that we are asking the gp to predict, in order to plot the result
        # to_predict = np.atleast_2d(np.linspace(0, 10, 100)).T
        to_predict = np.atleast_2d([x for x in range(100)]).T

        # make predictions
        y_pred, sigma = gp.predict(to_predict, return_std=True)

        for x, y in zip(to_predict, y_pred):
            print(x, y)

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



class CustomKernel(StationaryKernelMixin, NormalizedKernelMixin, Kernel):


    def __init__(self, length_scale=1.0):

        # Read the csv into memory, there should only be ten items in it at the moment. 
        counter = 0
        array = []
        with open('/home/stuart/Desktop/matrix_100.csv', 'r') as file:
            reader = csv.reader(file, delimiter=',')
            for row in reader:
                float_row = [float(r) for r in row]
                array.append(float_row)
                counter += 1
        self.array = np.array(array)
        self.length_scale = length_scale
        

       
    
    def __call__(self, X, Y=None):
        '''
        Implements this:
        k(xx_i, xx_j) = exp( -1/2 (d(xx_i, xx_j )^2) / length_scale )

        Returns an np array. This is used in the fitting and predicting parts of the GP.
        When fitting only the X argument is provided. In this case we make an array of the 
        disances (in terms of the similarity function) of all the X values from all other 
        X values. If the Y argument is provided, we are predicing. Meaning that we should 
        work out the distances between all X and all Y values.

        In each case we use the values in X (and Y) as indices into the array of precomputed
        distances.        
        '''

        # Uses looping, should be better numpy way of doing this
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
