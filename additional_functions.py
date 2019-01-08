#    "Kinetic-Triplet-Determination - additional_functions" (v1.0)
#    Copyright 2018 Soren Heinze
#    soerenheinze (at) gmx (dot) de
#    5B1C 1897 560A EF50 F1EB 2579 2297 FAE4 D9B5 2A35
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

# This file contains functions which are used by several programs or just put 
# here to keep the actual program files cleaner.

from decimal import Decimal as dec
import os

# ATTENTION: To many parameters can be wrong or non-existing. Thus I simply
# assume that everything is alright.
# Dear user, if you want to, you can easily crash the program.
# < data > is a class Data object. 
def write_to_file(outfile, data, order_of_variables):
	length = len(getattr(data, order_of_variables[0]))

	with open(outfile, 'w', encoding='utf8') as f:
		f.write(data.table_header)

		for i in range(length):
			this = ''
			for variable in order_of_variables:
				value = getattr(data, variable)[i]
				this = '{}\t{}'.format(this, value)

			# Strip the trailing tab at the beginning and add a linebreak.
			this = this.strip() + '\n'
			f.write(this)


 
# To make the main()-functions of the programs more tidy.
# This function checks if a folder actually exists.
# < text > can be a text to be displayed since it may be necessary to provide
# the user with a bit more information than the short standard text.
def get_path(text = None):
	if not text:
		text = 'Full path to folder with file(s): '

	path = ''
	while not os.path.isdir(path):
		# Get the location of the raw files.
		path = input(text)
		if not os.path.isdir(path):
			print('ERROR: Folder does not exist. Please try again.\n')

	return path



# Like get_path() just for files.
# < This function asks JUST for the filename. The path to the actual file has
# to be provided so that it can be checked if the file actually exists.
# < allow_blank > is for the case that a blank input is used to give the system
# certain information (e.g. to use default values).
def get_infile(path, text = None, allow_blank = False):
	if not text:
		text = 'Name of file (incl. extension): '

	infile = path
	while not os.path.isfile(infile):
		filename = input(text)

		if allow_blank and filename == '':
			return True

		infile = path + filename
		if not os.path.isfile(infile):
			print('ERROR: File does not exist. Please try again.\n')

	return infile



# Before I inroduced this function the program crashed all the time when e.g.
# an int was expected but a string was put in. 
# Now I check for such things for most of the user inputs.
# < this_type > is the expected type of the user input. If multiple choices
# are possible (e.g. 'y' or 'n' for 'yes' or 'no' it will be a list with the
# choices.
def correct_user_input(user_input, this_type):
	# < this_type > can be a list if several answer options are possible. If 
	# this function is then called with user_input = None (as usual) the 
	# else => else-case will be triggered already when entering this function.
	# This will lead to displaying a message which is not even applicable and
	# would unnecessarily confuse the user. Thus I created an artificial case
	# user_input = 'risimif' to avoid this.
	if user_input == 'risimif':
		return False
	elif this_type == 'float':
		try:
			float(user_input)
			return True
		except (ValueError, TypeError):
			return False
	elif this_type == 'int':
		try:
			int(user_input)
			return True
		except (ValueError, TypeError):
			return False
	else:
		if user_input.lower() in this_type:
			return True
		else:
			this = 'Please use one of these inputs: {}'.format(this_type)
			print(this)
			return False
	


# This is just to make the main functions of the programs bit more tidy.
# Usually user input is converted to a dec()-number. However, I had implemented
# that the user can leave an input empty to signal that something shall be 
# calculated directl from the data. In this case the user input would be < '' >
# and the value was (is) set to None.
def convert_input(user_input):
	if user_input == None:
		return None
	else:
		return dec(user_input)



