#    "Kinetic-Triplet-Determination - calculate_activation_energy" (v1.0)
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

# This program calculates the conversion dependent activation energy according
# to the exact isoconversional method.
# 
# ATTENTION: It is assumed that the input-files ran through the 
# "step_separator"-program. Thus the first line in the files is the table 
# header and from the second line follows he data and NOTING else.
# ATTENTION: It is assumed that tabs separate the columns.
# ATTENTION: The temperature will be converted to KELVIN!
# ATTENTION: The normalzided heat flow data will be used.
# ATTENTION: It is assumed that the input file is baseline corrected (meaning:
# baseline has a mean heat flow value of zero) 
# ATTENTION: It is assumed that the data is post-cure run subtracted 
# (if this applies)

import additional_functions as af
import class_definitions as cd
from decimal import Decimal as dec
from copy import deepcopy
import os
from scipy.optimize import minimize
import scipy.integrate as integrate
import numpy as np

## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## 
## ## ## ## ## ## ##                            ## ## ## ## ## ## ## 
## ## ## ## ## ## ## FUNCTION DEFINITIONS HERE  ## ## ## ## ## ## ##
## ## ## ## ## ## ##                            ## ## ## ## ## ## ## 
## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## 


# An experiment may not have reached full conversion but a value smaller
# than 1. It is important to let all algorithms do the things they do just 
# until this value is reached, because otherwise the program will crash 
# because it can not find values above that in the dataset from said experiment.
def find_smallest_conversion(all_data):
	smallest_conversion = dec('1.0')
	for data in all_data:
		# Interesting, isn't it? I'm searching for the maximum to determine
		# the minimal highest conversion ... tihihihi.
		minimum = max(data.conversion_steps)
		if minimum < smallest_conversion:
			smallest_conversion = minimum

	return smallest_conversion



# This function calculates all integrals for a given conversion which are 
# needed to calculate the isoconversional double sum.
# < this_index > is the UPPER integral limit!
# ATTENTION: numpy can NOT work with decimal.Decimal(). Thus I convert 
# everything back :(
def all_integrals(E, all_data, this_index):
	these_integrals = []

	for data in all_data:
		# Get the limits ...
		lower_time = float(data.time_steps[this_index - 1])
		upper_time = float(data.time_steps[this_index])
		lower_temperature = float(data.temperature_steps[this_index - 1])
		upper_temperature = float(data.temperature_steps[this_index])

		# ... then the slope and intercept to calculate the temperature ...
		# Since I calculate the activation energy over time I need to know 
		# how the temperature develops. What I do is that I take the temperature 
		# limits of a given integral and assume that the temperature develops
		# linear.
		slope = (upper_temperature - lower_temperature) / (upper_time - lower_time)
		intercept = upper_temperature - slope * upper_time

		# ... and then integrate :).
		# I don't use any specific rule for integration but .quad() which is
		# general. It should be OK, since I assume rather narrow integration
		# steps. The lambda expression works as the function .quad() shall 
		# over in the given limits.
		integral = integrate.quad(lambda time: np.exp(-E/8.314/(slope * time + intercept)), \
															lower_time, upper_time)[0]

		these_integrals.append(integral)

	return these_integrals



# This function calculates the inner sum with the given parameters.
def inner_sum(i_integral, j_integrals):
	inner_sum = 0.0
	for j_integral in j_integrals:
		inner_sum += i_integral / j_integral

	return inner_sum



# This actually calculates the double sum with the given parameters.
def calculate_double_sum(these_integrals):
	double_sum = 0.0
	# The outer sum counts over i and the inner sum over j.
	for i_integral in these_integrals:
		j_integrals = [x for x in these_integrals if x is not i_integral]

		double_sum += inner_sum(i_integral, j_integrals)

	return double_sum



# This calculates the isoconversional double sum. minimize() needs something 
# to minimize. In this case it is more complicated than a simple function, 
# thus I use this function is a parameter of minimize() and it calls 
# other functions.
# < initial_guess > is the parameter of interest and it will be 
# changed by minimize() until the result calculated in here is minimal.
def double_sum(E, all_data, this_index):
	these_integrals = all_integrals(E, all_data, this_index)

	double_sum = calculate_double_sum(these_integrals)

	return double_sum



# This function minimizes the double sum in the isoconversional equation for 
# a given conversion.
# < all_data > is in order but probably unsorted. However, the latter 
# doesn't matter as long as it is in order.
def outcome_for_one_value(this_index, all_data, initial_guess):
	# See comment to all_integrals() why I convert to float.
	E = float(initial_guess)

	outcome = minimize(double_sum, E, args = (all_data, this_index))

	# 'fun' is the value of the function. It should be n(n - 1) with n
	# as the number of measurements.
	# 'x' is what I'm interested in, the activation energy for the given
	# value of conversion.
	return outcome['x'][0], outcome['fun']




