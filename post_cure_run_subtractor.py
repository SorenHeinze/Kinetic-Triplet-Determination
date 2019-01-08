#    "Kinetic-Triplet-Determination - post_cure_run_subtractor" (v1.0)
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

# This program subtracts the post cure data from the cure data and returns
# a file that contains the subtracted heat flow.
# 
# The time in the new file will be in seconds. however, the temperature will
# not be changed to Kelvin here.
# 
# ATTENTION: It is assumed that cure and post-cure data are in separate files.
# ATTENTION: It is assumed that these two files are in the same folder.
# ATTENTION: It is assumed that these files ran through the "step_separator"-program.
# Thus the first line in the files is the table header and from the second line
# follows he data and NOTING else.
# ATTENTION: It is assumed that tabs separate the columns.
# ATTENTION: This is really just a simple subraction of data, line for line.
# ATTENTION: It is assumed that cure and post-cure run are identical in time 
# steps and temperature for each time step (but not the heat flow of course)
# Meaning: The resultig file will contain time-steps and temperature from
# the cure run!

import additional_functions as af
import class_definitions as cd
from copy import deepcopy

## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## 
## ## ## ## ## ## ##                            ## ## ## ## ## ## ## 
## ## ## ## ## ## ## FUNCTION DEFINITIONS HERE  ## ## ## ## ## ## ##
## ## ## ## ## ## ##                            ## ## ## ## ## ## ## 
## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## 


# Some wiggle-room is necessary because the length of the two datasets
# may be sligthly different. This function checks i the difference is
# within tis wiggle room.
# I arbitrarily choose 10 seconds as possible intervall.
def check_if_length_within_limits(cure_data, post_data, timestep):
	difference =  abs(len(cure_data.heat_flow) - len(post_data.heat_flow))

	if difference * timestep > 10:
		this = "ATTENTION: these two datasets are NOT equally long within 10 seconds!\n"
		that = "Subtraction will take place anyway\nBe aware that the result may be "
		siht = "severely wrong! (This may be the case even if the datasets are equally long)"
		print(this + that + siht)



# This function creates the new, subtracted data.
def subtracted_data(cure_data, post_data, timestep):
	# First: Check if the data actually has heat flow values; if not, return
	if not hasattr(cure_data, 'heat_flow') or not hasattr(post_data, 'heat_flow'):
		print('ATTENTION: No normalized (!) heat flow data in one of the files!')
		print('The program will be aborted')
		return False

	# Second: check if the data is equally long, within 10 seconds.
	# But just give a warning to the user and continue with the rest.
	check_if_length_within_limits(cure_data, post_data, timestep)

	# Third: the new data will have time, temperature (and heat capacity) from 
	# the cure run.
	new_data = deepcopy(cure_data)
	new_data.heat_flow = []

	for i in range(len(cure_data.heat_flow)):
		# Since I do the subtraction even if the datasets are NOT equally long, 
		# I can run into IndexErrors. 
		# Yes, yes, I could first figure out what the shortest dataset is, but
		# well, this is good enough
		try:
			new_value = cure_data.heat_flow[i] - post_data.heat_flow[i]
			new_data.heat_flow.append(new_value)
		except IndexError:
			break

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

	this = '{}\tHeat Flow (Normalized and Post Cure subtracted) (W/g)'.format(new_data.table_header)
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
	print("""\n\nSubtracting the post cure run from the cure run.\n
ATTENTION: It is assumed that cure and post-cure data are in separate files.

ATTENTION: It is assumed that these two files are in the same folder.

ATTENTION: It is assumed that these files ran through the "step_separator"-program.
Thus the first line in the files is the table header and from the second line follows the data and NOTHING else.

ATTENTION: It is assumed that tabs separate the columns.

ATTENTION: This is really just a simple subraction of data, line for line.

ATTENTION: It is assumed that cure and post-cure run are identical in time steps and temperature for each time step (but not the heat flow (or heat capacity) of course).
Meaning 1: The resulting file will contain time-steps and temperature (and heat capacity if it applies) from the cure run!
Meaning 2: If the length of the steps is not identical this program will return bogus!

ATTENTION: The time between two measurements is to be given in SECONDS. The new file
will have this time step in between the measurements. So the time in the new file will be in SECONDS! Not 
minutes as it may be the case with the original file.

ATTENTION: 
Heat Flow: It is assumed that the NORMALIZED Heat Flow is present in the raw-data.
           Not normalized heat flows will be ignored.
Heat Capacity: The heat capacity from the CURE-run will be used. Again, just the 
               NORMALIZED heat capacity will be used.
""")

	path = af.get_path()


	text = 'Name of CURE-run file (incl. extension): '
	cure_file = af.get_infile(path, text)

	text = 'Name of POST-cure-run file (incl. extension): '
	post_file = af.get_infile(path, text)


	outfile_name = af.get_user_input('outfile')


	timestep = af.get_user_input('timestep')


	cure_data = cd.Data(timestep, cure_file)
	post_data = cd.Data(timestep, post_file)


	print("Subtracting ...")
	new_data = subtracted_data(cure_data, post_data, timestep)


	# subtracted_data() has a return condition that does not do anything
	# if the data does not contain heat flow data.
	if new_data:
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






















