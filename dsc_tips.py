#    "Kinetic-Triplet-Determination - dsc_tips" (v1.0)
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

# This file contains just some tips how to get the best results and how to avoid
# some pitfalls.


def main():
	print("""\n\nTips how to get good results.\n
This text contains some tips how to get the best results from DSC measurements and how to avoid some pitfalls.
These are some hints how to work gained by several years of "experience" working with the methods and instruments.
This experience was won by working with a (very) slow curing material that did NOT experience a significant change in the heat capacity due to transition from liquid to solid. See paper [1] (open access) for details.

See at the end of section III what I recommend to do with fresh files to get a first impression of the data.

I - The experiment itself

- It is assumed that you know how to handle the DSC instrument.
- For isothermal experiments at low temperature: make sure the sample reached full cure by ramping to a (significantly) higher temperature and leaving the sample there.
  Be careful that the temperature is not too high, because that will lead to degradation.
- For isothermal experiments: After the ramp reaches the final temperature, keep the sample at this temperature for at least half an hour (better one hour). 
  This is again to make sure the sample reaches full cure.
- See paper [1] (open access) for details.
  
- Important: Run the SAME experiment again with the fully cured sample to get good post-cure data.
  If the isothermal cure was too long to be run again than have the isothermal phase for just one hour and use the final heat flow value as the post-cure baseline.

- - - - - - - - - - - - - - - - - - - - - -

II - The data

1.: Don't use bad data.
- Cut away the first 30 seconds (or maybe more) of the experiment. 
  Whenever the temperature changes, each DSC needs approx. this time to reach equilibrium.
  Everbody does this, nobody writes about it in the papers.
- DON'T cut the "30 seconds settling time" between e.g. the ramp and the isothermal part (to make sure the samples reaches full cure) in dynamic experiments or in similar situations.
  If full cure was NOT reached, curing takes place during THIS time. At higher temperatures A LOT of curing takes place. Thus this is crucial data and you just have to live with the fact that it is a bit less than perfect.
- Everybody does this but nobody mentions it in the papers. It's mouth-to-mouth knowledge you learn about during conference dinners.


2.: The baseline
- Often a straight baseline is assumed.
- However, gelation of a polymer leads to a change in the heat capacity which in turn influences the heat flow data.
- Don't worry about this too much. Most likely is the difference between experiments larger than the difference caused by this.
-  HOWEVER, the last statement may NOT be true for your material! Check this by performing Temperature Modulated DSC experiments (if possible) to see how much the heat capacit actually changes.

- The baseline is often acquired by just drawing a straight line from start to end.
  The data published in the majority of articles is from the kind where this is a valid approach.
- This however does not work if the sample does not reach full cure.
  It did not work in my case (since the material was so slow curing that it did not reach full cure during the temperature ramps).
- It is better to subtract the post-cure run data from the cure run data. 
  This approach is used by other researchers and one either stumbles over this information or it is again "conference dinner knowledge".

- Be careful with long runs with (really) small HF values. The DSC (instrument) baseline may shift during the experiment.
  This can not be distinguished from the real heat flow.
  However, don't worry. I did experiments over almost three days and if there was error caused due to baseline shift it was well within the 'between-experiments-error'.


3.: isothermal vs. dynamic activation energy
- It has been shown that the isoconversional activation energy can be different for small conversion values if the data was from dynamic or isothernal experiments. See reference in [1].
- For some materials it may also differ for higher conversions. Usually no explanations are given, but it may due to high energy processes which are simply not triggered in isothermal experiments (see [1]).

- - - - - - - - - - - - - - - - - - - - - -

III - The programs

0.: IMPORTANT THINGS
- All programs are python 3 programs.
- All programs are to be called from the command line.
- You need to have numpy and scipy installed for python 3

- (Almost) All files can be called separately and the specific program will work.
- If < main.py > is called it comes with a menu in which the program to be executed can be chosen. This us maybe a bit more convenient.
- I've tried to account for the most common input errors. However, naturally that will not cover all that can go wrong. The programs work if the user follows the instructions given on the screen and does not deliberately try to break the system.

- The FULL name of an input-file is to be given. This includes its extension like .txt or .csv or whatever
- Some calculations can take a LONG time (dependent on the parameters given). This is just the way it is. Be patient.
- Time is often given in MINUTES in DSC rawdata. This is converted to seconds with the information given by the user.

- I did NOT test these programs under a non-GNU/Linux operating system. For private projects I don't care about those.

- Below is the order of how I would call the programs on a fresh rawdata-files to get an impression of the data before a deeper analysis. 
- After a deeper analysis (mostly after cleaning the rawdata from "bad data", see above) I would run just the programs in connection with the isoconversional method. However, the results should not be too different and the differences should be within the "between experiments" error.
- It is enough to call < main.py >. There a menu is offered to easily access all sub-programs.


1.: step_separator.py
- The rawdata files from the DSC usually contain some meta-information AND the data from all steps in one file. 
  The programs can't work with this. Thus I decided to first extract the data for each step from the rawdata and save them in a way that the structure of the data is always the same so that I don't need to worry aboout it later.
- For the DSC I worked with, the data for each step was separated by the keyword < [step] >, followed by the name of the step in the next line, followed by the variable names, followed by the variable units, and finally followed by the data for this step until the same keyword appeares again.

- step_separator.py takes the rawdata files, looks for the keyword, extracts the data for one step and saves it in a new file with the name of the step. All these files (but NOT the rawdata file!) are then moved to a new folder.
- Try it by calling step_separator.py and use < 00_EXAMPLE_STEP_SEPARATOR.txt > as input-file.

- ATTENTION: ALL SUBSEQUENT PROGRAMS PROCESS JUST FILES WHICH ARE THE OUTPUT OF < step_separator.py >!


2.: stitch_steps_together.py
- Sometimes (often?) two steps need to be seen as one experiment (e.g. for dynamic experiments because the full cure was not reached during the ramp). In this case these two steps need to be joined into one file to be able to handle the information as a whole.
- This is what will happen when < stitch_steps_together.py > is called. One continuous data file will be created from two (or more) input files. 
- The time will be calculated according to the information given by the user.


3.: post_cure_run_subtractor.py
- As written above is it under certain circumstances advisable to subtract the post cure run of the same experiment with the same (fully cured) sample to get the actual (experimental) baseline.
- This is what happens when < post_cure_run_subtractor.py > is called. A new file with the subtracted data will be created.


4.: correct_baseline_to_zero.py
- The instrument baseline is different from experiment to experiment. Thus does NOT matter since the differences are small (or should be) and just the difference of the experimental data to this baseline is of interest.
- However, it is annoying and impractical to have a baseline different from zero. Since this shift of the instrument baseline does not matter, the whole DSC data can be shifted in a way that the full cure, steady state heat flow becomes zero.
- This is what happens when < correct_baseline_to_zero.py > is called. A new file with the baseline shifted (to zero) data will be created.
- The (original) baseline value which needs to be subtracted from the whole dataset can either be given by the user, or calculated from a certain amount of data (e.g. 5 minutes 23 seconds) from the end of the file.

- ATTENTION: All subsequent programs assume that the data has a baseline with value zero.


5.: total_heat_calculator.py
- From a given heat flow curve the total heat of reaction can be calculated.
- It is a simple multiplication of the heat flow at a given measurement times the time increment between measurements followed by an addition of all these values.
- After < total_heat_calculator.py > is called the calculation is done and the total heat for the given file will be displayed in the terminal.
- Whenever the total heat is needed and NOT provided by the user, this program is called.


6.: conversion_into_file.py
- Sometimes it is nice to have the rawdata and the conversion in one file.
- A call of < conversion_into_file.py > will result in a file that has exactly that.
- This is just for convenience in certain situation and otherwise done automatically if necessary.


7.: calculate_activation_energy.py
- THIS is probably why you, dear user, are here. One wonders why I put it so far down.
- From several files which contain the relevant data (e.g. just the isothermal step, post-cure-run subtracted and baseline corrected) the conversion dependent activation energy can be calculated. 
- After calling < calculate_activation_energy.py > the necessary calculations will be performed. ATTENTION: This may take some time! Afterwards the results will be saved in a separate file.

- Conversion and total heat will be calculated individually for each file if no value is given.

- ATTENTION: It is important, that the folder with the files contains JUST the files to be used for the isoconversional calculations!
- The program is dumb and can not check beforehand if a file is valid or not.

- The total heat of reaction will be determined automatically from each file


8.: calculate_common_compensation_parameters.py
- This program uses the compensation effect to calculate the pair of pre-factor and activation energy for a number of known models. A new file is created which contains the necessary values for the user to reproduce the results.
  Per datafile these values will then be fitted linear which yields the compensation parameters for this specific measurement. Another new file is created which contains the values of the pre-factor / activation energy-pairs and the calculated fitting factors.
  After all files are processed, the mean value of the compensation parameters is calculated and provided ti the user. Another file is created with this information.

- Conversion and total heat will be calculated individually for each file if no value is given.

- The compensation effect can be used JUST for dynamic experiments which had a LINEAR temperature ramp.

- ATTENTION: It is important, that the folder with the files contains JUST the files to be used for the calculations!
- The program is dumb and can not check beforehand if a file is valid or not.


9.: kinetic_function_calculation.py
- With a given acitvation energy and Arrhenius pe-factor the actual kinetic function can be calculated from the data. 
- This is what happens when < kinetic_function_calculation.py > is called for each file in a given folder. 
- Per input file a file is created which contains the values for the actual kinetic function and values for other kinetic models to be able to easily compare.

- Conversion and total heat will be calculated individually for each file if no value is given.

- The activation energy can either be provided in a file or as an equation. 
- For the latter it has to be stated how man "sections" the equation has.
- For each section the equation has to be stated and conversion domain for which this equation is valid.
- Numpy and python mathematical expressions can be used.
- I've tried to cover for the most common mistakes but some user input may lead to a crash of the program if the provided expression can not be evaluated.

- ATTENTION: It is important, that the folder with the files contains JUST the files to be used for the calculations!
- The program is dumb and can not check beforehand if a file is valid or not.


10.: prediction.py
- When the parameters are determined the heat flow of a DSC experiment can be calculated.
- This is what happens when < prediction.py > is called. The result will be saved in a new file.
- Isothermals and ramps can be predicted but just one at a time.
  If an experiment consists of a ramp followed by an isothermal, first the ramp has to be predicted. At the end of the ramp the conversion will have reached a certain value. This value has to be used as initial conversion for the isothermal step.


I wish fun with using this program.


[1] S. Heinze and A. T. Echtermeyer, A Practical Approach for Data Gathering for Polymer Cure Simulations, Appl. Sci. 2018, 8(11), 2227; https://doi.org/10.3390/app8112227

""")


## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## 
## ## ## ## ## ## ##                            ## ## ## ## ## ## ## 
## ## ## ## ## ## ## PROGRAM IS EXECUTED HERE   ## ## ## ## ## ## ##
## ## ## ## ## ## ##                            ## ## ## ## ## ## ## 
## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## 

# When this program is called on the console, main() is executed.
if __name__ == '__main__':
	main()




