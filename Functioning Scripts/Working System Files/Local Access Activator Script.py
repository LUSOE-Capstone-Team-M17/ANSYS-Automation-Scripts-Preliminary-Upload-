# LOCAL ACCESS FOR ANSYS
# Activates access to the local command line
# Sets up the logging system

import clr
clr.AddReference("System") 
from System.Diagnostics import Process, ProcessStartInfo
from System.Threading import Thread, ThreadStart
import time
import csv

# Logging Activation
# Makes logging accessible to Ansys
# home_folder is derived from initialize 
import os

logger_path = home_folder + r"\logger.txt"

def print_txt(string, file_path):
    with open(file_path, 'w') as file:
        file.write(string)
def append_txt(string,file_path):
    with open(file_path,'a') as file:
        file.write(string)
def read_txt(file_path):
    with open(file_path) as file:
        return file.read()
def log_str(string):
    append_txt("\n" + str(time.ctime()) + " - " + string,logger_path)
def read_csv(file_name, dir_path, skip_header=True):
    """
    Read a CSV using Python 3 text mode logic.
    Using newline='' is the official recommendation to avoid iterator errors.
    """
    if not file_name.lower().endswith('.csv'):
        file_name += '.csv'
    file_path = os.path.join(dir_path, file_name)
    
    if not os.path.exists(file_path):
        return []

    data_array = []
    try:
        # Open with newline='' to ensure csv.reader handles line endings correctly
        with open(file_path) as csvfile:
            reader = csv.reader(csvfile)
            if skip_header:
                try:
                    next(reader) # Skip the header row
                except StopIteration:
                    return []
            
            for row in reader:
                data_array.append(row)
    except Exception as e:
        print("Error reading CSV: "+str(e))
        return []
    return data_array

def write_csv(data, file_name, dir_path):
    """
    Write to CSV using csv.writer and newline='' to prevent blank lines 
    and 'bytes vs strings' iterator exceptions.
    """
    if not file_name.lower().endswith('.csv'):
        file_name += '.csv'
    save_path = os.path.join(dir_path, file_name)
    
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

    try:
        # Ensure data is a list of lists (2D)
        if data and not isinstance(data[0], (list, tuple)):
            data = [data]

        # Use 'w' mode with newline='' for the csv.writer to work correctly
        with open(save_path) as f:
            writer = csv.writer(f)
            writer.writerows(data)
            
        print("Successfully saved " + str(file_name) + " to " + str(dir_path))
    except Exception as e:
        print("Error writing CSV: "+str(e))


print("\nLogging commands have been initialized!")
print("Available commands:")
print("print_txt(string,file_path)")
print("read_txt(file_path)")
print("log_str(message)")
print("read_csv")
print("write_csv")

# Command Line Activation
# --- Async Output Handlers ---

def output_data_received(sender, e):
    """Event handler for standard output. Prints to Ansys Console."""
    if e.Data is not None:
        print(e.Data)

def error_data_received(sender, e):
    """Event handler for standard error. Prints to Ansys Console."""
    if e.Data is not None:
        print("!! ERROR: " + e.Data)

# --- Command Execution Core ---

def _execute_cmd_logic(cmd):
    """
    Internal logic that runs on a background thread.
    Captures output and prints it safely.
    """
    try:
        psi = ProcessStartInfo()
        psi.FileName = "cmd.exe"
        psi.Arguments = "/c " + cmd
        psi.UseShellExecute = False
        psi.RedirectStandardOutput = True
        psi.RedirectStandardError = True
        psi.CreateNoWindow = True 
    
        p = Process()
        p.StartInfo = psi
        p.OutputDataReceived += output_data_received
        p.ErrorDataReceived += error_data_received
        
        p.Start()
        p.BeginOutputReadLine()
        p.BeginErrorReadLine()
    
        # Wait for completion in the background
        p.WaitForExit()

        if p.ExitCode != 0:
            print(">>> COMMAND FINISHED WITH EXIT CODE {0}".format(p.ExitCode))
            
    except Exception as e:
        print("!!! CRITICAL SCRIPT ERROR:\n{0}".format(e))

# --- Public API ---

def form_seq_cmd(cmd_list):
    """
    Concatenates a list of commands into a single string.
    Uses '&&' so that execution stops if any command in the sequence fails.
    """
    if not cmd_list:
        return ""
    return " && ".join(cmd_list)

def send_cmd(cmd):
    """
    Spawns a new background thread to execute the command. 
    Output is printed directly to the console.
    """
    print("--------------------------------------------------")
    print("> {0}".format(cmd))
    print("--------------------------------------------------")
    
    # Create and start a background thread
    # This prevents the main Ansys UI from locking up while waiting for the command
    worker = Thread(ThreadStart(lambda: _execute_cmd_logic(cmd)))
    worker.IsBackground = True
    worker.Start()

print("\nCommand Line commands have been initialized!")
print("To send Command Shell commands to the terminal, use send_cmd(str).")
print("To send multiple commands at a time, use form_seq_cmd(cmd_list) before sending.")
print("Once a command has been sent, the output from the terminal will print in this window.")
print("WARNING: This operation is somewhat sketchy and prone to freezing. Functionality is limited.")