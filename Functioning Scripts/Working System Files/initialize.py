# Main Sequence

# For use in the Workbench Command line.
# Initializes Workbench & Mechanical macros
# Starts temp and log files
# Prints instructions for use

# USER SETUP:
# File folder to store logs and temps in
home_folder = r"C:\Users\hepha\Documents\academics\CAPSTONE\Scripts\Functioning Scripts\Temp"
# File folder which houses pre-written scripts
library_folder = r"C:\Users\hepha\Documents\academics\CAPSTONE\Scripts\Functioning Scripts\Working System Files"

# INITIALIZATION
# Set up using the activator scripts. 
def WBExec(file_name): # Executes a python script from the library folder in Workbench
    file_path = library_folder+"\\"+file_name+".py"
    SetScriptVersion(Version="25.2.170")
    RunScript(FilePath=GetAbsoluteUserPathName(file_path))

# ACTIVATOR SCRIPTS
WBExec("Local Access Activator Script") # Automatically sets up the Command Line access.
WBExec("Ansys Macros Activator Script")    # Automatically sets up the Workbench handling commands.

# Optimizer Access
def optimize():
    get_dir = "cd "+library_folder
    run_opt = "python "+"\"Optimizer Script.py\""
    command = form_seq_cmd([get_dir,run_opt])
    send_cmd(command)
def compare():
    get_dir = "cd "+library_folder
    run_opt = "python "+"\"Comparator Script.py\""
    command = form_seq_cmd([get_dir,run_opt])
    send_cmd(command)
    # Must be run thru the Terminal. Ansys cannot handle the modules necessary
# Running the Optimizer Script will either :
    # Detect no temp and log files. Initialize them and populate temp with a factorial design
    # Read the latest step in the optimization temp file, and create the next design

def analyze():
    WBExec("Analyzer Script")

def reinit():
    WBExec("initialize")

def main(iterlimit=150):
    for i in range(iterlimit):
        optimize()
        analyze()
        compare()