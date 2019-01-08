#    "Kinetic-Triplet-Determination - class definitions" (v1.0)
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

# This file contains the definitions of the classes which are used by several 
# programs.

from decimal import Decimal as dec
from copy import deepcopy
import kinetic_functions as kf
import numpy as np
from scipy.optimize import curve_fit
import additional_functions as af
# When I use eval() i try to catch common errors. Since eval() is very 
# powerful it can do much more than just calculate a value from a given 
# string. Thus it may return something which is OK for eval() but not 
# for the dec()-operation afterwards which uses the eval()-output. This 
# will raise a decimal-error and for that I need the whole module.
import decimal

# This is basically just a data container in which each the most attribute are
# all the data for one variable for one step of one eperiment.
# The "one step" condition above is relaxed, and these can be several steps 
# if the steps are properly "stithced together".
# 
# It takes a list of the variables and a list which contains as elements the
# rawdata for each measurement-point. The latter is another list with the
# values for each variable in the same order as the variables.
# 
# ATTENTION: instances of this class contain JUST the normalized heat flow and
# heat capacity values!
# 
# < timestep > already comes as dec()-number.
class Data(object):
	def __init__(self, timestep, infile):
		self.original_variables, rawdata = self._extract_data(infile)
		print("Structuring data ...")
		self.variables = []
		self.timestep = timestep
		self.number_of_measurements = len(rawdata)
		# Here self.indices and self.variables are created. The former is the 
		# information where in the rawdata the specific information can be found
		# for a variable stored in the latter.
		self._create_variable_indices()
		# Here the data-attributes are created. These are lists which contain 
		# the data for each timestep
		self._create_data_attributes(rawdata)
		self._make_all_data_equally_long()
		# The timestep may be in minutes in the original file. I need it to be
		# in seconds. Thus I overwrite the time data here.
		self._create_time_in_seconds()


	# This function extracts the data from a simple txt-file and returns the data
	# line by line but already separated into the entries.
	# ATTENTION: It is assumed that tabs separate the columns.
	# ATTENTION: It is assumed that the first line contains the variables.
	# ATTENTION: It is assumed that the file contains from the second line on JUST data.
	def _extract_data(self, infile):
		print("\nReading data ...")
		# This will be a list that contains lists.
		all_data = []

		with open(infile, 'r', encoding='utf8', errors='ignore') as f:
			# ATTENTION: DON'T .strip() anywhere! I observed that e.g. the heat 
			# capacity contains no values for the first minute of an experiment.
			# 
			# First line contains the variables
			# This is a list which contains all variables in the order in 
			# which these are in the rawdata file.
			variables = f.readline().split('\t')

			for line in f:
				all_data.append(line.split('\t'))

		return variables, all_data


	# In the rawdata the variables may be in different columns. This function
	# figures out in which column a ariable of interest actually is.
	def _create_variable_indices(self):
		self.indices = {}
		for i in range(len(self.original_variables)):
			variable = self.original_variables[i]
			if 'time' in variable.lower():
				self.indices['time'] = i
				self.variables.append('time')
			elif 'temperature' in variable.lower():
				self.indices['temperature'] = i
				self.variables.append('temperature')
			elif ('heat flow' in variable.lower()) and \
										('normalized' in variable.lower()):
				self.indices['heat_flow'] = i
				self.variables.append('heat_flow')
			elif 'heat capacity' in variable.lower() and \
										('normalized' in variable.lower()):
				self.indices['heat_capacity'] = i
				self.variables.append('heat_capacity')
			# The following is mainly to use class Data() as parent for 
			# class UserFunction().
			# 
			# To calculate the kinetic function or to do predictions I want to
			# give the possibility to read e.g. the activation energy from file.
			# This includes reading the conversion value for which a value is
			# valid.
			elif 'conversion' in variable.lower():
				self.indices['conversion'] = i
				self.variables.append('conversion')
			# I use here 'value' because class UserFunction() can have 
			# more than just one type of value as ... well, value.
			# However, in files that contain the activation energy this is 
			# already called 'activation energy', thus I check for this 
			# specifically.
			elif ('activation energy' in variable.lower()) or \
											('value' in variable.lower()):
				self.indices['values'] = i
				self.variables.append('values')
			else:
				pass


	# Here is the data extracted for each variable from the rawdata and stored 
	# separately in an attribute with the correct name.
	def _create_data_attributes(self, rawdata):
		for variable in self.variables:
			this_index = self.indices[variable]
			this_data = self._extract_from_raw(rawdata, this_index)
			setattr(self, variable, this_data)


	# Here the actual data is extraced for a given variable.
	def _extract_from_raw(self, rawdata, this_index):
		data = []
		for i in range(len(rawdata)):
			# The file may have empty lines. This will lead to an IndexError. 
			# Ignore this.
			try:
				foo = rawdata[i]
				bar = rawdata[i][this_index]
				number_raw = rawdata[i][this_index].strip().replace(',', '.')
				# Sometimes the rawdata contains nothing (or rather < '' >. 
				# E.g. during the first minute the heat capacity is not measured.
				# If it happens in the start, the value is set to zero.
				# If it happens in the end or after the initial periode, the value 
				# is set to the last value. The latter can be seen as "continuation".
				if not number_raw:
					# ATTENTION: The five minutes here (300seconds) are an 
					# arbitrary value which works for my cases, but may NOT 
					# work for yours!
					if i * self.timestep < 300:
						number = dec('0.00')
					# This is the "continuation"-case.
					else:
						number = data[i-1]
				else:
					number = dec(number_raw)

				data.append(number)

			except IndexError:
				pass

		return data


	# The file usually has empty lines at the end. This leads to the time
	# attribute having more entries than the other data-attributes.
	# Here I make everything equally long
	# ATTENTION: The variable with the shortest list of values will be used.
	def _make_all_data_equally_long(self):
		# First: figure out how long the shortest list with values is.
		for variable in self.variables:
			length = len(getattr(self, variable))
			if length < self.number_of_measurements:
				self.number_of_measurements = length

		# Secondly: Cut the too long end from all other lists.
		for variable in self.variables:
			while len(getattr(self, variable)) > self.number_of_measurements:
				getattr(self, variable).pop()


	# I need the time to be in seconds, but the time may have been provided
	# in minutes in the rawdata. Thus, just write this attribute again with 
	# the given timestep.
	def _create_time_in_seconds(self):
		# self.timestep should already be decimal.
		self.time = [self.timestep]

		# < - 1 > because the very first new time value is already put into
		# the list when it is created above.
		for i in range(self.number_of_measurements - 1):
			next_time = self.time[-1] + self.timestep
			self.time.append(next_time)


	# Usually the temperature is in degrees Celsius. However, I need it in 
	# Kelvin for all the calculations.
	def create_temperature_in_kelvin(self):
		# self.in_kelvin is either 1 or 0. Zero will be evaluated as False 
		# here ... Cool!
		if not self.in_kelvin and hasattr(self, 'temperature'):
			for i in range(len(self.temperature)):
				self.temperature[i] = self.temperature[i] + dec('273.15')
		elif not hasattr(self, 'temperature'):
			print("The data does not contain temperature data!")


	# The mean steady state heat flow value can be seen as a fundamental 
	# attribute of the data, thus this is a class method.
	# < intervall > is the timeframe in SECONDS that shall be taken 
	# from the end to calculate the mean steady state heat flow.
	def _calculate_steady_state_heat_flow(self, intervall = None):
		if not intervall:
			# ATTENTION: This is more or less an arbitrary value that works
			# for my data!
			intervall = 323

		length_for_mean = int(dec(intervall) / self.timestep)
		# Just a check if the data is actuall log enough to calculate sth.
		# at all.
		if len(self.time) < length_for_mean:
			this = 'The data is not long enough to calculate the mean heat '
			that = 'flow value from the last {} seconds!\n'.format(intervall)
			siht = 'ATTENTION: NOTHING will be done!'
			print(this + that + siht)

			# This is needed in correct_baseline() as return condition.
			return False

		else:
			i = -1
			self.steady_state_heat_flow = self.heat_flow[i]
			while abs(i) < length_for_mean:
				i -= 1
				self.steady_state_heat_flow += self.heat_flow[i]

			self.steady_state_heat_flow /= abs(i)

			return True


	# Baseline correction is also a basic method to be done with o on the data.
	# Thus it appears here.
	# < steady_state_heat_flow > gives the user to supply another value, thus
	# this metod can be used even if the data itself does not reach steady 
	# state.
	def correct_baseline(self, steady_state_heat_flow = None, intervall = None):
		# Set self.steady_state_heat_flow or return if this is not possible.
		if steady_state_heat_flow:
			self.steady_state_heat_flow = steady_state_heat_flow
		# self._calculate_steady_state_heat_flow() could have been called
		# independently and thus self.steady_state_heat_flow could already
		# exist.
		elif not hasattr(self, 'steady_state_heat_flow'):
			if not self._calculate_steady_state_heat_flow(intervall):
				self.baseline_corrected = False
				return

		# All values in the data-attributes are of type dec().
		# I love list comparisons :) .
		self.heat_flow = [x - self.steady_state_heat_flow for x in self.heat_flow]
		self.baseline_corrected = True


	# The total heat of reaction certainly is an attribute of the data.
	# Hence the calculation of the same is a class method.
	def calculate_total_heat_of_reaction(self):
		# Yes, it is as easy as this ... tihihihi.
		self.total_heat = dec('0.0')
		for i in range(len(self.heat_flow) - 1):
			self.total_heat += self.heat_flow[i] * self.timestep

		# Round to get a sensible value
		self.total_heat = round(self.total_heat, 3)


	# By reading the function name ou may have guessed what I consider an 
	# attribute of the data ;)
	# < total_heat > should come as a dec()-number.
	def calculate_conversion(self, total_heat, initial_conversion):
		if not total_heat:
			self.calculate_total_heat_of_reaction()
		else:
			# deepcopy(is probably not necessary, but, well, you never know.
			self.total_heat = deepcopy(total_heat)

		if not initial_conversion:
			self.initial_conversion = dec('0.00')
		else:
			self.initial_conversion = deepcopy(initial_conversion)

		self.conversion = [self.initial_conversion]

		# < - 1 > because the first value is alread set above!
		for value in self.heat_flow:
			previous_conversion = self.conversion[-1]
			# ATTENTION: total heat is calculated with the timestep taken into 
			# account (obviously). Thus I need to account for the timestep 
			# here, too. Otherwise the conversion will reach a fraction of
			# one and the fraction is correlated to the timestep (e.g. 10 of
			# the timestep is 0.1).
			added_conversion = value / self.total_heat * self.timestep
			self.conversion.append(previous_conversion + added_conversion)

		# pop() the very first value, because this can NEVER be (exactly) zero
		# (or exactly the initial conversion), since a heat flow value is 
		# already measured, thus some conversion has to be added to the actual
		# first value, which takes place above
		self.conversion.pop(0)


	# I need the index of the conversion with the value which is closest to
	# the steps the user want to calculate the activation energy for.
	def find_values_for_isoconversion(self):
		# ATTENTION: self.conversion_step (without the < s > at the end!) 
		# has to be det after the data was created but before this method is 
		# called.
		self.conversion_steps = [self.conversion[0]]
		self.time_steps = [self.time[0]]
		self.temperature_steps = [self.temperature[0]]

		# Weird conversion_step-values may lead to a final conversion larger
		# than one. This is of course not possible and shall be avoided.
		# ATTENTION: Don't use a conversion step of zero (or the initial 
		# conversion) conversion since this will not work with how the heat 
		# flow values are picked later to determine the integral.
		next_step = self.conversion_steps[0] + self.conversion_step

		for i in range(len(self.conversion)):
			# First find the closest actual value of conversion to the desired 
			# value ...
			if self.conversion[i] >= next_step:
				self.conversion_steps.append(next_step)
				# ... and use its index to find the corresponding time and 
				# temperature values.
				self.time_steps.append(self.time[i])
				self.temperature_steps.append(self.temperature[i])
				# Then calculate the next step.
				next_step = self.conversion_steps[-1] + self.conversion_step


	# The inverse temperature is needed to calculate the compensation 
	# parameters. Since the temperature is an attribute of the data, it
	# seems to fit that the inverse temperature is, too.
	def _calculate_inverse_temperature(self):
		R = dec('8.314')
		self.inverse_temperature = deepcopy(self.temperature)
		for i in range(len(self.inverse_temperature)):
			new_value = dec('-1.0') / (R * self.inverse_temperature[i]) 
			self.inverse_temperature[i] = new_value


	# More or less dito for the values of a given kinetic model.
	def _calculate_kinetic_model_values(self):
		for model_name, kinetic_function in kf.all_models.items():
			this = '{}_model_values'.format(model_name)
			these_values = []

			for conversion in self.conversion:
				# numpy can not work with dec()-numbers. Thus I have to 
				# convert to float :( .
				value = kinetic_function(float(conversion))
				these_values.append(value)

			setattr(self, this, these_values)


	# Just to keep .calculate_left_hand_side() more tidy.
	def _calculate_logarithm(self, model_name):
		this = '{}_model_values'.format(model_name)
		model_values = getattr(self, this)
		these_values = []

		for i in range(len(self.heat_flow)):
			heat_flow = float(self.heat_flow[i])
			model_value = model_values[i]

			value = heat_flow / model_value
			# It is possible that value becomes negative. In this case the 
			# logarithm can NOT be calculated. This will lead to errors and this
			# case is handled here. However, this should just happen towards
			# the very beginning or end of the curing process and within the
			# limits of 20 to 80 percent everything should be ok.
			if value <= 0.0:
				this = '-'
			else:
				this = np.log(value)

			these_values.append(this)

		return these_values


	# Dito for the left hand side of the equation that leads to the linear
	# relationship between the Arrhenius pre-factor and the activation energy.
	def calculate_left_hand_side(self):
		self._calculate_inverse_temperature()
		self._calculate_kinetic_model_values()

		for model_name in kf.all_models.keys():
			this = '{}_left_hand_side_values'.format(model_name)
			these_values = self._calculate_logarithm(model_name)

			setattr(self, this, these_values)


	# Linear regression shall take place between 20 and 80 percent conversion.
	# Here I find the indices in self.conversion at which 20 or 80 percent 
	# conversion are, so that I can use this in _fit_linear_equation_to_all_models().
	def _find_bounds(self):
		lower_bound = None
		upper_bound = None

		for i in range(len(self.conversion)):
			# Yes, I hard code here between which conversion limits the linear
			# regression shall take place afterwards.
			if not lower_bound and self.conversion[i] >= dec('0.2'):
				lower_bound = i
			if not upper_bound and self.conversion[i] >= dec('0.8'):
				upper_bound = i
				# Break at this point to not go through the whole list, which 
				# may be very long.
				break

		return lower_bound, upper_bound


	# This function fits the kinetic models between 20 and 80 percent to
	# figure out the Arrhenius pre-factor and activation energy for each model.
	def _fit_linear_equation_to_all_models(self):
		lower_bound, upper_bound = self._find_bounds()
		all_x_values = self.inverse_temperature
		x_values = [float(x) for x in all_x_values[lower_bound:(upper_bound + 1)]]

		for model_name in kf.all_models.keys():
			this = '{}_left_hand_side_values'.format(model_name)
			all_left_hand_side_values = getattr(self, this)
			fit_this = all_left_hand_side_values[lower_bound:(upper_bound + 1)]
			initial_guess = 0.0, 0.0

			result = curve_fit(kf.linear_function, x_values, fit_this, initial_guess)
			ln_pre_factor = result[0][0]
			activation_energy = result[0][1]

			this = '{}_ln_pre_factor'.format(model_name)
			that = '{}_activation_energy'.format(model_name)
			setattr(self, this, ln_pre_factor)
			setattr(self, that,activation_energy)


	# And finally the linear fit is made through all pairs of pre-factor and
	# activation energy to find the compensation parameters.
	def fit_all_for_compensation_parameters(self):
		self._fit_linear_equation_to_all_models()

		all_activation_energies = []
		all_ln_pre_factors = []

		for model_name in kf.all_models.keys():
			this = '{}_activation_energy'.format(model_name)
			that = '{}_ln_pre_factor'.format(model_name)
			activation_energy = getattr(self, this)
			ln_pre_factor = getattr(self, that)
			
			all_activation_energies.append(activation_energy)
			all_ln_pre_factors.append(ln_pre_factor)
			initial_guess = 0.0, 0.0

		result = curve_fit(kf.linear_function, all_activation_energies, \
												all_ln_pre_factors, initial_guess)
		self.a = result[0][0]
		self.b = result[0][1]


	# See comment to _generate_values_from_file() in class UserFunction() why 
	# I originally wrote this function. However, later it turned out, that I 
	# can use a more general version of it (the one below) also in another 
	# context. Thus I re-wrote it and moved it to class Data(). 
	# 
	# One example of what is done here: I check which value in reference_list
	# is closest to a value in original_list. Afterwards the corresponding 
	# value for the parameter of interest is found in values_list and stored.
	def _get_correct_values_from_file(self, reference_list, original_list, values_list):
		print("Finding correct values (this may take a while) ...")
		new_values_list = []

		# I do more or less the same trick as in find_values_for_isoconversion() 
		# to speed up the process.
		i = 0
		j = 0
		this_value = reference_list[j]

		# Problem: finding the closest element takes a lot of time, unless I do 
		# the same as in find_values_for_isoconversion(). However, this is 
		# just meaningful if original_list is considerably longer than 
		# reference_list. This is the case when I need just some e.g. heat flow 
		# values to calculate the actual kinetic function and I can use 
		# _original_longer_reference() where said trick is used.
		# 
		# However, when I need to find the corresponding activation energy
		# values to a more "fine grained" conversion-increment than the 
		# activation energy file actually has, than this trick would still work, 
		# but it would not yield the nearest value to a given conversion.
		# Thus I have implemented a proper way to do it in this case.
		# Fortunately is the list with the activation energies not assumed to 
		# be long.
		# If the the list with activation energies is equally long as 
		# original list (the conversion increment is equal), the upper case
		# should work, too. (It doesn't completely, though, see below)
		if len(original_list) >= len(reference_list):
			new_values_list = self._original_longer_reference(reference_list, \
														original_list, values_list)
		else:
			new_values_list = self._original_shorter_reference(reference_list, \
														original_list, values_list)

		# Case three is the opposite of the second case. This is a stupid case.
		# who would want a coarser grained kinetic function than the activation
		# energy is calculated for.
		# Usually I would let thr users run into such things, especially since
		# these two upper cases took me some nerves to test and implement. 
		# However, this seems to be fixable in an easy way, because in this case
		# it seems as if new_values_list is always just one element short.
		# I just add one element and that solves the occuring errors.
		while len(new_values_list) < len(reference_list):
			new_values_list.append(new_values_list[-1])

		return new_values_list


	# Just to keep _get_correct_values_from_file() more tidy.
	# Related to the problem described in _get_correct_values_from_file()
	# ATTENTION: It is assumed that values_list is equally long as original_list!
	def _original_longer_reference(self, reference_list, original_list, values_list):
		new_values_list = []
		# I do more or less the same trick as in find_values_for_isoconversion() 
		# to speed up the process.
		i = 0
		j = 0
		this_value = reference_list[j]

		while i < len(original_list):
			compare_value = original_list[i]
			if compare_value >= this_value:
				new_values_list.append(values_list[i])
				j += 1
				# There may be no element left in reference_list. Hence, I need
				# a break condition.
				if j == len(reference_list):
					break

				this_value = reference_list[j]

			i += 1

		return new_values_list


	# Dito
	# ATTENTION: It is assumed that values_list is equally long as original_list!
	def _original_shorter_reference(self, reference_list, original_list, values_list):
		new_values_list = []

		for this_value in reference_list:
			# I found this a while ago somewhere on the net, and I don't 
			# remember where. :(
			this_index = min(range(len(original_list)), key = lambda i: abs(original_list[i] - this_value))
			new_values_list.append(values_list[this_index])

		return new_values_list