# This function calls more or less all of the above.
def calculate_activation_energy(all_data, initial_guess):
	# Get the list with the steps of the desired conversion steps ...
	smallest_conversion = find_smallest_conversion(all_data)
	# ... but don't get higher than possible. See comment to 
	# find_smallest_conversion()
	conversion_steps = [x for x in all_data[0].conversion_steps if x <= smallest_conversion]
	activation_energies = []
	control_parameters = []

	# Don't calculate anything for time = 0!
	for i in range(1, len(conversion_steps)):
		this_conversion = conversion_steps[i]
		activation_energy, control_parameter = outcome_for_one_value(i, \
														all_data, initial_guess)

		# 'fun' is the value of the function. It should be n(n - 1) with n
		# as the number of measurements.
		# 'x' is what I'm interested in, the activation energy for the given
		# value of conversion.
		activation_energies.append(activation_energy)
		control_parameters.append(control_parameter)

		this = '{}\t{}\t{}'.format(this_conversion, activation_energy, \
															control_parameter)
		print(this)

	# conversion_steps still contains the zero value as the first element, as 
	# it is needed for the very first step of the above procedure. However, 
	# activation_energies and control_parameters don't have this value. 
	# Thus the zero at the beginning is popped before all is returned.
	conversion_steps.pop(0)

	return conversion_steps, activation_energies, control_parameters



def main():
	print("""\n\nCalculating the conversion dependent activation energy.\n
ATTENTION: It is assumed that the input-files ran through the "step_separator"-program.
Thus the first line in the files is the table header and from the second line follows he data and NOTING else.

ATTENTION: It is assumed that tabs separate the columns.

ATTENTION: The temperature will be converted to KELVIN!

ATTENTION: This program will work JUST over time, NOT over temperature. It should be the same though!

ATTENTION: The normalzided heat flow data will be used.

ATTENTION: It is assumed that the input file is baseline corrected (meaning: baseline has a mean heat flow value of zero).

ATTENTION: It is assumed that the data is post-cure run subtracted (if this applies).

ATTENTION: It is assumed that folder contains just files with the relevant data!
E.g. just the isothermal data from several experiments at different temperatures.
""")

	# Get the location of the raw files.
	this = 'Full path of folder with files (ATTENTION: folder shall contain '
	that = 'JUST these files!): '
	path = af.get_path(this + that)

	timestep = af.get_user_input('timestep')
	in_kelvin = af.get_user_input('kelvin')
	total_heat = af.get_user_input('total_heat', True, 'float')
	initial_conversion = af.get_user_input('initial_conversion', True, 'float')

	conversion_step = af.get_user_input('conversion_step')

	text = 'Initial guess for the activation energy in J/mol: '
	initial_guess = af.get_user_input(text)


	# Yes, this is a hard coded filename.
	outfile_name = '00000_Activation_energies.txt'
	outfile = path + outfile_name


	# So that the user does NOT need to delete all the time the file with the
	# calculated activation energies, I take it out of the list with the 
	# filenames. This is the only exception from the rule stated above and the
	# reason why the outfile_name is hard coded. Over many runs it turned out
	# that this is a good thing to do.
	filenames = [x for x in os.listdir(path) if '00000_activation' not in x.lower()]

	print('')


	all_data = []

	for filename in filenames:
		print("Working on {} ...".format(filename))
		data = cd.Data(timestep, path + filename)


		data.in_kelvin = in_kelvin
		if not in_kelvin:
			print("Setting temperature to Kelvin ...")
		# create_temperature_in_kelvin() will be called even is the temperature
		# is already in Kelvin, because it contains a check if the data 
		# actually has temperature data. This is just a check, which is probably
		# not necessary.
		data.create_temperature_in_kelvin()

		if not total_heat:
			print("Calculating total heat of reaction ...")
			data.calculate_total_heat_of_reaction()
		else:
			data.total_heat = deepcopy(total_heat)


		print("Calculating the conversion ...")
		data.calculate_conversion(total_heat, initial_conversion)


		data.conversion_step = conversion_step

		print("Finding the time and temperature values for the integral limits ...")
		data.find_values_for_isoconversion()


		all_data.append(data)
		print('------')


	conversion_steps, activation_energies, \
					control_parameters = calculate_activation_energy(all_data, \
																	initial_guess)


	with open(outfile, 'w') as f:
		this = 'conversion\tActivation Energy (J/mol)\tControl Parameter\n'
		f.write(this)
		for i in range(len(conversion_steps)):
			this = "{}\t{}\t{}\n".format(conversion_steps[i], \
									activation_energies[i], control_parameters[i])
			f.write(this)


	this = '\nA new file called < {} > '.format(outfile_name)
	that = 'was created in the same folder.' 
	print(this + that)





## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## 
## ## ## ## ## ## ##                            ## ## ## ## ## ## ## 
## ## ## ## ## ## ## PROGRAM IS EXECUTED HERE   ## ## ## ## ## ## ##
## ## ## ## ## ## ##                            ## ## ## ## ## ## ## 
## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## 

# When this program is called on the console, main() is executed.
if __name__ == '__main__':
	main()






















