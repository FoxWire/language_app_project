import os
import sys
import django

sys.path.append('/home/stuart/PycharmProjects/workspaces/language_app_project')
os.environ['DJANGO_SETTINGS_MODULE'] = 'language_app_project.settings'
django.setup()

import csv
import numpy as np
from lang_app.models import Card, Sentence
from utils.comparer.comparer import TreeComparer

'''
The initialiser takes a path, it reads in from the path to create a numpy array.
This allows you to interact with the underlying matrix.
Only requires the upper triangle of the matrix. 
'''

class MatrixWrapper:

	def __init__(self, path):

		with open(path, 'r') as file:
			matrix = []
			reader = csv.reader(file, delimiter=',')
			for row in reader:
				matrix.append(row)
		self.matrix = np.array(matrix)

	def get(self, x, y, use_pks=True):

		if use_pks:
			x -= 1  
			y -= 1

		if x == y:
			return 0.0

		# If you know you are accessing a value in the lower triangle, you can 
		# just flip the coordinates and get the value form the upper triangle
		if x > y:
			x, y = y, x

		return float(self.matrix[x, y])

		# elif x > y:
		# 	# You are in the lower triangle
		# 	return float(self.matrix[y, x])
		# else:
		# 	# You are in the upper triangle
		# 	return float(self.matrix[x, y])
		


if __name__ == '__main__':
	
	comp = TreeComparer()
	wrapper = MatrixWrapper('/home/stuart/PycharmProjects/workspaces/language_app_project/data/matrix_1989.csv')
	card_a = Card.objects.get(pk=100)
	card_b = Card.objects.get(pk=567)

	val = comp.compare(card_a, card_b)

	assert val == wrapper.get(card_a.pk, card_b.pk)
	assert val == wrapper.get(card_b.pk, card_a.pk)
	assert 0.0 == wrapper.get(card_b.pk, card_b.pk)
	print('tests completed')



	