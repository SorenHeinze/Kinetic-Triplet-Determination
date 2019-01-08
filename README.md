# Kinetic-Triplet-Determination
Programs to get the activation energy, Arrhenius pre-factor and kinetic function from DSC data

## Introduction
In my PhD I investigated the curing kinetics of a slow curing polymer using Differential Scanning Calorimetry (DSC).
See [1] for details (open access paper).

Regular data-fitting did NOT yield the parameters needed to simulate the curing.

Hence, all assumed knowledge was abandoned and the exact isoconversional method was used to determine the needed information.

These programs are NOT the programs I used while I worked on my PhD, but they use the same method and yield the same results.
Otherwise are these programs much better structured (and commented) and I offer to the user more options and a much nicer interface.

## Description
These are python3 programs. The main functions are:
- calculation of the activation energy using the exact isoconversional method
- calculation of the compensation parameters using the compensation effect
- Calculation of the actual kinetic function
- prediction of the heat flow

In addition the following functions are offered to the user:
- separationof the experimental steps from a DSC rawdata file
- stitching together of several steps (if necessary) so that all other programs can work with it
- subtract of post-cure-run data from the actual cure data
- correction of the baseline to zero
- calculation of the total heat
- creation of a file that contains also the conversion
- some hints and tips around how to get / interpret DSC data

## Usage
Put all .py-files into one folder and simply run the programs in a command line window. Remember, that python3 was used to write the software.

All programs can be run separately by simply calling them. However, it is probably more convenient to call < main.py >. The latter offers an interface to the user in which each program can be chosen.

Numpy and SciPy need to be installed for these programs to work.

These programs were tested under Debian 9.6 . However, they should work also under proprietary operating systems. 

When the program is running chose < How to use the programs and DSC / data hints > to get more information on how I recommend in which order the separate programs should be executed when a user comes with a bunch of DSC rawdata-files.

## Literature
[1] S. Heinze and A. T. Echtermeyer, A Practical Approach for Data Gathering for Polymer Cure Simulations, Appl. Sci. 2018, 8(11), 2227; https://doi.org/10.3390/app8112227
