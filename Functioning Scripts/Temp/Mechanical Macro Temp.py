# Mechanical Initializer
# To be appended to in order to initialize mechanical functions before they are run.
# Mechanical functions are not persistent when run thru Workbench :'(

import os
import math

# PROJECT SETUP

# Label the model and its components
# Check that you don't have extra sims, or adjust these indices.
model = ExtAPI.DataModel.Project.Model
static_structural = model.Analyses[0]                     # Static Structural sim
modal_analysis = model.Analyses[1]                        # Modal sim
random_vibration = model.Analyses[2]                      # Random Vibration sim
coordinate_systems = model.CoordinateSystems              # Contains coordinate systems in the model
bolt_pretensions = static_structural.Children[1].Children # Bolt pretensions
SYS_container = model.Geometry.Children[0]                # Contains geometry bodies 
top_plate = SYS_container.Children[1]                     # Top plate geometry
drum_shell = SYS_container.Children[2]                    # Drum geometry 
modal_analysis_settings = DataModel.GetObjectById(43)     # Solving settings for modal analysis


# Shows a message in the Mechanical GUI
def show_msg(str):
    ExtAPI.Application.Messages.Add(Ansys.Mechanical.Application.Message(str, MessageSeverityType.Info))

# Modal Setup Function
def set_modal_range(rangemin,rangemax):
    modal_analysis.Children[1].SearchRangeMinimum = Quantity(rangemin,"Hz")
    modal_analysis.Children[1].SearchRangeMaximum = Quantity(rangemax,"Hz")

# INITIALIZE COORDINATE SYSTEMS & RESPONSE PSD SENSORS

def clear_sensors_coords(): # use this before creating new sensors and coordinates
    [child.Delete() for child in list(random_vibration.Solution.Children)[1:]] # clear out sensors
    [child.Delete() for child in list(coordinate_systems.Children)[2:]] # clear out coordinate systems

# Calculate the placement of the sensors:
# How many sensors (by ring)?
def place_sensors(numSensorsPerRing,numRings):
    numSensors = numSensorsPerRing*numRings
    
    # Change these if the dimensions of the drum changes
    drumBottom = -1.0829
    drumTop = 6.324e-2
    drumRadius = 0.281
    sensorReferenceLocation = [-0.51153e-8, -0.51143, -1.191e-3]
    
    # Calculate placement
    sensorHeightIncrement = (drumTop-drumBottom)/numRings
    sensorHeightStart = drumBottom + sensorHeightIncrement/2
    angularOffsetIncrement = 2*math.pi/numSensorsPerRing
    xStart = sensorReferenceLocation[0] + drumRadius
    zStart = sensorReferenceLocation[2]
    sensorLocations = [None]*(numSensors)
    for i in range(numRings):
        for j in range(numSensorsPerRing):
            y = sensorHeightStart + sensorHeightIncrement*i
            angularOffset = angularOffsetIncrement*j
            x = math.cos(angularOffset)*xStart - math.sin(angularOffset)*zStart
            z = math.sin(angularOffset)*xStart + math.cos(angularOffset)*zStart
            sensorLocations[i*numSensorsPerRing + j] = [x, y, z]
    
    # Initialize custom coordinate systems for sensors
    coord_bucket = [coordinate_systems.AddCoordinateSystem() for i in sensorLocations]
    for s, sensor in enumerate(coord_bucket):
        coord_bucket[s].Name = "Sensor" + str(s+1)
        x = sensorLocations[s][0]
        y = sensorLocations[s][1]
        z = sensorLocations[s][2]
        coord_bucket[s].SetOriginLocation(Quantity(x,'m'), Quantity(y,'m'), Quantity(z,'m'))
        coord_bucket[s].RotateY(-angularOffsetIncrement*s*360/2/math.pi)
    
    # Initialize the response PSD sensors based on coordinate systems
    response_psd_sensors = [random_vibration.Solution.AddResponsePSD() for i in range(numSensors*3)]
    for idx, response_psd_sensor in enumerate(response_psd_sensors):
        response_psd_sensor.LocationMethod = LocationDefinitionMethod.CoordinateSystem
        response_psd_sensor.CoordinateSystemSelection = coord_bucket[int(floor(idx/3))]
        response_psd_sensor.ResultType = ProbeResultType.DeformationProbe
        if idx % 3 == 0:
            response_psd_sensor.ResultSelection = ProbeDisplayFilter.XAxis
            response_psd_sensor.Name = "Sensor " + str(int(floor(idx/3))+1) + " Axis X Probe"
        elif idx % 3 == 1:
            response_psd_sensor.ResultSelection = ProbeDisplayFilter.YAxis
            response_psd_sensor.Name = "Sensor " + str(int(floor(idx/3))+1) + " Axis Y Probe"
        elif idx % 3 == 2:
            response_psd_sensor.ResultSelection = ProbeDisplayFilter.ZAxis
            response_psd_sensor.Name = "Sensor " + str(int(floor(idx/3))+1) + " Axis Z Probe"

