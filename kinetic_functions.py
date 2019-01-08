#    "Kinetic-Triplet-Determination - kinetic_functions" (v1.0)
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

# This file contains some functions that are used to model the cure of polymers.

import numpy as np

# Due to noise can the conversion be (slightly) larger than one or for some 
# measurement points or (in principle) smaller than zero.
# This will lead to errors for certain models and this function takes care of it.
def avoid_bad_conversion(conversion):
	if conversion <= 0.0:
		conversion = 0.00000001
	elif conversion >= 1.0:
		conversion = 0.99999999

	return conversion


def FO(conversion):
	return 1 - conversion


def SO(conversion):
	return (1 - conversion)**2


def AUTO_12(conversion):
	conversion = avoid_bad_conversion(conversion)

	return conversion**1*(1 - conversion)**2



def AUTO_21(conversion):
	conversion = avoid_bad_conversion(conversion)

	return conversion**2*(1 - conversion)**1



def AUTO_11(conversion):
	conversion = avoid_bad_conversion(conversion)

	return conversion**1*(1 - conversion)**1



def AUTO_0515(conversion):
	conversion = avoid_bad_conversion(conversion)

	return conversion**(0.5)*(1 - conversion)**(1.5)


def A2(conversion):
	conversion = avoid_bad_conversion(conversion)

	return 2*(1 - conversion)*(-np.log(1 - conversion))**(1.0/2.0)


def A3(conversion):
	conversion = avoid_bad_conversion(conversion)

	return 3*(1 - conversion)*(-np.log(1 - conversion))**(2.0/3.0)


def A4(conversion):
	conversion = avoid_bad_conversion(conversion)

	return 4*(1 - conversion)*(-np.log(1 - conversion))**(3.0/4.0)


def D1(conversion):
	conversion = avoid_bad_conversion(conversion)

	return 1.0/2.0*conversion**(-1)


def D2(conversion):
	conversion = avoid_bad_conversion(conversion)
	this = -np.log(1 - conversion)

	return (this)**(-1)


def D3(conversion):
	conversion = avoid_bad_conversion(conversion)
	factor = (1 - (1 - conversion)**(1.0/3.0))

	return 3.0/2.0*(1 - conversion)**(2.0/3.0)*factor**(-1)


def P1(conversion):
	conversion = avoid_bad_conversion(conversion)

	return 4*conversion**(3.0/4.0)


def P2(conversion):
	conversion = avoid_bad_conversion(conversion)

	return 3*conversion**(2.0/3.0)


def P3(conversion):
	conversion = avoid_bad_conversion(conversion)

	return 2*conversion**(1.0/2.0)


def P4(conversion):
	conversion = avoid_bad_conversion(conversion)

	return 2.0/3.0*conversion**(-1.0/2.0)


def R2(conversion):
	conversion = avoid_bad_conversion(conversion)

	return 2*(1 - conversion)**(1.0/2.0)



def R3(conversion):
	conversion = avoid_bad_conversion(conversion)

	return 3*(1 - conversion)**(2.0/3.0)



all_models = {'FO':FO, 'SO':SO, 'AUTO_12':AUTO_12, 'AUTO_21':AUTO_21, \
				'AUTO_11':AUTO_11, 'AUTO_0515':AUTO_0515, 'A2':A2, 'A3':A3, \
				'A4':A4, 'D2':D2, 'D1':D1, 'D3':D3, 'P1':P1, 'P2':P2, 'P3':P3, \
				'P4':P4, 'R2':R2, 'R3':R3}


# This is not really a kinetic model function, but it is a function and thus
# I placed it here.
def linear_function(x_values, y_intercept, slope):
	return y_intercept + slope * x_values






