# For the kinetic function or the actual kinetic function, the user shall
# be able to provide the function values in a file or as an equation. 
# In the latter case the actually used values shall be calculated for each
# conversion step. 
# Long story short, this is a class Data() object with additinal methods
# and a bit different focus.
class UserFunction(Data):
	# < timestep > is just needed to be able to call super(). It will NOT
	# be used and the time-values will be wrong
	def __init__(self, conversion_step, timestep):
		self.conversion_step = conversion_step
		# These are the x-values. Will either be set when super() is called or
		# when the values are calculated.
		self.conversion = None
		self.timestep = timestep
		# These are the y-values.
		self.values = None
		self.path = None
		self.infile = None
		self.number_of_functions = None

		self.get_values()


	# The activation energy can come either from a file or be parametrized with 
	# one or severa functions. The former is easy, the latter requires more
	# information and this function get's this additional information.
	# It returns the (hard coded!) name of the activation energy file or the 
	# number of functions used for parametrization. This is needed at two places, 
	# thus it ended up here.
	def get_values(self):
		this = 'Read values from file (F) or calculate from equation (E): '
		user_input = 'risimif'
		while not af.correct_user_input(user_input, ['f', 'e']):
			user_input = input(this)

		if user_input.lower() == 'f':
			this = '\nATTENTION: What is usually assumed regarding the structure '
			that = 'of the data in the file is assumed here, too! (First line is '
			siht = 'table header, columns separated by tabs).\n'
			print(this + that + siht)

			this = 'Full path of folder with activation energy file: '
			that = 'Name of file (incl. extension): '
			self.path = af.get_path(this + that)
			self.infile = af.get_infile(self.path)

			self._generate_values_from_file()

		elif user_input.lower() == 'e':
			# A function can be parametrized differently for different areas of 
			# conversion. To be able to handle that, I need to know the number 
			# of different functions.
			self.number_of_functions = af.get_user_input('number_of_functions')
			print('')
			self._generate_values_from_function()
			self._delete_duplicates()


	# It is possible that self.conversion_step is different from the increment
	# in the conversion values in the given file. This method handles this.
	def _generate_values_from_file(self):
		# It was easiest to simple call super because class Data() has
		# already methods that can read the data from a file.
		super(UserFunction, self).__init__(self.timestep, self.infile)

		# Because of what is written in the comment above, I need a copy of
		# the original values, since _calculate_conversion_steps() will
		# change self.conversion and _find_correct_values_in_file() will
		# change self.values.
		self.original_conversion = deepcopy(self.conversion)
		self.original_values = deepcopy(self.values)

		lower_conversion = self.original_conversion[0]
		upper_conversion = self.original_conversion[-1]

		self.conversion = self._calculate_conversion_steps(lower_conversion, \
																upper_conversion)

		# _get_correct_values_from_file() is a method of the parent class.
		self.values = self._get_correct_values_from_file(self.conversion, \
									self.original_conversion, self.original_values)







	# I want it to be possible for the user to just write a valid python expression
	# of a function that will then be used for calculations.
	# This is taken care of in here. The user states the function and for which
	# conversion limits it is valid. The conversion steps and the belonging 
	# activation energies are then calculated and returned.
	def _generate_values_from_function(self):
		this = 'Please state below the equations for each area of conversion these '
		that = 'are valid for.\nUse python numpy expression for the functions '
		siht = '(Press H for help and examples).\n'
		print(this + that + siht)

		self.conversion = []
		self.values = []

		i = 1
		while i <= self.number_of_functions:
			this = 'Function {} (Use CAPITAL < X > for the conversion, '.format(i)
			that = 'H for help): '
			function_as_string = input(this + that)

			if function_as_string.lower() == 'h' or \
											function_as_string.lower() == 'help':
				af.print_function_input_help_text()
			elif function_as_string.lower() == '':
				pass
			else:
				text = 'Lower conversion limit for this function: '
				lower_limit = af.get_user_input(text)

				text = 'Upper conversion limit for this function: '
				upper_limit = af.get_user_input(text)

				print('Calculating function values ...\n')
				conversions = self._calculate_conversion_steps(lower_limit, upper_limit)

				# I test for the most common errors in the string that can
				# occur, to help out the user so that the program is not 
				# always crashed.
				try:
					values = self._get_function_values(function_as_string, conversions)

					self.conversion.extend(conversions)
					self.values.extend(values)

					i += 1
				except (NameError, AttributeError, decimal.InvalidOperation, \
						SyntaxError, ZeroDivisionError):
					this = '\nFunction contains invalid symbols or unknown '
					that = 'numpy operations or Divison by zero or does anything '
					siht = 'else weird.\nPlease check and try again.'
					print(this + that + siht)


	# The kinetic function (or prediction) will NOT be calculated for all 
	# possible conversion steps, but with the increment provided by the user. 
	# This function calculates all steps with the given parameters.
	def _calculate_conversion_steps(self, lower_limit, upper_limit):
		conversion_steps = [lower_limit]

		while conversion_steps[-1] < upper_limit:
			next_step = conversion_steps[-1] + self.conversion_step
			conversion_steps.append(next_step)

		return conversion_steps


	# Mainly to keep _generate_values_from_function() more tidy.
	# < function_as_string > is the function as a string.
	# < onversion > is a list that contains all valid conversion steps for
	# this function.
	# 
	# ATTENTION: I need to use eval()!!!
	# The user can totally mess up everything. I will NOT sanitize the user input
	# more than explained below. 
	# ATTENTION: Dear user that wants to build upon this. You need to make 
	# absolutely sure that your own users can NOT mess up everything. The below
	# solution is good enough for the purpose of the program I originally wrote,
	# but it may not be enough for what you want to do. Please take special care
	# if it shall run on the web.
	def _get_function_values(self, function_as_string, conversions):
		values = []
		function = function_as_string.replace('__', '')

		for i in range(len(conversions)):
			# .replace() needs a string, but self.conversion contains dec()-numbers.
			conversion = str(conversions[i])
			# < X > needs to be replaced with the conversion, since eval() will
			# evaluate just things with "real numbers" in it. Yes, yes, eval()
			# can do much more, but this is not of interest here.
			# I also try to assist the user if she or he uses different brackets.
			foo = function.replace('X', conversion).replace('[', '(')
			this_function = foo.replace(']', ')').replace('{', ')').replace('}', ')')

			# ATTENTION: eval() IS DANGEROUS! I try to make it less dangerous by 
			# not allowing double underscores (see .replace() above) and by not 
			# allowing builtin-functions that could mess with the system 
			# (e.g. os.system() used to delete everything).
			# I got these solutions from here:
			# https://nedbatchelder.com/blog/201206/eval_really_is_dangerous.html
			# 
			# As far as I understand it, am I mapping all builtin functions to an
			# empty dict where this can not do harm.
			# 
			# However, I do need to be able to use numpy functions. Thus I 
			# specify how this shall be interpreted by passing a local dict as 
			# second parameter.
			this_value = dec(str(eval(this_function, {'__builtins__': {}}, {'np':np})))

			values.append(this_value)

		return values


	# If the area of definition overlaps for two function, I need to delete
	# duplicate conversions and corresponding values.
	# 
	# ATTENTION: This will take a LONG time for lists with more than ca. 20k
	# elements! 
	# 
	# The duplicate element in the conversion list is associated with the
	# element in the values list at the same index. If the former is deleted, 
	# the latter needs to be deleted, too.
	# This means that I basically have to go through each element of the 
	# conversion list and check if it occurs more than once and then delete it 
	# and the corresponding element in the values list.
	# Below is the fastest and simplest I could come up with under the
	# assumption that I can not assume anything (so duplicates can be anywhere 
	# in the list). All solutions on the web basically go also through the 
	# complete list, thus I could not find something which is significantly 
	# faster under these assumptions and conditions described above :( 
	def _delete_duplicates(self):
		print('Deleting duplicates (this may take a while) ...\n')
		# I want to delete the second, third etc. occurence of an element, 
		# NOT the first. Hence I start deleting from behind.
		backwards_conversion = self.conversion[::-1]
		backwards_values = self.values[::-1]
 
		length = len(backwards_conversion)
		i = 0
		while i < length:
			this_conversion = backwards_conversion[i]
			if backwards_conversion.count(this_conversion) > 1:
				del backwards_conversion[i]
				del backwards_values[i]
				length -= 1
				i -= 1
			i += 1

		self.conversion = backwards_conversion[::-1]
		self.values = backwards_values[::-1]