# Function to suppress three bolts
# If first is 0 => no bolts suppressed
def suppress_bolts(bolt_vec):
    for bolt_pretension in bolt_pretensions:
        bolt_pretension.Suppressed = False
    if bolt_vec[0] == 0:
        pass
    else:
        bolt_pretensions[bolt_vec[0]-1].Suppressed = True
        bolt_pretensions[bolt_vec[1]-1].Suppressed = True
        bolt_pretensions[bolt_vec[2]-1].Suppressed = True

# Function which solves all three simulations
def update_results():
    show_msg("Solving Static Structural...")
    static_structural.Solution.Solve()
    
    show_msg("Solving Modal...")
    modal_analysis.Solution.Solve()
    
    show_msg("Solving Random Vibration...")
    random_vibration.Solution.Solve()

# Function which evaluates modal results to a string array [Mode, Frequency]
def extract_modal():
    show_msg("Extracting modal results...")
    modal_result_objs = [child for child in modal_analysis.Solution.Children if child.Name == "Total Deformation"]
    modal_result_obj = modal_result_objs[0]
    modeNumCol = modal_result_obj.TabularData["Mode"]
    frequencyCol = modal_result_obj.TabularData["Frequency"]
    modalData = [[str(modeNumCol[i]), str(frequencyCol[i])] for i in range(len(list(modeNumCol)))]
    modalData.insert(0,["Mode","Frequency"]) # adding a title row
    return modalData

# Function which evaluates random vibration results to a string array [Frequency, PSD Accel]
# Credit: https://blog.ozeninc.com/resources/using-python-to-export-tabular-data-from-within-ansys-mechanical
def extract_randvibe():
    show_msg("Extracting PSD results...")
    numSensors = len(coordinate_systems.Children)-2
    psdResults = random_vibration.Solution.Children
    psdData = [[[] for _ in range(numSensors*6)]]  # three sensors, with a frequency column and a PSD column for each
    for i in range(len(psdResults)-1):
        psdResults[i+1].Activate()
        Pane = ExtAPI.UserInterface.GetPane(MechanicalPanelEnum.TabularData)
        Con = Pane.ControlUnknown
        if len(psdData) < Con.RowsCount:
            psdData.extend([[] for _ in range(numSensors*6)] for __ in range(Con.RowsCount-len(psdData)))
    
        for R in range(Con.RowsCount):
            for C in range(Con.ColumnsCount-1):
                psdData[R][C+i*2] = Con.cell(R+1,C+2).Text.ToString()
    return psdData

# Function for writing nested lists to CSV, data must be strings
def write_csv(data,file_name,dir_path):
    saveName = os.path.join(dir_path,file_name+'.csv')
    show_msg("Writing CSV to " + saveName)
    with open(saveName, "w") as f:
        for line in data:
            for col in line:
                f.write(col + ', ')
            f.write("\n")
    show_msg(file_name+" has been saved to "+dir_path)

# OPTIMIZATION FUNCTIONS
# Parametric functions

# Set top plate thickness
def set_plate_thick(thickness):
    top_plate.Thickness = Quantity(thickness,'m')

def set_drum_thick(thickness):
    drum_shell.Thickness = Quantity(thickness,'m')

def set_damping_ratio(ratio):
    modal_analysis_settings.StructuralDampingCoefficient = ratio

# # Prints to the message bubble in Mechanical
# ExtAPI.Application.Messages.Add(Ansys.Mechanical.Application.Message("Available commands for analysis: \nclear_sensors_coords() \nplace_sensors(numSensorsPerRing,numRings) \nsuppress_bolts(bolt_vec), bolt_vec = [#,#,#] \nupdate_results() \nset_modal_range(rangemin,rangemax) \nset_plate_thick(thickness) \nset_damping_ratio(ratio)", MessageSeverityType.Info))
# ExtAPI.Application.Messages.Add(Ansys.Mechanical.Application.Message("Available commands for data handling: \nextract_modal() \nextract_randvibe() \nwriteCSV(data,fileName,dir_path)", MessageSeverityType.Info))
# ExtAPI.Application.Messages.Add(Ansys.Mechanical.Application.Message("Available commands for design changes: \nset_plate_thick(thickness) \nset_drum_thick(thickness) \nset_damping_ratio(ratio)", MessageSeverityType.Info))
write_csv(extract_randvibe(),"PSD DataPoint 6",r"C:\Users\hepha\Documents\academics\CAPSTONE\Scripts\Functioning Scripts\Temp")