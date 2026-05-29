# # ANALYZER MODULE

# Start logging
log_str("Ansys - I'm awake and ready to analyze!")

# USER INPUT

# Includes only the points missing solution data 
existingY = read_Ydata()
existingX = read_Xdata()

completed = len(existingY)
remaining = len(existingX[0])-completed

if remaining >= 1:
    log_str("Ansys - Detecting a factorial design. Buckle up, this may take a while...")
log_str("Ansys - Received step #"+str(completed+1)+", beginning the analysis.")

for i in range(remaining):
    j = i+completed
    Xdata = read_Xdata()
    
    log_str("Ansys - Solving step #"+str(j+1)+".")
    # Set the parameters at the given data point.
    # If you change this, be careful to change your temp file initialization too.
    ClearData()
    SetDamping(Xdata[0][j])
    SetElasticModulus(Xdata[1][j])
    SetDensity(Xdata[2][j])
    log_str("Ansys - Set to parameters: Damping Ratio = "+str(Xdata[0][j])+", Elastic Modulus = "+str(Xdata[1][j])+", Density = "+str(Xdata[2][j])+".")
    # Simulate and publish
    UpdateSims()
    PublishResults(j)
    log_str("Ansys - Solved! Results are published in the home folder.")

log_str("Ansys - I'm out. Comparator, it's all you...")