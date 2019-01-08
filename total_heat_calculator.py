#    "Kinetic-Triplet-Determination - total_heat_calculator" (v1.0)
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

# This program simply adds up the normalized heat flow which is the total
# heat of reaction per gram.
# 
# ATTENTION: It is assumed that the input-file ran through the 
# "step_separator"-program. Thus the first line in the files is the table 
# header and from the second line follows he data and NOTING else.
# ATTENTION: It is assumed that tabs separate the columns.
# ATTENTION: This is really just a simple addition of data
# ATTENTION: It is assumed that the input file is baseline corrected (meaning:
# baseline has a mean heat flow value of zero) 
# ATTENTION: It is assumed that the data is post-cure run subtracted 
# (if this applies)

import additional_functions as af
import class_definitions as cd

## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## 
## ## ## ## ## ## ##                            ## ## ## ## ## ## ## 
## ## ## ## ## ## ## FUNCTION DEFINITIONS HERE  ## ## ## ## ## ## ##
## ## ## ## ## ## ##                            ## ## ## ## ## ## ## 
## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## 


def main():
	print("""\n\nCalculating the total heat of reaction.\n
ATTENTION: It is assumed that the input-file ran through the "step_separator"-program. 
Thus the first line in the files is the table header and from the second line follows he data and NOTING else.

ATTENTION: It is assumed that tabs separate the columns.

ATTENTION: It is assumed that the data is post-cure run subtracted (if this applies).

ATTENTION: It is assumed that the input file is baseline corrected (meaning: steady state has a mean heat flow value of zero)

ATTENTION: The returned value will be in Joule per GRAM! 

ATTENTION: This is really just a simple addition of data.
""")

	path = af.get_path()
	infile = af.get_infile(path)


	timestep = af.get_user_input('timestep')


	data = cd.Data(timestep, infile)


	data.calculate_total_heat_of_reaction()

	print('')

	this = "The total heat of reaction is {} J/g.\n".format(data.total_heat) 
	print(this)





## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## 
## ## ## ## ## ## ##                            ## ## ## ## ## ## ## 
## ## ## ## ## ## ## PROGRAM IS EXECUTED HERE   ## ## ## ## ## ## ##
## ## ## ## ## ## ##                            ## ## ## ## ## ## ## 
## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## 

# When this program is called on the console, main() is executed.
if __name__ == '__main__':
	main()






















