# -*- coding: utf-8 -*- 

#    "Kinetic-Triplet-Determination - main" (v1.0)
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

# In general will all of these programs do things in relation with the 
# isoconversional method to figure out the conversion dependent activation
# energy, the Arrhenius pre-factor and it will calculate the actual kinetic
# function regarding the cure of a polymer. 
# All the above will be done by taking DSC files wich contain the heat flow data.
# 
# With given parameters can the heat flow be predicted.
# 
# The DSC rawdata files usually need to be modified (not the values of course)
# to be able to work with it. Programs to do the most common things are 
# provided, too
# 
# Lastly I give some hints how to get the best results.
# 
# So the name of the program is a bit misleading, since it does much more than
# this.
# 
# ATTENTION: It is everywhere assumed that the user is actally reading and following 
# the instructions. I usually don't check for wrong user input and this will
# (usually) crash the program(s).

# This is the main-file which is to be called and will ask the user what to do 
# and it will then call all other programs for the actions that shall be performed.
# 
# This is just for user-convenience. All programs can be run separately.

import step_separator as sep
import post_cure_run_subtractor as sub
import stitch_steps_together as sst
import correct_baseline_to_zero as cb
import total_heat_calculator as thc
import conversion_into_file as cif
import calculate_activation_energy as cae
import calculate_common_compensation_parameters as cccp
import kinetic_function_calculation as kfc
import prediction as pre
import dsc_tips as dt

def users_choice():
	allowed = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'k', 'l']

	print('''
ATTENTION: It is everywhere assumed that the user is actally reading and following the instructions. 
I usually don't check for wrong user input and this will (usually) crash the program(s).

What do you want to do?
Calculate activation energy using the exact isoconversional method ...... => A
Calculate the compensation parameters using the compensation effect ..... => B
Calculate the actual kinetic function ................................... => C
Predict the heat flow ................................................... => D

Additional options:
Separate steps from DSC-raw data file ................................... => E
Stitch together several steps ........................................... => F
Subtract post cure run from cure run .................................... => G
Correct baseline to zero ................................................ => H
Calculate total heat .................................................... => I
Create file that contains also the conversion ........................... => K

How to use the programs and DSC / data hints ............................ => L
''')

	while True:
		do_this = input('Your choice (letter followed by ENTER): ').strip().lower()

		if (do_this in allowed) or (do_this == ''):
			return do_this
		else:
			this = '\nERROR! Just the following choices can be made: '
			that = 'A, B, C, D, E, F, G, H, I, K, L.\n'
			print(this + that)




if __name__ == '__main__':
	loop = True

	while loop:
		do_this = users_choice()

		if do_this == 'a':
			cae.main()
		elif do_this == 'b':
			cccp.main()
		elif do_this == 'c':
			kfc.main()
		elif do_this == 'd':
			pre.main()
		elif do_this == 'e':
			sep.main()
		elif do_this == 'f':
			sst.main()
		elif do_this == 'g':
			sub.main()
		elif do_this == 'h':
			cb.main()
		elif do_this == 'i':
			thc.main()
		elif do_this == 'k':
			cif.main()
		elif do_this == 'l':
			dt.main()
		else:
			pass

		do_more = input('\n\nDo you want to do more exciting tings? (Y or N): ').lower()
		if ('yes' in do_more) or (do_more == 'y'):
			pass
		elif ('no' in do_more) or (do_more == 'n'):
			loop = False
		else:
			print('\nEverthing except "no" or "n" is interpreted as yes.\n\n')
	
print('\nThank you for using this program :) .\n')






















