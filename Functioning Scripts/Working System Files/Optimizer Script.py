# OPTIMIZER

import optimize as opt
import time
import numpy as np

# Start logging
opt.log_str("Optimizer - I'm awake and ready to optimize!")

# USER INPUT: 
# Set the bounds for your variables of optimization below
bounds1 = [0.0004,0.002] # Current - damping ratio
bounds2 = [180000000000,225000000000] # Youngs modulus, GPa
bounds3 = [7800,7900] # Density, kg/m3
bounds = [bounds1,bounds2,bounds3]
min_bounds = np.array([bounds1[0], bounds2[0], bounds3[0]])
max_bounds = np.array([bounds1[1], bounds2[1], bounds3[1]])

# Factorial design settings
facsets=[3,2] # ndims, nlevels

# Set up the particle swarm optimizer settings
upper_b = 1
lower_b = -1

settings = {
    'dimensions': 3,
    'options': {'c1': 0.5, 'c2': 0.3, 'w': 0.9},
    'iters': 700,
    'n_particles': 500,
    'bounds': (min_bounds, max_bounds)
}


# MAIN OPTIMIZATION LOGIC
# Check the status before optimizing
try:
    exist_results = opt.read_data()
    stepno = float(exist_results["steps"][-1])
except:
    stepno = 0

if stepno == 0: # This is the first pass, or maybe an error occurred
    # Start the optimization process
    opt.log_str("Optimizer - No existing steps detected.")
    opt.log_str("Optimizer - Starting factorial design generation...")
    fact_array = opt.factorial_design(facsets[0],facsets[1])
    fact_array = opt.scale_array(fact_array,bounds)

    # Publish the design (no data exists yet)
    opt.init_opt_temp(["Damping Ratio", "Stiffness", "Thickness"])
    post_data = opt.post_Xdata(fact_array)
    opt.log_str("Optimizer - Factorial design generated and published. Waiting for Ansys...")
else: # This is not the first pass. Factorial design had better be complete with results.
    opt.log_str("Optimizer - step #" + str(stepno) + " received. Training model to find step #"+str(stepno+1)+".")

    [Xdata,Ydata]=[exist_results["Xdata"],exist_results["Ydata"]]
    
    # Train the surrogate
    omegas = opt.train_weights(Xdata,Ydata)
    def function(Xtest):
        # pass the trained Xdata (training set) and omegas into test_surrogate
        return float(opt.test_surrogate(Xtest, Xdata, omegas))
    
    # Start timing
    start_time = time.time()
    # Run the genetic algorithm (pass the function object, don't call it)
    [nextpoint,best_cost] = opt.optimize(function, settings)
    # End timing
    end_time = time.time()
    
    elapsed_time = end_time - start_time
    
    # post_data expects Xdata and Ydata; nextpoint is a single row (list),
    # so wrap it in a list and provide empty Y (no result yet).
    
    opt.post_Xdata([nextpoint])
    print("Found a winner: "+str(nextpoint)+", with a cost function of "+str(best_cost)+".")
    opt.log_str("Optimizer - point swarm optimization completed in " + str(elapsed_time) + " seconds. Ansys, it's your turn.")

