# WORKBENCH COMMAND ACTIVATOR SCRIPT
# Enables use of custom Workbench commands.

# Execute a Python script through the Mechanical program
def MechExecute(file_path): # i.e. r"C:\...\macro.py"
    macro_content = open(file_path).read()
    # Ansys organization
    analysis_system = GetSystem(Name="SYS")
    model_container = analysis_system.GetContainer(ComponentName="Model")
    # Execute the macro
    model_container.SendCommand(Language='Python', Command=macro_content)

# Change a parameterized value
def AdjustParameter(par_num,new_value): #i.e. "P1", 1.234
    par_value = str(new_value)

    designPoint1 = Parameters.GetDesignPoint(Name="0")
    adjusted_par = Parameters.GetParameter(Name=par_num)

    designPoint1.SetParameterExpression(
    Parameter=adjusted_par,
    Expression=par_value)
# Specific design value adjusters
def SetDamping(damping_value):
    AdjustParameter("P28", damping_value)
def SetElasticModulus(youngs_mod):
    AdjustParameter("P32", youngs_mod)
def SetShellThickness(shell_thickness):
    AdjustParameter("P26", shell_thickness)
# def SetBoltPretension(bolt_num,preload):
#     bolt_param = "P" + str(35 + bolt_num)
#     AdjustParameter(bolt_param, preload)
def SetDensity(density_value):
    AdjustParameter("P30", density_value)

# def set_params(Xdata,idx):
#     SetDamping(Xdata[0][idx])
#     SetElasticModulus(Xdata[1][idx])
#     SetShellThickness(Xdata[2][idx])

def read_Xdata():
    design_set = read_csv("opt_temp",home_folder)
    [X1_set, X2_set, X3_set] = [[],[],[]]
    for row in design_set:
        X1_set.append(row[1])
        X2_set.append(row[2])
        X3_set.append(row[3])
    return [X1_set,X2_set,X3_set]
def read_Ydata():
    design_set = read_csv("opt_temp",home_folder)
    Y_set = []
    for row in design_set:
        try:
            Y_set.append(float(row[4]))
        except:
            pass
    return Y_set

# Mechanical temp files
mech_macro_path = library_folder+r"\Mechanical Initializer.py"
mech_macros = read_txt(mech_macro_path)
mech_macro_temp_path = home_folder + r"\Mechanical Macro Temp.py"
# Mechanical macros can only be run from Workbench as script files, and must contain function definitions
def save_mech_command(command):
    macro = "\n".join([mech_macros,command])
    print_txt(macro,mech_macro_temp_path)
def run_mech_command():
    MechExecute(mech_macro_temp_path)
def add_mech_command(command):
    append_txt("\n"+command,mech_macro_temp_path)

# Execution and publishing of simulation
def ClearData():
    system1 = GetSystem(Name="Static Structural (ANSYS)")
    modelComponent1 = system1.GetComponent(Name="Model")
    modelComponent1.Refresh()
def UpdateSims():
    # save_mech_command("update_results()")
    # run_mech_command()
    save_mech_command("static_structural.Solution.Solve()")
    run_mech_command()
    save_mech_command("modal_analysis.Solution.Solve()")
    run_mech_command()
def PublishResults(idx):
    # save_mech_command('write_csv(extract_randvibe(),"PSD DataPoint '+str(idx)+'",r"'+home_folder+'")')
    # run_mech_command()
    save_mech_command('write_csv(extract_modal(),"PSD DataPoint '+str(idx)+'",r"'+home_folder+'")')
    run_mech_command()


print("\nWorkbench commands have been initialized!")
print("Available commands:")
print("MechExecute(file_path)")
print("MechCommand(command)")
print("AdjustParameter(par_num,new_value)")
print("SetDamping(damping_value)")
print("SetElasticModulus(youngs_mod)")
print("SetShellThickness(shell_thickness)")
print("SetBoltPretension(bolt_num,preload)")

print("\nMechanical commands have been initialized!")
print("To run a command in Mechanical, save it as a string.")   
print("Then save the command with save_mech_command(command), and execute with run_mech_command().")
print("Available commands for Mechanical:")
print("update_results()")
print("extract_modal()")
print("extract_randvibe()")
print("write_csv(data,file_name,dir_path)")