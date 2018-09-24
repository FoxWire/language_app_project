import csv

with open('/home/stuart/PycharmProjects/workspaces/language_app_project/data/matrix_2000.csv', 'r') as file:
	    reader = csv.reader(file, delimiter=',')
	    row_counter = 1
	    correct_size = 1989
	    counter_correct = 0
	    counter_incorrect = 0
	    incorrect_line_numbers = []
	    for row in reader:
	    	if len(row) != correct_size:
	    		counter_incorrect += 1
	    		incorrect_line_numbers.append(row_counter)
	    	else:
	    		counter_correct += 1
	    	row_counter += 1

	    print("Result:")
	    print("Number of rows with correct length: {}".format(counter_correct))
	    print("Number of rows with wrong length: {}".format(counter_incorrect))
	    if incorrect_line_numbers:
	    	print("These lines have incorrect rows:")
	    	print(incorrect_line_numbers)
	      
