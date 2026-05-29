# Module containing utility functions for optimization tasks

import numpy as np
from itertools import product
import os
import csv
import time
import pyswarms as ps

home_folder = r"/home/sjvogan/Capstone/Functioning Scripts/Temp"
opt_temp_name = "opt_temp"
logger_path = os.path.join(home_folder, "logger.txt")

# Functions for handling files and logging
# Note these were previously defined, but only internally to Ansys.

def print_txt(string, file_path):
    """
    Overwrites the specified file with the provided string. Saves to .txt format only.
    Example usage: 
    
    print_txt("Hello, World!", "C:\\path\\to\\file.txt")
    """
    with open(file_path, 'w') as file:
        file.write(string)

def append_txt(string, file_path):
    """Appends the provided string to the end of the specified .txt file.
    Example usage: 
    
    append_txt("Hello, World!", "C:\\path\\to\\file.txt")
    """
    with open(file_path, 'a') as file:
        file.write(string)

def read_txt(file_path):
    """Reads and returns the entire content of the specified text file.
    Example usage: 
    
    read_txt("C:\\path\\to\\file.txt")
    """
    with open(file_path) as file:
        return file.read()

def init_log():
    """
    Initializes the logger file with a header and a start timestamp.
    Prints the initialization status to the console.
    """
    print_txt("Logging the Ansys macro process...\n", logger_path)
    log_str("Started logging...")
    print(f"Logger initialized. Logging to {logger_path}")

def log_str(string):
    """Appends a timestamped message to the logger file using ctime formatting.
    Example usage:
    
    log_str("This is a log message.")
    """
    append_txt("\n" + str(time.ctime()) + " - " + string, logger_path)

