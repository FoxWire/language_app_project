from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
import numpy as np
import csv
from sklearn.gaussian_process.kernels import RBF, Kernel, StationaryKernelMixin, NormalizedKernelMixin, Hyperparameter
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, ConstantKernel as C
from random import randint, shuffle
from sklearn.model_selection import train_test_split, cross_val_score, KFold
from tqdm import tqdm
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches



class CustomKernel(StationaryKernelMixin, NormalizedKernelMixin, Kernel):

    def __init__(self, length_scale=25.0):

        root = '/home/stuart/PycharmProjects/workspaces/language_app_project/data/'
        file = 'matrix_500.csv'
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


# Read in the question data. Roughly the first 200 odd questions.
def read_user_data():
    dict = {}
    path = '/home/stuart/PycharmProjects/workspaces/language_app_project/data/third_user_function.csv'
    with open(path, 'r') as file:
        reader = csv.reader(file, delimiter=',')
        for row in reader:
            dict[row[0]] = row[1]
    return dict

user = read_user_data()

def ask_user(x):
    y_values = [float(user[str(val[0])]) for val in x]
    return np.atleast_2d(y_values).T

def make_binary(array):
    '''
    Converts the data to 'binary' (1 for a correct answer and -1 for incorrect)
    This can be toggled when the evaluate function is called.
    '''
    x = [[1] if a[0] == 0 else [-1] for a in array]
    # x = [[1] if a[0] >= 0 and a[0] <= 2 else [-1] for a in array]
    return np.atleast_2d(x)


def evaluate(binary=True):

    # Create the kernel and the GP
    kernel = CustomKernel()
    gp = GaussianProcessRegressor(kernel=kernel, optimizer=None, alpha=0.9, normalize_y=True)

    # You need a list of all the question numbers. Because I left out the questions, with uncommon words
    # I can't just use a complete list of pks, because there will be gaps. You need to get the sequence
    # of pks from the user data
    pk_sequence = [int(pk) for pk in user.keys()]
    questions = np.atleast_2d(pk_sequence).T

    # Get the answers to the questions
    answers = ask_user(questions)

    if binary:
        answers = make_binary(answers)
  
    # Get answers to all of the questions
    answers = np.atleast_2d(answers.ravel()).T

    kfold = KFold(n_splits=97)
    results = []

    for train, test in kfold.split(questions):

        X_train, X_test, y_train, y_test = questions[train], questions[test], answers[train], answers[test]
      
        gp.fit(X_train, y_train)

        predictions, sigma = gp.predict(X_test, return_std=True)

        if binary:
            prediction = make_binary(predictions)

        results.append(prediction[0][0] == y_test[0][0])

    correct = results.count(True)
    print("correct:", correct)

if __name__ == '__main__':
    evaluate(binary=True)

    # ones = 0
    # twos = 0
    # threes = 0
    # fours = 0
    # for key, val in user.items():
    #     if int(val) == 1:
    #         ones += 1
    #     elif int(val) == 2:
    #         twos += 1
    #     elif int(val) == 3:
    #         threes += 1
    #     elif int(val) == 4:
    #         fours += 1
    #     else:
    #         print("problem", val)
    #         break

    # print(ones)
    # print(twos)
    # print(threes)
    # print(fours)

'''
In this version of the script, we want to analyse the information that we gathered from Eleni. We will
need to set it up a little differently though because I can no longer just use the 200 first cards because
I decided to remove some of them. 
- get the maximum question number from the user data
- You might need to use a larger matrix too
- There is some other problem here too

- what was the average score? It will be pretty low, due to the hints
'''