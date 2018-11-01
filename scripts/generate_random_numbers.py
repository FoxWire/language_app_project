# Generate some random numbers

from random import shuffle

path = "/home/stuart/PycharmProjects/workspaces/language_app_project/data/rand_nums.csv"
with open(path, 'a') as file:

	numbers = [x for x in range(1, 201)]
	shuffle(numbers)
	for n in numbers:
		file.write(str(n))
		file.write('\n')
