#    "Kinetic-Triplet-Determination - correct_baseline_to_zero" (v1.0)
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

# This program calculates the mean heat flow value from the last last 5 minutes 
# and 23 seconds of a file and  subtracts this value from all the data.
# 
# The time in the new file will be in seconds. However, the temperature will
# not be changed to Kelvin here.
# 
# ATTENTION: It is assumed that the heat flow does actually reach steady state
# for the last 5 minutes and 23 seconds.
# ATTENTION: It is assumed that the files ran through the "step_separator"-program.
# Thus the first line in the file is the table header and from the second line
# follows he data and NOTING else.
# ATTENTION: It is assumed that tabs separate the columns.
# ATTENTION: This is really just a simple shift of the data so that the steady 
# state is at value zero.


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

	this = '{}\tHeat Flow (Normalized and baseline corrected) (W/g)'.format(new_data.table_header)
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
	print("""\n\nCorrecting the baseline to zero\n

ATTENTION: It is assumed that the file ran through the "step_separator"-program. Thus the first line in the files is the table header and from the second line follows he data and NOTING else.

ATTENTION: It is assumed that tabs separate the columns.

ATTENTION: This is really just the simple subtraction of a value from the heat flow data.

ATTENTION: The time between two measurements is to be given in SECONDS. The new file will have this time step in between the measurements. So the time in the new file will be in SECONDS! Not minutes as it may be the case with the original file.

ATTENTION: 
Heat Flow: It is assumed that the NORMALIZED Heat Flow is present in the raw-data. Not normalized heat flows will be ignored. If no normalized heat flow data is available the program will crash
Heat Capacity: If heat capacity data is present just the NORMALIZED heat capacity will be used.
""")

	path = af.get_path()
	infile = af.get_infile(path)


	outfile_name = af.get_user_input('outfile')


	timestep = af.get_user_input('timestep')


	this = 'Steady state (normalized) heat flow '
	that = '(leave EMPTY if it shall be calculated from the data itself): '
	text = this + that
	steady_state_heat_flow = af.get_user_input(text, True, 'float')
	intervall = None


	if steady_state_heat_flow == None:
		this = 'Intervall (in SECONDS) over which the steady (normalized) heat '
		that = 'flow shall be calculated (leave EMPTY to use 5 minutes 23 '
		siht = 'seconds = 323 seconds): '
		text = this + that + siht
		intervall = af.get_user_input(text, True, 'float')


	# I always call the data "new_data", thus I keep this here, even though it
	# would not be necessary!
	new_data = cd.Data(timestep, infile)


	print('')

	print('Correcting the baseline ...')
	new_data.correct_baseline(steady_state_heat_flow, intervall)


	# If the steady state heat flow can NOT be calculated 
	# data._calculate_steady_state_heat_flow() writes a note to the user and
	# returns False and subsequently data.correct_baseline sets 
	# data.baseline_corrected to False and returns False. 
	# Don't continue if this happens.
	if not new_data.baseline_corrected:
		return

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






















