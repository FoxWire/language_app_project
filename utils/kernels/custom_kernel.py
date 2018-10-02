import numpy as np
import csv
from sklearn.gaussian_process.kernels import Kernel, StationaryKernelMixin, NormalizedKernelMixin


class CustomKernel(StationaryKernelMixin, NormalizedKernelMixin, Kernel):

    def __init__(self, length_scale=100):


        '''
            The custom kernel basically needs to access all comparison values between all cards and apply a
            transformation to them. Because the function to compare two cards uses the tree comparison algorithm, this
            is an expensive operation for all 2000 cards and so we read in the precomputed values from file.

            For speed we only actually compute half the values and then the kernel builds up the other half in memory.
        '''

        root = '/home/stuart/PycharmProjects/workspaces/language_app_project/data/'
        file = 'matrix_1989.csv'
        path = root + file

        # Read in from the file
        temp_array = []
        with open(path, 'r') as file:
            reader = csv.reader(file, delimiter=',')
            for row in reader:
                float_row = [float(r) for r in row]
                temp_array.append(float_row)

        np_array = np.array(temp_array)

        # Check if the first x axis is the same as the first y axis, if so, the array is symmetrical
        if not (np_array[0] == np_array[:, 0, None].T[0]).all():

            # Use mask to combine the array and the transposed array.
            mask = np_array != 0
            np_array.T[mask] = np_array[mask]

        self.array = np_array
        self.length_scale = length_scale

    def __call__(self, x, y=None, eval_gradient=False):
        '''
            Implements this:
            k(xx_i, xx_j) = exp( -1/2 (d(xx_i, xx_j )^2) / length_scale )

            Returns an np array. This is used in the fitting and predicting parts of the GP.
            When fitting, only the X argument is provided. In this case we make an array of the
            distances (in terms of the similarity function) of all the X values from all other
            X values. If the Y argument is provided, we can assume that we are predicting
            meaning that we should work out the distances between all X and all Y values.

            In each case we use the values in X (and Y) as indices into the array of precomputed
            distances.
        '''

        values_x = x[:, 0]
        values_y = y[:, 0] if y is not None else values_x

        x = self.array[[values_x], :][0]
        x = x[:, [values_y]].reshape(len(values_x), len(values_x))

        kernel = np.exp(-.5 * (x ** 2) / self.length_scale)
        return np.atleast_2d(kernel)


if __name__ == "__main__":
    c = CustomKernel()
    a = c.array
    assert (a[0] == a[:, 0, None].T[0]).all()
    print("Complete")



