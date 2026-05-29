# # COMPARATOR 
# Customize for another error metric if desired, very flexible.
import optimize as opt

opt.log_str("Comparator - I'm awake and ready to compare!")

# import temp file
existingY = opt.read_data()['Ydata']
existingX = opt.read_data()['Xdata']

remaining = len(existingY)
completed = len(existingX[0])-remaining

# import a psd datapoint file

# Find the 60Hz peak
# calculate that minus 56Hz

measurederror = 1
best_idx = []
for i in range(remaining):
    modal_data = opt.read_csv("PSD DataPoint "+str(completed+i),opt.home_folder)
    modes = [row[0] for row in modal_data]  # Frequency
    freq_data = [row[1] for row in modal_data]  # Sensor 2
    best_err = 100
    for idx in range(1,len(freq_data)-1):
        err = (56-float(freq_data[idx]))**2
        if err<best_err:
            best_err = err
            best_freq = freq_data[idx]
    opt.post_Ydata([best_err])

# print(best_idx)
# error = (best_psd-56)^2
# opt.post_Ydata(error)