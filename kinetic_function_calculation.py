#    "Kinetic-Triplet-Determination - calculate_kinetic_function" (v1.0)
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

# This program calculates the kineitc function from the given data.
# The user has to provide either a file with the conversion dependent 
# activation energy or has to provide a parametrization of the same.
# 
# ATTENTION: It is assumed that the input-files ran through the 
# "step_separator"-program. Thus the first line in the files is the table 
# header and from the second line follows he data and NOTING else.
# ATTENTION: It is assumed that tabs separate the columns.
# ATTENTION: The temperature will be converted to KELVIN!
# ATTENTION: It is assumed that the input file is baseline corrected (meaning:
# baseline has a mean heat flow value of zero) 
# ATTENTION: It is assumed that the data is post-cure run subtracted 
# (if this applies).
# ATTENTION: At one point eval() is used! I've tried to make it as safe as 
# possible. However, that is no guarantee!

import additional_functions as af
import class_definitions as cd
from copy import deepcopy
import os
import numpy as np
import kinetic_functions as kf

## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## 
## ## ## ## ## ## ##                            ## ## ## ## ## ## ## 
## ## ## ## ## ## ## FUNCTION DEFINITIONS HERE  ## ## ## ## ## ## ##
## ## ## ## ## ## ##                            ## ## ## ## ## ## ## 
## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## 


# This function does what its name says.
# < activation_energy > is a class UserFunction() object.
def calculate_pre_factor(a, b, activation_energy):
	pre_factors = []
	for value in activation_energy.values:
		this = np.exp(kf.linear_function(float(value), a, b))
		pre_factors.append(this)

	return pre_factors



# This function calculates the actual kinetic function for the given dataset.
def calculate_kinetic_function(data):
	R = 8.314
	kinetic_function_values = []

	for i in range(len(data.conversion)):
		heat_flow = float(data.heat_flow[i])
		activation_energy = float(data.activation_energy[i])
		pre_factor = float(data.pre_factor[i])
		temperature = float(data.temperature[i])

		rate_constant = 1.0 / (pre_factor * np.exp(-activation_energy / R / temperature))

		value = heat_flow * rate_constant
		kinetic_function_values.append(value)

	data.kinetic_function = kinetic_function_values



# The highly variable table header needs extra work *rolleyes*
# I want the variables in a certain order, even though these may have been
# in a different order in the rawdata.
# 
# ATTENTION: This is also the only place where I execute direct control over
# some aspects of the data. 
# The table header shall mirror the content of the rows in the file in which 
# the data will be written later. Thus I need to return the order of the 
# variables in the table header.
# I keep the parameter name as "new_data" just because it is called like that
# in other files.
def create_table_header(new_data):
	order_of_variables = ['conversion', 'kinetic_function', 'heat_flow', \
								'temperature', 'activation_energy', 'pre_factor']
	this = 'Conversion\tActual Kinetic Function\tNormalized Heat FLow (W/g)\t'
	that = 'Temperature (K)\tActivation Energy (J/mol)\tPre-Factor'

	new_data.table_header = this + that + '\n'

	return order_of_variables



def main():
	print("""\n\nCalculating the actual kinetic function.\n
ATTENTION: It is assumed that the input-files ran through the "step_separator"-program.
Thus the first line in the files is the table header and from the second line follows he data and NOTING else.

ATTENTION: It is assumed that tabs separate the columns.

ATTENTION: The temperature will be converted to KELVIN!

ATTENTION: It is assumed that the input file is baseline corrected (meaning: baseline has a mean heat flow value of zero).

ATTENTION: It is assumed that the data is post-cure run subtracted (if this applies).

ATTENTION: It is assumed that folder contains just files with the relevant data!
And (if it applies) the file with the conversion dependent activation energy.
""")

	# Get the location of the raw files.
	this = 'Full path of folder with files (ATTENTION: folder shall contain '
	that = 'JUST these files!): '
	path = af.get_path(this + that)


	timestep = af.get_user_input('timestep')
	in_kelvin = af.get_user_input('kelvin')
	total_heat = af.get_user_input('total_heat', True, 'float')
	initial_conversion = af.get_user_input('initial_conversion', True, 'float')


	text = 'Compensation parameter a = '
	# Don't use dec()-numbers here, because these values are needed shortly 
	# after in numpy functions.
	a = float(af.get_user_input(text))

	text = 'Compensation parameter b = '
	b = float(af.get_user_input(text))


	conversion_step = af.get_user_input('conversion_step')


	print('\nRegarding the activation energy:')
	activation_energy = cd.UserFunction(conversion_step, timestep)

	# I want the pre-factors also to be a UserFunctionobject. But the __init__ 
	# of class UserFunction() can not handle to calculate the values from given 
	# third values (not the conversion). I could write that, but it doesn't
	# seem worth it. Thus I simply deepcopy activation_energy, calculate
	# the pre-factor values with calculate_pre_factor() and simply replace
	# the value-attribute with the new list.
	pre_factors = deepcopy(activation_energy)
	new_values = calculate_pre_factor(a, b, activation_energy)
	pre_factors.values = new_values

	print()


	# That the user does NOT need to delete all the time the file this 
	# program creates these are taken out from the list with the filenames
	# in the folder. This is the reason why the outfile_name(s) are hard coded. 
	# Over many runs it turned out that this is a good thing to do.
	filenames = [x for x in os.listdir(path) if ('0000_calculated' not in x.lower() and \
												'0001_calculated' not in x.lower()) and \
												'00000_activation' not in x.lower() and \
												'00000_compensation' not in x.lower() and \
											'000_actual_kinetic_function' not in x.lower()]

	print('')


	for filename in filenames:
		print("\nWorking on {} ...".format(filename))
		data = cd.Data(timestep, path + filename)


		data.in_kelvin = in_kelvin
		if not in_kelvin:
			print("Setting temperature to Kelvin ...")
		# create_temperature_in_kelvin() will be called even if the temperature
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

		# I need of course just the heat flow values for the given conversion
		# steps.
		data.heat_flow = data._get_correct_values_from_file(activation_energy.conversion, \
															data.conversion, data.heat_flow)

		# Dito for the temperature.
		data.temperature = data._get_correct_values_from_file(activation_energy.conversion, \
															data.conversion, data.temperature)

		# And finally just the necessary conversion steps.
		data.conversion = activation_energy.conversion

		data.activation_energy = activation_energy.values
		data.pre_factor = pre_factors.values


		# This is what I'm here for.
		calculate_kinetic_function(data)


		outfile_name = '000_actual_kinetic_function_{}'.format(filename)
		#print("Writing calculated values to a file ...")
		outfile = path + outfile_name


		order_of_variables = create_table_header(data)
		af.write_to_file(outfile, data, order_of_variables)

		print()


	this = 'Many new files were created in the stated folder containing the '
	that = 'actual kinetic function for each raw-data file.\n'
	print(this + that)





## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## 
## ## ## ## ## ## ##                            ## ## ## ## ## ## ## 
## ## ## ## ## ## ## PROGRAM IS EXECUTED HERE   ## ## ## ## ## ## ##
## ## ## ## ## ## ##                            ## ## ## ## ## ## ## 
## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## 

# When this program is called on the console, main() is executed.
if __name__ == '__main__':
	main()






















