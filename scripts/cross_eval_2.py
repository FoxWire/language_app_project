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

    def __init__(self, length_scale=0.4):

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


        '''
        In order to use the log_marginal_likelihood function on the gp, the custom kernel has to register
        the hyperparameters. I also had to override the Hyperparameter getters and setters.
        '''
  
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

def make_binary(array):
    '''
    Converts the data to 'binary' (1 for a correct answer and -1 for incorrect)
    This can be toggled when the evaluate function is called.
    '''
    x = [[1] if a[0] <= 2 else [-1] for a in array]
    # x = [[1] if a[0] >= 0 and a[0] <= 2 else [-1] for a in array]
    return np.atleast_2d(x)


def evaluate(binary=True):

    # Create the kernel and the GP
    kernel = CustomKernel()
    gp = GaussianProcessRegressor(kernel=kernel, optimizer=None, alpha=0.9, normalize_y=True)

    # Get all of the availiable questions
    questions = np.atleast_2d(range(1, 201)).T

    # Get the answers to the questions
    answers = ask_user(questions)

    if binary:
        answers = make_binary(answers)
  
    # Get answers to all of the questions
    answers = np.atleast_2d(answers.ravel()).T

    kfold = KFold(n_splits=200)
    results = []

    for train, test in kfold.split(questions):

        X_train, X_test, y_train, y_test = questions[train], questions[test], answers[train], answers[test]
      
        gp.fit(X_train, y_train)

        predictions, sigma = gp.predict(X_test, return_std=True)

        if binary:
            prediction = make_binary(predictions)

        results.append(prediction[0][0] == y_test[0][0])

    correct = 0
    for x in results:
        if x:
            correct += 1

    print(correct)




        # Split the data   
        # X_train, X_test, y_train, y_test = train_test_split(questions, answers, 
        #                                                     test_size=0.005, random_state=x)
      

        # # Fit the data
        # gp.fit(X_train, y_train)

        # # Make predictions on the test data, to get test error
        # predictions, sigma = gp.predict(X_test, return_std=True)

        # if binary:
        #     predictions = make_binary(predictions)
      
        # test_error = np.abs((predictions - y_test).mean())
        # test_errors.append(test_error)

        # # Collect results from testing to make the plot
        # master_predictions.append(predictions[0][0])
        # master_y_test.append(y_test[0][0])

        # # Make predictions on the training data to get the training error
        # predictions_train, sigma_train = gp.predict(X_train, return_std=True)
        # training_error = np.abs((predictions_train - y_train).mean())
        # training_errors.append(training_error)

        # # Collect data on training to make the second plot
        # master_predictions_train.append(predictions_train[0][0])
        # master_y_train.append(y_train[0][0])

    # # Convert the scores array to np array
    # test_errors = np.array(test_errors)
    # training_errors = np.array(training_errors)
    # # Print the mean score over all of the folds
    # print("Test error: %0.2f (+/- %0.2f)" % (test_errors.mean(), test_errors.std() * 2))
    # print("Training error: %0.2f (+/- %0.2f)" % (training_errors.mean(), training_errors.std() * 2))
    # print()

    # '''
    # If you are not converting the data to binary, you still need to truncate the 
    # predicted values that are below zero to zero.
    # '''
    # if not binary:
    #     master_predictions = [x if x > 0 else 0 for x in master_predictions]

    # # Plot the test and the training data
    # plot(master_y_test, master_predictions)
    # # plot(master_y_train, master_predictions_train)


def plot(master_y_test, master_predictions):
    # Plot the data
    red_patch = mpatches.Patch(color='red', label='Predictions')
    blue_patch =mpatches.Patch(color='blue', label='Observed')

    plt.legend(handles=[red_patch, blue_patch])
    plt.scatter([x for x in range(1, len(master_y_test) + 1)], master_y_test, c='blue', marker='.')
    plt.scatter([x for x in range(1, len(master_predictions) + 1)], master_predictions, c='red', marker='.')
    plt.xlabel('question number')
    plt.ylabel('score');
    plt.show()


if __name__ == '__main__':
  
   '''
   Set binary to true to have values set to 1 for correct 
   and -1 for wrong. Otherwise the full range of values is
   used.
   '''
   evaluate(binary=True)

   # X = ["a", "b", "c", "d"]
   # kf = KFold(n_splits=4)
   # for train, test in kf.split(X):
   #      print("%s %s" % (train, test))
  

'''
Here we split the test data up into test and training and do the kfold evaluation.
The result is that it got just more than half right. 
'''