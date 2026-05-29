import os
import time
import csv
import subprocess
import threading
import platform

# --- PATH CONFIGURATION ---
# Ensure home_folder is defined. Using os.path.join handles / vs \ automatically.
# logger_path = os.path.join(home_folder, "logger.txt")

def print_txt(string, file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(string)

def append_txt(string, file_path):
    with open(file_path, 'a', encoding='utf-8') as file:
        file.write(string)

def read_txt(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def log_str(string):
    # Ensure logger_path is accessible here
    append_txt("\n" + str(time.ctime()) + " - " + string, logger_path)

# --- CSV OPERATIONS ---

def read_csv(file_name, dir_path, skip_header=True):
    if not file_name.lower().endswith('.csv'):
        file_name += '.csv'
    file_path = os.path.join(dir_path, file_name)
    
    if not os.path.exists(file_path):
        return []

    data_array = []
    try:
        # Linux/Python 3 standard for CSV
        with open(file_path, mode='r', newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            if skip_header:
                try:
                    next(reader)
                except StopIteration:
                    return []
            for row in reader:
                data_array.append(row)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return []
    return data_array

def write_csv(data, file_name, dir_path):
    if not file_name.lower().endswith('.csv'):
        file_name += '.csv'
    save_path = os.path.join(dir_path, file_name)
    
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

    try:
        if data and not isinstance(data[0], (list, tuple)):
            data = [data]

        # Mode changed to 'w' (was missing in original)
        with open(save_path, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(data)
            
        print(f"Successfully saved {file_name} to {dir_path}")
    except Exception as e:
        print(f"Error writing CSV: {e}")

# --- COMMAND EXECUTION CORE ---

def _execute_cmd_logic(cmd):
    """
    Cross-platform command execution using subprocess.
    This replaces the .NET Process logic.
    """
    try:
        # Determine shell based on OS
        is_windows = platform.system() == "Windows"
        executable = None if is_windows else "/bin/bash"
        
        # Start the process
        # bufsize=1 (line buffered) for real-time output
        process = subprocess.Popen(
            cmd,
            shell=True,
            executable=executable,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, # Merge stderr into stdout for easier logging
            text=True,
            bufsize=1
        )

        # Print output in real-time
        for line in iter(process.stdout.readline, ''):
            print(line.strip())
        
        process.stdout.close()
        return_code = process.wait()

        if return_code != 0:
            print(f">>> COMMAND FINISHED WITH EXIT CODE {return_code}")
            
    except Exception as e:
        print(f"!!! CRITICAL SCRIPT ERROR:\n{e}")

# --- PUBLIC API ---

def form_seq_cmd(cmd_list):
    """
    Works on both Windows and Linux (&& is standard for sequential execution).
    """
    if not cmd_list:
        return ""
    return " && ".join(cmd_list)

def send_cmd(cmd):
    """
    Spawns a standard Python thread to keep the UI responsive.
    """
    print("-" * 50)
    print(f"> {cmd}")
    print("-" * 50)
    
    worker = threading.Thread(target=_execute_cmd_logic, args=(cmd,))
    worker.daemon = True # Equivalent to IsBackground = True
    worker.start()

print("\nLinux-compliant Command Line commands initialized!")
print("Use send_cmd(str) for terminal commands.")