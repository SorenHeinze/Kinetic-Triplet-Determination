#    "Kinetic-Triplet-Determination - calculate_common_compensation_parameters" (v1.0)
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

# This program calculates the compensation parameters utilizing the 
# compensation effect and several different models defined in models.py
# 
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
# ATTENTION: Fitting will take place between 20 percent and 80 percent
# It is assumed that the data actually reaches 80 percent conversion.

import additional_functions as af
import class_definitions as cd
import os
from copy import deepcopy
import kinetic_functions as kf

## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## 
## ## ## ## ## ## ##                            ## ## ## ## ## ## ## 
## ## ## ## ## ## ## FUNCTION DEFINITIONS HERE  ## ## ## ## ## ## ##
## ## ## ## ## ## ##                            ## ## ## ## ## ## ## 
## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## 


# A second file shall be written per input data in which the model dependent
# Arrhenius pre-factor and activation energy shall be stored. This can not
# be done with the regular write_to_file() function.
# < this_type > can be 'per_model' or 'mean'.
def write_linear_fitting_parameters(outfile, data, this_type):
	model_names = sorted(list(kf.all_models.keys()))
	if this_type == 'per_model':
		with open(outfile, 'w') as f:
			this = 'Compensation parameters for this dataset calculated by '
			that = 'a linear fit of the data given below:\n'
			siht = 'a = {} (J/mol)\tb = {}\n\n\n'.format(data.a, data.b)
			f.write(this + that + siht)

			this = 'Model name\tE for this model\tln(A) for this model\n'
			f.write(this)

			for model_name in model_names:
				activation_energy = getattr(data, '{}_activation_energy'.format(model_name))
				ln_pre_factor = getattr(data, '{}_ln_pre_factor'.format(model_name))

				this = '{}\t{}\t{}\n'.format(model_name, activation_energy, ln_pre_factor)
				f.write(this)

	elif this_type == 'mean':
		# ATTENTION: in this case < data > is a dict!
		a_mean = deepcopy(data['a_mean'])
		b_mean = deepcopy(data['b_mean'])
		# I delete here to make my life below easier.
		del data['a_mean']
		del data['b_mean']

		filenames = sorted(list(data.keys()))

		with open(outfile, 'w') as f:
			this = 'Mean compensation parameters calculated from all '
			that = 'compensation parameters given below:\n'
			siht = 'a_mean = {} (J/mol)\tb_mean = {}\n\n\n'.format(a_mean, b_mean)
			f.write(this + that + siht)

			this = 'Filename\ta (J/mol)\tb\n'
			for filename in filenames:
				this_a = data[filename]['a']
				this_b = data[filename]['b']
				this = '{}\t{}\t{}\n'.format(filename, this_a, this_b)
				f.write(this)



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
	order_of_variables = ['time', 'heat_flow', 'conversion', 'temperature', 'inverse_temperature']
	this = 'Time (s)\tNormalized Heat FLow (W/g)\tConversion\tTemperature (K)\t-1/RT\t'

	model_names = sorted(list(kf.all_models.keys()))
	for model_name in model_names:
		first = '{}_model_values'.format(model_name)
		second = '{}_left_hand_side_values'.format(model_name)

		order_of_variables.append(first)
		order_of_variables.append(second)
		this = this + '{}\t{}\t'.format(first, second)

	# Remove the trailing tab.
	new_data.table_header = this.strip() + '\n'

	return order_of_variables



def main():
	print("""\n\nCalculating the compensation parameters.\n
ATTENTION: It is assumed that the input-files ran through the "step_separator"-program.
Thus the first line in the files is the table header and from the second line follows he data and NOTING else.

ATTENTION: It is assumed that tabs separate the columns.

ATTENTION: The temperature will be converted to KELVIN!

ATTENTION: It is assumed that the input file is baseline corrected (meaning: baseline has a mean heat flow value of zero).

ATTENTION: It is assumed that the data is post-cure run subtracted (if this applies).

ATTENTION: It is assumed that folder contains just files with the relevant data!
That means just data from dynamic experiments

ATTENTION: Fitting will take place between 20 percent and 80 percent. It is assumed that the data actually reaches 80 percent conversion.

ATTENTION: For each input file a file with the calculated parameters and a second file with the calculated functions will be created. Of interest is probably just the file < 00000_compensation_parameters > in which the mean value of all compensation parameters is reported.
""")

	# Get the location of the raw files.
	this = 'Full path of folder with files (ATTENTION: folder shall contain '
	that = 'JUST these files!): '
	path = af.get_path(this + that)


	timestep = af.get_user_input('timestep')
	in_kelvin = af.get_user_input('kelvin')
	total_heat = af.get_user_input('total_heat', True, 'float')
	initial_conversion = af.get_user_input('initial_conversion', True, 'float')


	# That the user does NOT need to delete all the time the file this 
	# program creates these are taken out from the list with the filenames
	# in the folder. This is the reason why the outfile_name(s) are hard coded. 
	# Over many runs it turned out that this is a good thing to do.
	filenames = [x for x in os.listdir(path) if ('0000_calculated' not in x.lower() and \
												'0001_calculated' not in x.lower()) and \
												'00000_activation' not in x.lower() and \
												'00000_compensation' not in x.lower()]

	print('')

	all_compensation_parameters = {}
	all_a = []
	all_b = []
	

	for filename in filenames:
		print("Working on {} ...".format(filename))
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


		print("Calculating the kinetic model values ...")
		data.calculate_left_hand_side()


		print("Fitting ...")
		data.fit_all_for_compensation_parameters()


		all_a.append(data.a)
		all_b.append(data.b)
		all_compensation_parameters.update({filename:{'a':data.a, 'b':data.b}})


		print("Writing calculated values to a file ...")
		outfile_name = '0000_calculated_function_values_{}'.format(filename)
		outfile = path + outfile_name


		order_of_variables = create_table_header(data)
		af.write_to_file(outfile, data, order_of_variables)


		outfile_name = '0001_calculated_fitting_parameters_{}'.format(filename)
		outfile = path + outfile_name
		write_linear_fitting_parameters(outfile, data, 'per_model')


		print()


	a_mean = sum(all_a) / len(all_a)
	b_mean = sum(all_b) / len(all_b)
	all_compensation_parameters.update({'a_mean':a_mean, 'b_mean':b_mean})
	print('\nmean a: {} J/mol, mean b: {}\n'.format(a_mean, b_mean))


	outfile_name = '00000_compensation_parameters.txt'
	outfile = path + outfile_name
	write_linear_fitting_parameters(outfile, all_compensation_parameters, 'mean')

	print()

	this = 'Many new files were created in the stated folder.'
	that = 'Of highest interest is probably < {} >.\n'.format(outfile_name)
	print(this + that)





## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## 
## ## ## ## ## ## ##                            ## ## ## ## ## ## ## 
## ## ## ## ## ## ## PROGRAM IS EXECUTED HERE   ## ## ## ## ## ## ##
## ## ## ## ## ## ##                            ## ## ## ## ## ## ## 
## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## 

# When this program is called on the console, main() is executed.
if __name__ == '__main__':
	main()






















