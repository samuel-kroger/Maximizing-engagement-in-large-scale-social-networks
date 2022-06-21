import re

ext = "./porta/porta-1.4.1/win32/bin/"
filename = "prop_1_2.txt.poi.ieq"
file = open(ext + filename)
read_lines = file.readlines()

def find_num(string, number):
	index = 0

	if number <= 9:
		for char in string:
			if char.isdigit():
				if int(char) == number:

					return index + 2
			index += 1
	else:
		for i in range(0, len(string)):
			if string[i].isdigit() and string[i+1].isdigit():
				if int(string[i] + string[i+1]) == number:
					return index + 3

			index += 1


counter = 0
for line in read_lines:
	if counter == 0:
		x_var_num = int((line.strip()[6:]))
		print ("$\\begin{array}{" + "c"* (x_var_num + 1)+ "}")

	if counter >= 6:
		#print("Line{}: {}".format(counter, line.strip()[5:]))

		latex_str = ""
		first_equality_found = False
		in_bracket = False


		#print(line)
		for char in line.strip()[5:]:
			if char != " ":
				if in_bracket:
					if not char.isdigit():
						latex_str += "}"
						in_bracket = False

				if char.isdigit():
					latex_str += char

				if char == "x":
					latex_str += char + "_{"
					in_bracket = True
				if char == "+" or char == "-":
					latex_str += char

				if not first_equality_found:
					if char == "=":
						latex_str += " &="
						first_equality_found = True
					if char == "<":
						latex_str += " &\\leq "
						first_equality_found = True

		latex_str += "\\\\"


		left_str = ""
		right_str = ""
		encountered_space = False

		for char in latex_str:
			if char.isspace():
				encountered_space = True

			if encountered_space == False:
				left_str += char
			else:
				right_str += char




		numbers = [int(num) for num in re.findall(r'\b\d+\b', left_str)]


		if len(numbers) != 0:
			left_str = ("&" * (numbers[0] - 1)) + left_str
			left_str = left_str + ("&" * (x_var_num - numbers[-1]))
		if len(numbers) >= 2:
			i = 0
			#print(left_str)
			#print(numbers)
			for i in range(len(numbers)- 1):
				current_num = numbers[i]
				next_num = numbers[i+1]
				num_index = find_num(left_str, current_num)
				#print(next_num - current_num)
				left_str = left_str[:num_index] + ("&" * (next_num - current_num)) + left_str[num_index:]
				#print(left_str)
		#print(left_str)


		print(left_str + right_str)
		#print(left_str)
	counter += 1

print("\\end{array}$")