def read_csv(file_name, dir_path, skip_header=True):
    """
    Reads a CSV file from the specified directory.
    
    Uses newline='' for robust cross-platform line ending handling.
    Returns a list of rows, where each row is a list of strings.
    """
    if not file_name.lower().endswith('.csv'):
        file_name += '.csv'
    file_path = os.path.join(dir_path, file_name)
    
    if not os.path.exists(file_path):
        return []

    data_array = []
    try:
        with open(file_path, 'r', encoding='cp1252', newline='') as csvfile:
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
    """
    Writes a 2D list to a CSV file in the specified directory.
    
    Automatically creates the directory if it does not exist.
    Ensures correct formatting by using newline='' during the write process.
    """
    if not file_name.lower().endswith('.csv'):
        file_name += '.csv'
    save_path = os.path.join(dir_path, file_name)
    
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

    try:
        if data and not isinstance(data[0], (list, tuple)):
            data = [data]

        with open(save_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(data)
            
        print(f"Successfully saved {file_name} to {dir_path}")
    except Exception as e:
        print(f"Error writing CSV: {e}")

# Functions for custom optimization temp file handling
# Store and retrieve the steps of the optimization

def init_opt_temp(variables):
    """
    Creates or overwrites the optimization temporary CSV file with default headers.
    The headers include Step, Damping Ratio, Stiffness, Thickness, and Error.
    """
    [variable1, variable2, variable3]=variables
    header = [["Step", variable1, variable2, variable3, "Error"]]
    write_csv(header, opt_temp_name, home_folder)

def read_data():
    """
    Reads the optimization temporary file and returns a structured dictionary.
    
    The dictionary contains:
    - 'header': The first row of the CSV.
    - 'steps': A list of identifiers from the first column.
    - 'Xdata': Input variables returned as a list of columns.
    - 'Ydata': Output/Error values from the final column.
    """
    databucket = read_csv(opt_temp_name, home_folder, skip_header=False)
    if not databucket:
        return {"header": [], "steps": [], "Xdata": [], "Ydata": []}
    header = databucket[0]
    body = databucket[1:]
    stepnos = [row[0] for row in body]
    
    if body:
        ncols = max(len(r) for r in body) - 2
        databucketX = [[row[j] if j < len(row) else '' for row in body] for j in range(1, 1 + ncols)]
        databucketY = [row[-1] for row in body]
    else:
        databucketX = []
        databucketY = []
    return {"header": header, "steps": stepnos, "Xdata": databucketX, "Ydata": databucketY}

def post_data(Xdata, Ydata, append=True):
    """
    Unified entry point for posting X and Y data to the temporary file.
    
    Handles cases where only X, only Y, or both are provided.
    Maintains backwards compatibility with unified datasets.
    """
    if Xdata is None and Ydata is None:
        return
    if Xdata is not None and Ydata is not None:
        post_Xdata(Xdata, append=append)
        post_Ydata(Ydata)
        return
    if Xdata is not None:
        post_Xdata(Xdata, append=append)
    elif Ydata is not None:
        post_Ydata(Ydata)

def post_Xdata(Xdata, append=True):
    """
    Posts input variable rows (X) to the optimization temporary CSV.
    
    If append is True, it increments the step number based on existing data.
    If False, it re-initializes the file with the provided data.
    """
    X = np.array(Xdata)

    if X.size == 0:
        if not append or not read_csv(opt_temp_name, home_folder, skip_header=False):
            init_opt_temp()
        return

    if X.ndim == 1:
        Xrows = [X.tolist()]
    elif X.ndim == 2:
        Xrows = X.tolist()
    else:
        raise ValueError("Unsupported Xdata shape")

    if append:
        existing_rows = read_csv(opt_temp_name, home_folder, skip_header=False)
        if not existing_rows:
            init_opt_temp()
            existing_rows = read_csv(opt_temp_name, home_folder, skip_header=False)
        header = existing_rows[0]
        body = existing_rows[1:]
        try:
            last_step = int(body[-1][0]) if body else 0
        except:
            last_step = 0
    else:
        init_opt_temp()
        existing_rows = read_csv(opt_temp_name, home_folder, skip_header=False)
        header = existing_rows[0]
        body = []
        last_step = 0

    start_step = last_step + 1
    new_rows = []
    for i, row in enumerate(Xrows):
        new_rows.append([str(start_step + i)] + [str(v) for v in row] + [''])

    write_csv([header] + body + new_rows, opt_temp_name, home_folder)

def post_Ydata(Ydata):
    """
    Posts result values (Y) to the optimization temporary CSV.
    
    Fills existing rows that have empty 'Error' columns first.
    If more Y values remain than unfilled rows, new rows are appended with empty X fields.
    """
    Y = list(Ydata)
    existing_rows = read_csv(opt_temp_name, home_folder, skip_header=False)
    if not existing_rows:
        init_opt_temp()
        existing_rows = read_csv(opt_temp_name, home_folder, skip_header=False)

    header = existing_rows[0]
    body = existing_rows[1:]
    n_x = max(len(header) - 2, 0)

    unfilled_indices = [i for i, r in enumerate(body) if len(r) < len(header) or r[-1] in ['', None]]

    used = 0
    for ui in unfilled_indices:
        if used >= len(Y): break
        row = body[ui]
        if len(row) < len(header):
            row = row + [''] * (len(header) - len(row))
        row[-1] = str(Y[used])
        body[ui] = row
        used += 1

    new_rows = []
    if used < len(Y):
        try:
            last_step = int(body[-1][0]) if body else 0
        except:
            last_step = 0
        for i in range(used, len(Y)):
            new_rows.append([str(last_step + 1 + (i - used))] + ([''] * n_x) + [str(Y[i])])

    write_csv([header] + body + new_rows, opt_temp_name, home_folder)


# Design of experiments functions
# Sets up lists of data points to be evaluated

def factorial_design(ndims, nlevels):
    """
    Generates a full factorial design of experiments.
    
    Input ranges are normalized between -1.0 and 1.0.
    Returns a numpy array of shape (nlevels^ndims, ndims).
    """
    levels = np.linspace(-1.0, 1.0, nlevels)
    combinations = list(product(levels, repeat=ndims))
    return np.array(combinations, dtype=float)

def scale_array(array, bounds):
    """
    Scales the columns of a 1D or 2D array to the specified (min, max) bounds.
    
    Bounds should be an iterable of tuples: [(min1, max1), (min2, max2), ...].
    Returns the scaled data as a Python list.
    """
    arr = np.array(array, dtype=float)
    bounds = list(bounds)
    if arr.ndim == 1:
        src_min, src_max = np.min(arr), np.max(arr)
        span = (src_max - src_min) or 1.0
        t = (arr - src_min) / span
        low, high = bounds[0]
        return (t * (high - low) + low).tolist()

    src_mins = np.min(arr, axis=0)
    src_maxs = np.max(arr, axis=0)
    span = src_maxs - src_mins
    span[span == 0] = 1.0
    t = (arr - src_mins) / span
    out = np.empty_like(arr)
    for i, (low, high) in enumerate(bounds):
        out[:, i] = t[:, i] * (high - low) + low
    return out.tolist()

def normalize(array):
    """
    Convenience wrapper to scale a 3-variable array to the [-1, 1] range.
    """
    return scale_array(array, [[-1, 1]] * 3)


# Optimization function
# Uses a particle swarm optimizer to minimize a given function

def optimize(user_function, settings):
    """
    Minimizes a user-defined function using Global Best Particle Swarm Optimization.
    
    Settings dictionary must include:
    - 'dimensions': int
    - 'options': dict (c1, c2, w)
    - 'iters': int
    - 'n_particles': int
    - 'bounds': tuple (min_arr, max_arr)
    
    Returns a list containing the [optimal_position, optimal_cost].
    """
    dims = settings['dimensions']
    options = settings['options']
    iters = settings.get('iters', 100)
    n_particles = settings.get('n_particles', 10)
    bounds = settings.get('bounds', None)

    def pyswarms_compatible_func(x):
        return np.apply_along_axis(lambda p: user_function(p), 1, x)

    optimizer = ps.single.GlobalBestPSO(
        n_particles=n_particles,
        dimensions=dims,
        options=options,
        bounds=bounds
    )

    cost, pos = optimizer.optimize(pyswarms_compatible_func, iters=iters)
    return [pos, cost]


# Surrogate modeling functions 
# Uses a Gaussian radial basis function to create a quick compute surrogate across centers

def measure_distance(X1, X2):
    """Computes the L2 (Euclidean) norm between two points or vectors."""
    v1 = np.asarray(X1, dtype=float)
    v2 = np.asarray(X2, dtype=float)
    if v1.shape != v2.shape:
        raise ValueError("Point dimensions must match for distance calculation.")
    return np.linalg.norm(v1 - v2)

def gaussian(r, epsilon=1):
    """Computes the Gaussian Radial Basis Function value for a given radius r."""
    return np.exp(-(epsilon * r)**2)

def construct_tmat(xdata1, xdata2):
    """Constructs a pairwise distance matrix between two sets of points."""
    tmat = np.zeros((len(xdata1), len(xdata2)))
    for i in range(len(xdata1)):
        for j in range(len(xdata2)):
            tmat[i][j] = measure_distance(xdata1[i], xdata2[j])
    return tmat

def train_phimat(tmat, epsilon=1):
    """Applies the Gaussian kernel function to an existing distance matrix."""
    return gaussian(tmat, epsilon)

def _to_rows(Xb, ylen=None):
    """
    Internal helper to ensure X data is formatted as a list of sample rows.
    Heuristically detects row vs column orientation based on target length ylen.
    """
    arr = np.array(Xb, dtype=float)
    if arr.ndim == 1:
        return [arr.tolist()]
    if ylen is not None:
        if arr.shape[0] == ylen:
            return arr.tolist()
        if arr.shape[1] == ylen:
            return arr.T.tolist()
    return arr.tolist()

def train_weights(X_bucket, Y_bucket):
    """
    Calculates the weights (omegas) for a radial basis function surrogate model.
    
    Solves the linear system Phi * w = Y. 
    Requires that the number of points in X_bucket matches Y_bucket.
    """
    Y = np.array(Y_bucket, dtype=float)
    X_rows = _to_rows(X_bucket, ylen=len(Y))
    tmat = construct_tmat(X_rows, X_rows)
    Phi = train_phimat(tmat, epsilon=1)
    
    try:
        omegas = np.linalg.solve(Phi, Y)
    except np.linalg.LinAlgError:
        print("Matrix is singular. Regularization required (not implemented).")
        raise
    return omegas

def test_surrogate(test_point, X_bucket, omegas):
    """
    Predicts the value at a test point using a vector of trained weights.
    
    Interpolates between all known training points with Gaussian smoothness.
    """
    X_rows = _to_rows(X_bucket, ylen=len(omegas))
    tvec = construct_tmat([test_point], X_rows)
    phivec = train_phimat(tvec, epsilon=1)
    return np.dot(phivec, omegas)

print("\nOptimizer Module Loaded.")