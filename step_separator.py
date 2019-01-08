# -*- coding: utf-8 -*- 

#    "Kinetic-Triplet-Determination - step_separator" (v1.0)
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

# This program separates all steps in DSC-files from each other and
# returns as many files as there are steps.
# 
# ATTENTION: It is assumed that tabs separate the columns.
# ATTENTION: It is assumed that the keyword < [step] > is followed by three 
# text-lines which contain the following (in this order):
# 1.: step name
# 2.: table header -> variables
# 3.: table header -> units
# 
# ATTENTION: This probably works just with files exported from the 
# TA Instruments TRIOS software. Other vendors probably structure their
# files differently.

import os
import additional_functions as af

## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## 
## ## ## ## ## ## ##                            ## ## ## ## ## ## ## 
## ## ## ## ## ## ## FUNCTION DEFINITIONS HERE  ## ## ## ## ## ## ##
## ## ## ## ## ## ##                            ## ## ## ## ## ## ## 
## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## 


# Each step gets its own file in the end.
# Here I create the outfile names
def create_filenames(path, steps):
	filenames = []

	# To not confuse the user I start counting the files at one.
	for i in range(1, (len(steps) + 1)):
		number = str(i).zfill(2)
		description = steps[i - 1]
		filenames.append('{}{}_{}.txt'.format(path, number, description))

	return filenames



# The next line after the keyword '[step]' is always a descrption of 
# this step. I need this information for the filenames.
def extract_stepname(line):
	# \xc2\xb0 is the degree character
	# FUCKING STUPID ENCODING OF STRINGS!!!!
	# Sometimes replacing < \xc2\xb0 > works other times it doesn't, 
	# like for example, here! I needed to use the actual degree character here 
	# so that it gets replaced and does not cause any more trouble.
	# FUCKING STUPID ENCODING OF STRINGS!!!!
	foo = line.strip().replace('°', '')
	# Out if these stepnames filenames will be created later.
	# Hence " / " should not be present in the filename.
	stepname = foo.replace('/', ' per ')

	return stepname



# In the raw-data-files the table header is over two lines. This function
# makes just one line out of these.
def create_table_header(names_as_line, units_as_line):
	variables = names_as_line.strip().split('\t')
	# \xc2\xb0 is the degree character
	units = units_as_line.strip().replace('\xc2\xb0C', 'C').split('\t')

	table_header = ''

	for i in range(len(variables)):
		table_header = table_header + '{} ({})\t'.format(variables[i], units[i])

	return table_header.strip()



# This functions reads the infile and returns the information for the 
# table-head header for each file, the names of each step and a list that 
# contains lists with the data from each step.
# I don't like that it does so much, but separating these functions would 
# have meant to go through the file several times which I liked even less.
def extract_data(infile):
	all_data = []
	steps = []
	step_data = []
	table_header = None
	collect_data = False
	
	skip_so_many = 3

	with open(infile, 'r', encoding='utf-8', errors='ignore') as f:
		for line in f:
			# Before the data of the first step is a lot of text that
			# shall be ignored. Thus all "collect data stuff" is 
			# switched on at the first occurence of the keyword '[step]'.
			if '[step]' in line and len(step_data) == 0:
				collect_data = True

				# After the keyword < [step] > some information follows 
				# which is not the data.
				steps.append(extract_stepname(f.readline()))
				names_as_line = f.readline()
				units_as_line = f.readline()
				table_header = create_table_header(names_as_line, units_as_line)

			# If the keyword step occurs a second (third, etc) time, the step 
			# taken care of before is over. All the collected step_data
			# shall be stored in all_data and the collection of the 
			# step data for the next step shall be started.
			elif '[step]' in line and len(step_data) > 0:
				all_data.append(step_data)
				step_data = []

				steps.append(extract_stepname(f.readline()))
				# I don't need to extract te table header again.
				f.readline()
				f.readline()

			# collect_data is just to skip the first lines of the file. 
			# As soon as the first step starts it is set to True.
			# Thus the keyword < [step] > itself would be collected as data
			# if I would not take care of it.
			if collect_data and ('[step]' not in line):
				# Don't strip the linebreak at the end of each line,
				# because then I have to put it there again later when
				# writing to the file.
				step_data.append(line)

		# The last step will NOT be finished with the keyword '[step]'.
		# Thus I need to store it in all_data manually.
		all_data.append(step_data)

	return all_data, steps, table_header



# This function writes the data for each step into a single file.
# step_data is a list.
def write_step_data_into_file(outfile_name, table_header, step_data):
	with open(outfile_name, 'w', encoding='utf-8', errors='ignore') as f:
		# The table header should NOT have a linebreak at the end.
		f.write('{}\n'.format(table_header))
		for line in step_data:
			f.write(line)



# Create a directory just for this measurement and move the files into it
# to keep order.
def move_to_new_directory(path, infile, outfiles):
	# The folder name is basically the end of the path to the file.
	folder_name = 'separated_steps_of_{}/'.format(infile.split('/')[-1])
	to_here = path + folder_name


	# Make the new directory ...
	# ATTENTION: If the directory already exists, an os-message is displayed
	# to the user. I have no influence over this.
	# I could delete the whole folder, but the user ma already have files
	# in there which shall not be deleted.
	try:
		os.mkdir('{}'.format(to_here))
	except FileExistsError:
		this = '\n\nERROR: Folder exists! Please delete the existing folder '
		that = 'and try aggain'
		print(this + that)
		input("Please press ENTER to continue.")
		return
		

	# ... move all files there.
	# But beware, < outfiles > contains just the path's to the new files.
	# The original file will remain in the original folder.
	for element in outfiles:
		from_here = element
		os.system('mv "{}" "{}"'.format(from_here, to_here))

	print("""\n
A new folder with the filenames name was created. It contains the files with the 
data for each step.
ATTENTION: The original file was NOT moved into this folder.
""")


# The function that executes all of the above stuff.
def main():
	print("""\n\nStep separation\n
This program separates all steps in DSC-files from each other and returns as 
many files as there are steps.

ATTENTION: IT IS ASSUMED THAT THE COLUMNS ARE SEPARATED WITH TABS!

ATTENTION: It is assumed that the keyword < [step] > is followed by three 
text-lines which contain the following (in this order):
line 1.: name of the step
line 2.: table header -> variables
line 3.: table header -> units

ATTENTION: This probably works just with files exported from the TA Instruments 
TRIOS software. Other vendors probably structure their files differently.
""")

	path = af.get_path()
	infile = af.get_infile(path)


	all_data, steps, table_header = extract_data(infile)


	outfiles = create_filenames(path, steps)


	for i in range(len(outfiles)):
		write_step_data_into_file(outfiles[i], table_header, all_data[i])


	move_to_new_directory(path, infile, outfiles)





## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## 
## ## ## ## ## ## ##                            ## ## ## ## ## ## ## 
## ## ## ## ## ## ## PROGRAM IS EXECUTED HERE   ## ## ## ## ## ## ##
## ## ## ## ## ## ##                            ## ## ## ## ## ## ## 
## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## 

# When this program is called on the console, main() is executed.
if __name__ == '__main__':
	main()






















