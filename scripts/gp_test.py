from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
import numpy as np
import csv
from sklearn.gaussian_process.kernels import RBF, Kernel, StationaryKernelMixin, NormalizedKernelMixin
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, ConstantKernel as C

'''

'''


# Dummy function to model the user
def ask_user(x):
    return (x*0.2) * np.sin(x / 10)
            # height      width

class CustomKernel(StationaryKernelMixin, NormalizedKernelMixin, Kernel):


    def __init__(self, length_scale=1.0):

        # Read the csv into memory, there should only be 100 items in it at the moment. 
        array = []
        with open('matrix_100.csv', 'r') as file:
            reader = csv.reader(file, delimiter=',')
            for row in reader:
                float_row = [float(r) for r in row]
                array.append(float_row)
        self.array = np.array(array)
        # length scale currently not used.
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

if __name__ == '__main__':

    # Represent the pks of some randomly selected questions that we will initally ask the user
    questions = np.atleast_2d([1, 10, 20, 50, 80]).T

    # We get the answers by putting the questions into the dummy user function.
    answers = np.atleast_2d(ask_user(questions).ravel()).T

    # Create the custom kernel
    kernel = CustomKernel()
    # Or user the exiting kernel for testing
    # kernel = C(1.0, (1e-3, 1e3)) * RBF(10, (1e-2, 1e2))

    gp = GaussianProcessRegressor(kernel=kernel, n_restarts_optimizer=2)

    # Fit the model using the data from the user and the questions
    print("Fitting...")
    gp.fit(questions, answers)

    print("Predicting...")
    # These are the values that we are asking the gp to predict, in order to plot the result
    to_predict = np.atleast_2d([x for x in range(100)]).T

    # make predictions
    y_pred, sigma = gp.predict(to_predict, return_std=True)

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