#    "Kinetic-Triplet-Determination - prediction" (v1.0)
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

# This program calculates the normalized heat flow measured with a DSC according
# to the given parameters.
# 
# ATTENTION: At one point eval() is used! I've tried to make it as safe as 
# possible. However, that is no guarantee!

import additional_functions as af
import class_definitions as cd
from decimal import Decimal as dec
from copy import deepcopy
import kinetic_function_calculation as kfc

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
	order_of_variables = ['time', 'temperature', 'conversion', 'heat_flow']
	this = 'Time (s)\tTemperature (K)\tConversion\tNormalized Heat Flow (W/g)\n'
	new_data.table_header = this

	return order_of_variables



def main():
	print("""\n\nPredicting DSC heat flow curves.\n
Important: Use the exact (!) parameters for a given dataset -- total heat, compensation parameters (if it is a dynamic measurement), parameters of the kinetic function -- if you want to compare the measured DSC heat flow curves with predicted values. This may be seen as a measure how good the method is in figuring out the kinetic parameters from a given set of data.

Use mean values for all these parameters, to make a more general prediction.

ATTENTION: This program can EITHER predict isothermal heat flow OR the heat flow if a linear (!) temperature ramp is applied.
If a general temperature program shall be predicted the program has to be called again, with changed parameters. E.g. a ramp followed by an isothermal would first simulate the ramp, starting with conversion = 0.0 and having at the end a conversion of 23 percent (for example). Afterwards, a second call of this program predicts the isothermal, taking the 23 percent as initial degree of cure.

ATTENTION: This program assumes that all heat is transported away at once. This is just valid for small samples. The behaviour of large samples, which heat up during the curing process, can NOT be predicted with this simple tool!
""")

	path = af.get_path('Folder where the result shall be stored: ')
	outfile_name = af.get_user_input('outfile')



	this = '\nATTENTION: small time increments and long overall timeframes will '
	that = 'take quite some time to calculate!\n'
	print(this + that)


	timestep = af.get_user_input('timestep')

	text = 'After how many SECONDS shall the calculation latest stop? '
	timeframe = af.get_user_input(text)


	isothermal = af.get_user_input('prediction_mode')


	if not isothermal:
		text = 'Start temperature in KELVIN: '
		start_temperature = af.get_user_input(text)

		end_temperature = af.get_user_input('End temperature in KELVIN: ')

		# I use here as the only place minutes as time, because the ramps
		# in typical DSC instruments are given in Kelvin per minute.
		text = 'Temperature ramp in Kelvin per MINUTE: '

		# The above is just for te convenience of the user. In the end I need
		# this value of course in seconds.
		ramp = af.get_user_input(text) / dec('60.0')
	else:
		text = 'Isothermal temperature in KELVIN: '
		start_temperature = af.get_user_input(text)

		end_temperature = start_temperature
		ramp = dec('0.0')


	# Here the total heat needs to be stated by the user since there is 
	# nothing where it could be calculated from like in all the other cases
	# where rawdata is provided.
	text = 'Total heat of reaction (J/g): '
	total_heat = af.get_user_input(text)


	initial_conversion = af.get_user_input('initial_conversion', True, 'float')

	# Some (kinetic) functions may not work properly if the conversion is zero.
	# So even if it is zero I have to start with a small value.
	if initial_conversion == None:
		initial_conversion = dec('0.0000001')


	conversion_step = af.get_user_input('conversion_step')


	# With the above all is ready to finally create the Prediction() object.
	# All else will be added manually below.
	prediction = cd.Prediction(timestep, timeframe, isothermal, \
					start_temperature, end_temperature, ramp, total_heat, \
					initial_conversion)


	print('\nRegarding the activation energy:')
	activation_energy = cd.UserFunction(conversion_step, timestep)

	prediction.activation_energy = activation_energy


	text = 'Compensation parameter a = '
	# Don't use dec()-numbers here, because these values are needed shortly 
	# after in numpy functions.
	a = float(af.get_user_input(text))

	text = 'Compensation parameter b = '
	b = float(af.get_user_input(text))


	# I want the pre-factors also to be a UserFunctionobject. But the __init__ 
	# of class UserFunction() can not handle to calculate the values from given 
	# third values (which are not the conversion). I could write that, but it 
	# doesn't seem worth it. Thus I simply deepcopy activation_energy, calculate
	# the pre-factor values with calculate_pre_factor() and simply replace
	# the value-attribute with the new list.
	pre_factor = deepcopy(activation_energy)
	new_values = kfc.calculate_pre_factor(a, b, activation_energy)
	pre_factor.values = new_values

	prediction.pre_factor = pre_factor


	print('\n\nRegarding the kinetic function:')
	kinetic_function = cd.UserFunction(conversion_step, timestep)

	prediction.kinetic_function = kinetic_function


	# And finally the thing is happening what I actually wanted to happen.
	# Hey look! It's a one liner ;)
	prediction.predict()


	order_of_variables = create_table_header(prediction)

	outfile = path + outfile_name

	print('\nWriting to File ...')
	af.write_to_file(outfile, prediction, order_of_variables)

	print('')

	this = 'The < {} > file with the predicted values was '.format(outfile_name)
	that = 'created in the stated folder.\n'
	print(this + that)





## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## 
## ## ## ## ## ## ##                            ## ## ## ## ## ## ## 
## ## ## ## ## ## ## PROGRAM IS EXECUTED HERE   ## ## ## ## ## ## ##
## ## ## ## ## ## ##                            ## ## ## ## ## ## ## 
## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## 

# When this program is called on the console, main() is executed.
if __name__ == '__main__':
	main()






















