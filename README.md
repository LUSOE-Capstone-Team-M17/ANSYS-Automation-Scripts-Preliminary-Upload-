README
Instructions for optimization with Sam's auto package 
Capstone Team M17
This is a preliminary upload of Sam Vogan's scripts that automatically set ANSYS parameters and run simulations. This code is designed to handle all optimization calculations to minimize the required level of user input.

_____________________________________________________

This package should contain the following files:
sjv_11_24_2025.wbpj (Ansys 2025 R2) [a recent simulation, hopefully working but may need adjustment]
sjv_11_24_2025_files [directory containing simulation support files]
(in Temp):
	the pycache folder allowing stuff to access the files in temp
	opt_temp.csv [doesn't exist yet but will be generated for storing optimization steps]
	logger.txt [doesn't exist yet but will be generated for recording the steps/timing of the optimization
	PSD Datapoint X.csv [doesn't exist yet but will be generated for storing the Xth set of PSD data]
	Mechanical Macro Temp [doesn't exist yet but will be generated for storing custom Mechanical commands]
(in Working System Files):
	Analyzer Script.py [Ansys runs this internally to detect the next requested data point and simulate that data]
	Ansys Macros Activator Script.py [initialize.py runs this in Ansys internally to set up custom Ansys commands]
	initialize.py [run this file through the Workbench command line to automatically complete setup of this system]
	Local Access Activator Script [initialize.py runs this in Ansys internally to set up access to your computer and its files]
	Mechanical Initializer.py [support library for running macros in Mechanical]
	optimize.py [module containing many functions for use in DOE and optimization]
	Optimizer Script [Ansys runs this externally to detect existing data and generate new datapoints with surrogate modeling]
_____________________________________________________

IMPORTANT:
Before optimizing, go thru the following steps for customization:
1. Under initialize.py line 10 & 12, you have to define home_folder = r"C:\...\Mobile Files\Temp" and library_folder = r"C:\...\Mobile Files\\Working System Files" yourself. Do the same for home_folder in optimize.py, line 10.
2. Under Optimizer Script.py, you can change optimization settings in lines 12-29. Ask Gemini for help with the particle swarm settings if you want to change them.

REQUIREMENTS:
Installed versions of:
	Ansys 2025 R2
	Python, recent version containing:
		numpy
		time
		itertools
		os
		csv
		pyswarms

INSTRUCTIONS FOR USE:
1. Open Workbench, open the project file (.wbpj file)
2. Double click "Results" in the last sim to open Mechanical
3. Go to Workbench>File>Scripting>Open Command Line
4. Go to Workbench>File>Scripting>Run Script and choose Python file, select initializer.py. It should print out some available commands in the command window, and start a new window representing the command line output. Now those commands are active and ready to use if you want to poke around. 
5. Use optimize() to generate a factorial design if none exists, or use radial basis functions to find the next minimizing datapoint.
6. Use analyze() to simulate all datapoints in the .csv which do not have data filled out yet. Results publish to Temp.