# It was convenient to have this. However, it is instantiated with just the
# bare minimum of parameters and more attributes will be added to it manually.
class Prediction(Data):
	# < isothermal > is True or False. I don't really need it 
	# (end_temperature) could serve this function. But it is convenient to have.
	# For an isothermal prediction, start_temperature will be the only temperature.
	def __init__(self, timestep, timeframe, isothermal, start_temperature, \
								end_temperature, ramp, total_heat, initial_conversion):
		# I do NOT do it like in class UserFunction() because I do NOT want to
		# call the __init__ of class Data(), since I don't have the necessary 
		# information. However, I want to use at least one method of this class
		# and this I'm using super().
		super(Data, self)
		self.timestep = float(timestep)
		self.timeframe = timeframe
		self.isothermal = isothermal
		self.start_temperature = float(start_temperature)
		self.end_temperature = float(end_temperature)
		self.ramp = float(ramp)
		self.total_heat = float(total_heat)
		self.initial_conversion = float(initial_conversion)
		self.conversion = [self.initial_conversion]
		self.temperature = [self.start_temperature]
		self.time = [0.0]
		self.activation_energy = None
		self.pre_factors = None
		self.kinetic_function = None
		self.heat_flow = [0]


	# Just to keep predict() more tidy.
	# Well, the name is a bit misleading, since it will also return True when
	# the time is up
	def fully_cured(self):
		if not self.isothermal:
			this = (self.temperature[-1] >= self.end_temperature) or \
											(self.time[-1] >= self.timeframe)
		else:
			this = (self.time[-1] >= self.timeframe) or (self.conversion[-1] >= 0.99999)

		return this



	def predict(self):
		print("Calculating the heat flow. ATTENTION: This will take some time ...")
		R = 8.314
		i = 0
		while not self.fully_cured():
			i += 1
			temperature = self.temperature[-1]
			conversion = self.conversion[-1]

			# I use _original_longer_reference() since it returns the
			# truly closest value. See comment in _get_correct_values_from_file().
			# Don't forget that all parameters need to be lists.
			activation_energy = float(self._original_longer_reference([conversion], \
											self.activation_energy.conversion, \
												self.activation_energy.values)[0])
			pre_factor = float(self._original_longer_reference([conversion], \
											self.pre_factor.conversion, \
												self.pre_factor.values)[0])
			kinetic_function = float(self._original_longer_reference([conversion], \
											self.kinetic_function.conversion, \
												self.kinetic_function.values)[0])

			Arrhenius = pre_factor * np.exp(-activation_energy / R / temperature)

			heat_flow = Arrhenius * kinetic_function
			self.heat_flow.append(heat_flow)

			conversion_change = heat_flow / self.total_heat * self.timestep
			conversion += conversion_change
			self.conversion.append(conversion)

			temperature += self.ramp * self.timestep
			self.temperature.append(temperature)

			time = self.time[-1] + self.timestep
			self.time.append(time)

			# Just to let the user know how far the process came since this may
			# take some time.
			if i % 1000 == 0:
				this = 'At time {} s of {} s; conversion = {}'.format(time, \
														self.timeframe, conversion)
				print(this)

				# I apologize for the lengthy comment.
				# 
				# Problem: if small timesteps are used and long timeframes
				# will this while-loop be called very often and it turned out 
				# that it gets considerable slower over time (rather extrem).
				# 
				# Initially I thought it is because of appending to the lists. 
				# This because I thought that finding the minimum in a list to 
				# a given conversion value (that is what takes place in 
				# self._original_longer_reference()) takes always the same time 
				# if the length of the list doesn't change, the only thing
				# that changes is the length of the lists I append to and the web 
				# suggested that it may be the appending itself.
				# 
				# However, the latter WAS a problem in python 2, but this here
				# runs in python 3 where this problem was fixed.
				# Also, using cProfiler revealed that appending to the list was
				# NOT the bottleneck.
				# 
				# So I tried other suggestions and in the end it turned out
				# that it actually was somewhere inside _original_longer_reference()
				# that got slower over time. So the thing I ruled out before was 
				# the culprit.
				# The only thing that differs in this function with progressing 
				# conversion is that matching values are found LATER in the list 
				# of which the minimum is to be found from. I can't imagine why 
				# this should slow down, since I would think that the whole list 
				# has to be searched for the minimum anyway, but it does.
				# 
				# Solution: The list is ordered and I don't need previous 
				# values for this application. Thus I simply shorten the lists 
				# which are used to find the necessary parameters, every 1000 
				# iterations. 
				# 
				# The following lines made the algorithm ca. 100 times faster 
				# than it is without these.
				# And for once I came up with the idea all by myself :) .

				# The .conversion-attributes which are used below are 
				# dec()-numbers. It is not possible to do math with dec()-numbers
				# and float-values.
				conversion = dec(conversion)

				f = lambda i: abs(self.activation_energy.conversion[i] - conversion)
				# Find the index of te minimum ...
				this_index = min(range(len(self.activation_energy.conversion)), key = f)
				# Don't do the following, if the index is zero, since I subtract
				# one from this_index and I this would become < -1 > as argument
				# for how to slice the lists and this would mess everthing up!
				if this_index != 0:
					# ... and cut everything before this index (minus 1) from 
					# the lists. The minus one just in case if a real conversion
					# value get's a bit smaller due to rounding errors or
					# whatever and needs the previous value.
					self.activation_energy.conversion = self.activation_energy.conversion[(this_index - 1):]
					self.activation_energy.values = self.activation_energy.values[(this_index - 1):]

				f = lambda i: abs(self.pre_factor.conversion[i] - conversion)
				this_index = min(range(len(self.pre_factor.conversion)), key = f)
				if this_index != 0:
					self.pre_factor.conversion = self.pre_factor.conversion[(this_index - 1):]
					self.pre_factor.values = self.pre_factor.values[(this_index - 1):]

				f = lambda i: abs(self.kinetic_function.conversion[i] - conversion)
				this_index = min(range(len(self.kinetic_function.conversion)), key = f)
				if this_index != 0:
					self.kinetic_function.conversion = self.kinetic_function.conversion[(this_index - 1):]
					self.kinetic_function.values = self.kinetic_function.values[(this_index - 1):]






















