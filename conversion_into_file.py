#    "Kinetic-Triplet-Determination - conversion_into_file" (v1.0)
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

# This program calculates the conversion for eac time from the given 
# heat flow values
# 
# The time in the new file will be in seconds. However, the temperature will
# not be changed to Kelvin here.
# 
# ATTENTION: It is assumed that the files ran through the "step_separator"-program.
# Thus the first line in the file is the table header and from the second line
# follows he data and NOTING else.
# ATTENTION: It is assumed that tabs separate the columns.
# ATTENTION: It is assumed that the data is post-cure and baseline corrected.
# The program does NOT check for this! But if this is not the case the program
# will run anyway and return bogus!
# However, it is NOT necessar that the sample reached full cure, if a value 
# for the total heat of reaction is provided.

import additional_functions as af
import class_definitions as cd

## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## 
## ## ## ## ## ## ##                            ## ## ## ## ## ## ## 
## ## ## ## ## ## ## FUNCTION DEFINITIONS HERE  ## ## ## ## ## ## ##
## ## ## ## ## ## ##                            ## ## ## ## ## ## ## 
## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## 


# The highly variable table header needs extra work *rolleyes*
# I want the variables in a certain order, even though these may have been
# in a different order in the rawdata.
# 
# ATTENTION: This is also the only place where I execute direct control over
# some aspects of the data. 
# The table header shall mirror the content of the rows in the file in which 
# the data will be written later. Thus I need to return the order of the 
# variables in the table header.
def create_table_header(new_data):
	order_of_variables = ['time']
	new_data.table_header = 'Time (s)'

	# I don't know in which unit the temperature is (or if it even is in the
	# data at all). Fortunately the table header of the rawdata is still 
	# available :) .
	for variable in new_data.original_variables:
		if 'temperature' in variable.lower():
			this = '{}\t{}'.format(new_data.table_header, variable)
			new_data.table_header = this
			order_of_variables.append('temperature')

	this = '{}\tHeat Flow (Normalized)) (W/g)'.format(new_data.table_header)
	new_data.table_header = this
	order_of_variables.append('heat_flow')

	this = '{}\tConversion'.format(new_data.table_header)
	new_data.table_header = this
	order_of_variables.append('conversion')

	# Like for temperature, I don't know if heat capacity data is available
	# However, IF it is available it will always be the normalized heat capacity
	# since this is taken care of in class Data().
	if hasattr(new_data, 'heat_capacity'):
		this = '{}\t{}'.format(new_data.table_header, variable)
		new_data.table_header = this
		order_of_variables.append('heat_capacity')

	new_data.table_header = new_data.table_header + '\n'

	return order_of_variables



def main():
	print("""\n\nCalculate conversion and write to file.\n
ATTENTION: It is assumed that the files ran through the "step_separator"-program.
Thus the first line in the file is the table header and from the second line follows he data and NOTING else.

ATTENTION: It is assumed that tabs separate the columns.

ATTENTION: It is assumed that the data is post-cure and baseline corrected. The program does NOT check for this!
If this is not the case the program will run anyway and return bogus!
However, it is NOT necessar that the sample reached full cure, if a value for the total heat of reaction is provided.

ATTENTION: The time between two measurements is to be given in SECONDS. The new file
will have this time step in between the measurements. So the time in the new file will be in SECONDS! Not 
minutes as it may be the case with the original file.

ATTENTION: 
Heat Flow: It is assumed that the NORMALIZED Heat Flow is present in the raw-data.
           Not normalized heat flows will be ignored.
Heat Capacity: Just the NORMALIZED heat capacity will be printed into the to the new file!
""")

	path = af.get_path()
	infile = af.get_infile(path)


	outfile_name = af.get_user_input('outfile')


	timestep = af.get_user_input('timestep')
	total_heat = af.get_user_input('total_heat', True, 'float')
	initial_conversion = af.get_user_input('initial_conversion', True, 'float')


	new_data = cd.Data(timestep, infile)


	print("Calculating the conversion ...")
	new_data.calculate_conversion(total_heat, initial_conversion)


	order_of_variables = create_table_header(new_data)

	outfile = path + outfile_name
	print("Writing to file ...\n")
	af.write_to_file(outfile, new_data, order_of_variables)

	print('A new file called < {} > was created in the same folder.'.format(outfile_name))





## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## 
## ## ## ## ## ## ##                            ## ## ## ## ## ## ## 
## ## ## ## ## ## ## PROGRAM IS EXECUTED HERE   ## ## ## ## ## ## ##
## ## ## ## ## ## ##                            ## ## ## ## ## ## ## 
## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## 

# When this program is called on the console, main() is executed.
if __name__ == '__main__':
	main()






