# Just to make the main()-functions of the programs more tidy.
# Yes, this is just a long function with different cases of which some have
# a general component.
# < text > is a string which specifies what to ask for.
# < this_type > is information about what type is expected. Since I mainly 
# expect float-type numbers as user input I've set this as default.
def get_user_input(text, allow_blank = False, this_type = 'float'):
	if text == 'timestep':
		text = 'Time between two measurments in SECONDS (e.g. 0.1): '
	elif text == 'total_heat':
		this = 'Total heat of reaction in J/g (leave EMPTY if it shall be '
		that = 'calculated from the data itself): '
		text = this + that
	elif text == 'initial_conversion':
		this = 'Initial conversion, e.g. 0.23 for 23 % (leave EMPTY if it is '
		that = 'assumed to be zero): '
		text = this + that
	elif text == 'conversion_step':
		this = 'Conversion increment for which the activation energy or function '
		that = 'shall be calculated (e.g. 0.001 for every 0.1 percent)\n'
		siht = 'ATTENTION: too low a value will lead to very long calculation '
		taht = 'times. Recommended is to stay above 0.01 percent: '
		text = this + that + siht + taht

	# These functions to make the program more user friendly were coded after
	# all else was done. Thus certain functions or parameters were in use so
	# often that it was simpler to NOT generalize them and have a special case
	# for them here.
	# If the temperature is in Kelvin is one such parameter
	elif text == 'kelvin':
		this = 'Is the temperature in KELVIN (Y = Yes, N = NO = it is in '
		that = 'degrees Celsius): '
		text = this + that

		# Here I need something else than None, because in correct_user_input()
		# it is checked if the users answer is part of the allowed elements
		# in the list and that doesn't work for None. "risimif" is obviously
		# not part of the list.
		user_input = 'risimif'
		while not correct_user_input(user_input, ['y', 'n', 'yes', 'no']):
			user_input = input(this + that)

		if user_input.lower() == 'y' or user_input.lower() == 'yes':
			return True
		else:
			return False

	elif text == 'outfile':
		user_input = ''
		this = 'How shall the the file with the results be called: '
		while user_input == '':
			user_input = input(this)

		return user_input

	elif text == 'number_of_functions':
		this = 'Number of different functions used for parametrization of the '
		that = 'function (H for Help / examples): '
		text = this + that

		user_input = None
		while not correct_user_input(user_input, 'int'):
			user_input = input(this + that)
			if user_input.lower() == 'h' or user_input.lower() == 'help':
				print_parametrization_help_text()

		return int(user_input)

	elif text == 'prediction_mode':
		this = 'What shall be predicted? Isothermal (I) or linear '
		that = 'temperature ramp (R)? '
		text = this + that

		user_input = 'risimif'
		while not correct_user_input(user_input, ['i', 'r']):
			user_input = input(this + that)

		if user_input.lower() == 'i':
			return True
		else:
			return False


	user_input = None
	while not correct_user_input(user_input, this_type):
		user_input = input(text).replace(',', '.')
		if allow_blank and user_input == '':
			user_input = None
			break

	this_value = convert_input(user_input)

	return this_value



# Just to print some information to the user. This is needed at two places, 
# thus it ended up here.
def print_parametrization_help_text():
	this = '\nHelp regarding the Number of different functions used for '
	that = 'parametrization of the activation energy.' 
	print(this + that)

	this = '\nExample 1: the function can be described over the whole conversion '
	that = 'range with one function (probably a constant).\nNumber of different '
	siht = 'functions used for parametrization = 1\n'
	print(this + that + siht)

	this = 'Example 2: the function can be described in the conversion '
	that = 'range between 0.0 to 0.2 as a constant, between 0.2 and 0.8 as a second '
	siht = 'order polynom and between 0.8 and 1.0 again as a constant.\n'
	taht = 'Number of different functions used for parametrization = 3\n'
	print(this + that + siht + taht)

	input('Press ENTER to continue.')



# To provide the user with examples how to write the function in a way that 
# it can be evaluated as function. This is needed at two places, thus it ended 
# up here.
def print_function_input_help_text():
	print('\nHelp regarding the input of functions.')
	print('\nATTENTION: DO NOT USE DOUBLE UNDERSCORES < __ >. THESE WILL BE DELETED!')
	print('\nIMPORTANT: Use CAPITAL < X > for the conversion!')

	this = '\nIMPORTANT: Every (!) number needs a decimal point, e.g. 23.0 '
	that = 'for the number 23.'
	print(this + that)

	this = '\nSymbols for regular operations (without the " < > ").\nAddition: '
	that = '< + >, subtraction: < - >, multiplication: < * >, division: < / >.\n'
	siht = 'Exponentiation: < ** > (TWO asterisk followed by the exponent).\n'
	taht = 'Parenthsis: < ( ) > (Use JUST round parenthesis).'
	print(this + that + siht + taht)

	this = '\nUse numpy-expressions for all other mathematical expressions.\n'
	that = 'Sinus etc.: < np.sin(X)>, e-function: < np.exp(X)>, natural (!) '
	siht = 'logarithm: < np.log(X) >'
	print(this + that + siht)

	this = '\nExample 1 - activation eneryg is constant at value 23 kJ/mol.\n'
	that = 'Input needs to be: 23000.0'
	print(this + that)

	this = '\nExample 2 - activation eneryg is linear dependent on conversion:\n'
	that = 'Input needs to be (numbers are made up!): 23000.0 + 42000.0*X'
	print(this + that)

	this = '\nExample 3 - activation eneryg is a second order polynom:\n'
	that = 'Input needs to be (numbers are made up!): 23000.0 + 42000.0*X - 5000.0*X**2.0'
	print(this + that)

	this = '\nExample 4 - activation eneryg is square root dependent of conversion:\n'
	that = 'Input needs to be: X**(1.0/2.0)'
	print(this + that)

	this = '\nExample 5 - activation eneryg is logarithmically dependent of '
	that = 'conversion:\nInput needs to be: np.log(X)'
	print(this + that)

	input('\nPress ENTER to continue')






















