#    "Kinetic-Triplet-Determination - stitch_steps_together" (v1.0)
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

# This program stitches several steps of the DSC experiment together.
# 
# The time in the new file will be in seconds. However, the temperature will
# not be changed to Kelvin here.
# 
# ATTENTION: It is assumed that the steps are separate files.
# ATTENTION: It is assumed that these files are in the same folder.
# ATTENTION: It is assumed that these files ran through the "step_separator"-program.
# Thus the first line in the files is the table header and from the second line
# follows he data and NOTING else.
# ATTENTION: It is assumed that tabs separate the columns.
# ATTENTION: This is really just a simple putting the data of one step behind 
# the other, line for line.
# ATTENTION: It is assumed that step one actually is followed by step two is
# followed by step three etc.
# ATTENTION: It is assumed that the files actually belong together and thus
# contain the same same variables. If this is not the case, certain functions
# will break! I don't test for all the stuff the user could do wrong!

import additional_functions as af
import class_definitions as cd
from copy import deepcopy

## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## 
## ## ## ## ## ## ##                            ## ## ## ## ## ## ## 
## ## ## ## ## ## ## FUNCTION DEFINITIONS HERE  ## ## ## ## ## ## ##
## ## ## ## ## ## ##                            ## ## ## ## ## ## ## 
## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## 


# Just to keep stitched_together() more tidy.
def add_these_values(new_data, variable, these_values):
	# I'm a bit unsure with deep copies and shallow copies and so on
	# I'm pretty sure it would be ok without the deepcopy(), but to be sure
	# I have it here. I'm not overly concerned about memory or performance.
	new_values = deepcopy(getattr(new_data, variable))
	for value in these_values:
		new_values.append(value)

	setattr(new_data, variable, new_values)



# This function does the stitching of the files.
def stitched_together(all_data, timestep):
	new_data = deepcopy(all_data.pop(0))

	for this_data in all_data:
		for variable in new_data.variables:
			these_values = getattr(this_data, variable)
			add_these_values(new_data, variable, these_values)

	# ATTENTION: new_data.number_of_measurements has still the information
	# from the file new_data was copied from! Thus it needs to be updated ...
	new_data.number_of_measurements = len(new_data.time)
	# ... to be able to update the time-attribute.
	new_data._create_time_in_seconds()

	return new_data



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

	this = '{}\tHeat Flow (Normalized) (W/g)'.format(new_data.table_header)
	new_data.table_header = this
	order_of_variables.append('heat_flow')

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
	print("""\n\nStitching several steps together into one file\n
ATTENTION: It is assumed that the steps are separate files.

ATTENTION: It is assumed that these files are in the same folder.

ATTENTION: It is assumed that these files ran through the "step_separator"-program. Thus the first line in the files is the table header and from the second line follows he data and NOTING else.

ATTENTION: It is assumed that tabs separate the columns.

ATTENTION: This is really just a simple putting the data of one step behind the other, line for line.

ATTENTION: It is assumed that step one actually is followed by step two is followed by step three etc.

ATTENTION: It is assumed that all files have the same time step between measurements

ATTENTION: It is assumed that step one actually is followed by step two is followed by step three etc.
THIS WILL NOT BE CHECKED!

ATTENTION: The time between two measurements is to be given in SECONDS. The new file will have this time step in between the measurements. So the time in the new file will be in SECONDS! Not minutes as it may be the case with the original file.

ATTENTION: 
Heat Flow: It is assumed that the NORMALIZED Heat Flow is present in the raw-data. Not normalized heat flows will be ignored.
Heat Capacity: If heat capacity data is present just the NORMALIZED heat capacity will be used.
""")

	path = af.get_path()

	# Since I want to loop until all filenames are provided I can not 
	all_filenames = []
	i = 1
	loop = True
	while loop:
		this = 'Name of file #{} (incl. extension) -- '.format(i)
		that = 'press just ENTER to continue to next step: '
		text = this + that

		infile = af.get_infile(path, text, True)

		# af.get_infile() returns True if I allow a blank input.
		if infile == True and i > 2:
			loop = False
		elif infile == True:
			print("I won't stop asking before more than one filename is provided.")
		else:
			all_filenames.append(infile)
			i += 1


	outfile_name = 	outfile_name = af.get_user_input('outfile')


	timestep = af.get_user_input('timestep')


	all_data = []
	for infile in all_filenames:
		data = cd.Data(timestep, infile)
		all_data.append(data)

	print('')


	print("Stitching ...")
	new_data = stitched_together(all_data, timestep)

	print('')


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






















