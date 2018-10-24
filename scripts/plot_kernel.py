from sklearn.manifold import TSNE
# import matplotlib.pyplot as plt
import numpy as np
import csv
from sklearn.gaussian_process.kernels import RBF, Kernel, StationaryKernelMixin, NormalizedKernelMixin, Hyperparameter
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, ConstantKernel as C
from random import randint, shuffle
from sklearn.model_selection import train_test_split, cross_val_score
from tqdm import tqdm
import matplotlib.patches as mpatches

from matplotlib import pyplot as plt


class CustomKernel(StationaryKernelMixin, NormalizedKernelMixin, Kernel):

    def __init__(self, length_scale=100.0):

        root = '/home/stuart/PycharmProjects/workspaces/language_app_project/data/'
        file = 'matrix_201.csv'
        path = root + file

        # Read in from the file
        temp_array = []
        with open(path, 'r') as file:
            reader = csv.reader(file, delimiter=',')
            for row in reader:
                float_row = [float(r) for r in row]
                temp_array.append(float_row)

        np_array = np.array(temp_array)

        '''
        For some of the larger arrays, I am only computing half of the values because of the 
        time needed for the tree comparison to run on all questions. The next block just checks
        if only half of the array is present and mirrors it.
        '''
        if not (np_array[0] == np_array[:, 0, None].T[0]).all():
            # Use mask to combine the array and the transposed array.
            mask = np_array != 0
            np_array.T[mask] = np_array[mask]

        self.array = np_array
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

 # Read in the 200 questions. 
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

def run():

    '''
    Here we just put the questions into the kernel function and show the 
    results on an image plot. To see if there are any patterns
    in the kernel. 
    '''

    kernel = CustomKernel()

	# get all the sentence scores from the user
    questions = np.atleast_2d(range(1, 200)).T

	# Get the answers to the questions
    answers = ask_user(questions)

	# Get answers to all of the questions
    answers = np.atleast_2d(answers.ravel()).T

    results = kernel(questions)

    plt.imshow(results, interpolation='nearest')
    plt.show()


if __name__ == '__main__':
	print("running")
	run()
	print("complete")

