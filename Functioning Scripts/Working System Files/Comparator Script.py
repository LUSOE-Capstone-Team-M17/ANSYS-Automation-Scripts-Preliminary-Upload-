# # COMPARATOR 
# Customize for another error metric if desired, very flexible.
import optimize as opt

opt.log_str("Comparator - I'm awake and ready to compare!")

# import temp file
existingY = opt.read_data()['Ydata']
existingX = opt.read_data()['Xdata']
nonzeroY = []
for value in existingY:
    if value != 0:
        nonzeroY.append(value)

remaining = len(nonzeroY)
completed = len(existingX[1])-remaining

print(completed)
print(remaining)
print(range(completed,remaining))

measurederror = 1
best_idx = []
best_frequencies = []
for i in range(len(opt.read_data()['steps'])):
    modal_data = opt.read_csv("PSD DataPoint "+str(i),opt.home_folder)
    modes = [row[0] for row in modal_data]  # Frequency
    freq_data = [row[1] for row in modal_data]  # Sensor 2
    best_err = 1000
    for idx in range(1,len(freq_data)-1):
        err = (56-float(freq_data[idx]))**2
        if err<best_err:
            best_err = err
            best_freq = freq_data[idx]
    opt.post_Ydata([best_err])
    best_frequencies.append(best_freq)
    print("Data point "+str(i)+": best frequency = "+str(best_freq)+", with an error of "+str(best_err)+".")
opt.write_csv(best_frequencies,"Best Frequencies",opt.home_folder)
# i=completed+1
# modal_data = opt.read_csv("PSD DataPoint "+str(i-1),opt.home_folder)
# modes = [row[0] for row in modal_data]  # Frequency
# freq_data = [row[1] for row in modal_data]  # Sensor 2
# best_err = 1000
# for idx in range(1,len(freq_data)-1):
#     err = (56-float(freq_data[idx]))**2
#     if err<best_err:
#         best_err = err
#         best_freq = freq_data[idx]
# opt.post_Ydata([best_err])