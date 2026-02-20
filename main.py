import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import inspect
import openpyxl as xl

#----------------------------
# SETTINGS
#----------------------------

# PATH to data file. Can just write "fileName.txt" if local directory
dataFile = "test/example.txt"

# Define the function to fit
# Make universal usage of variables
# a=A, b=B, c=kobs
def func(x, a, b, c):
	return a * np.exp(-c * x) + b

# Eg. Worst case function
# a=A, b=B, c=k1, d=k2, f=ti
#a * (np.exp(-c * (x+f)) - np.exp(-d * (x+f))) + b

# Bounds for fitting curve
# Array size should match number of variables to optimize
bounds = ([0, 0, 0], [10000000, 1000000, 0.5])
# Default bounds
defaultLb = 0
defaultUb = 10**12

# Input data format
# 0= .txt where first column x, all other columns y
# Broken 1= .csv, alternating x y columns
# 2= .txt output from plate reader
# Broken 3= .txt output from Horiba
dataFormat = 0

# Print any plots?
sett_plot = False

# Print the k values vs column number?
# Broken, plots odd curves and fits too
sett_plotK = True

# Print the individual kinetic plots vs fit?
sett_plotCurv = False

# Export results to terminal?
sett_outTerm = True

# Export the results to a .txt file?
# Broken
sett_outTxt = False
outfile = "analysis.txt"

# Export the results to an excel file?
# Not implemented
#sett_outxlsx = False

# Create a plot in the axcel file?
# Not implementes
# sett_xlsxGraph = False

#----------------------------
#----------------------------

# SETT LOGIC
if not sett_plot:
	sett_plotK = False
	sett_plotCurv = False

# Determine number of variables to optimize
funcSignature = inspect.signature(func)
funcParameters = funcSignature.parameters
numVar = len(funcParameters) - 1
# Fix bounds
lowerBound = np.zeros(numVar)
upperBound = np.zeros(numVar)
for x in range(numVar):
	try:
		lowerBound[x] = bounds[0][x]
	except:
		lowerBound[x] = defaultLb
	try:
		upperBound[x] = bounds[1][x]
	except:
		upperBound[x] = defaultUb

sett_bounds = (lowerBound, upperBound)

# DO THE WORK
# Collect and format the data
def frmt_csv(file):
	return 1

def frmt_pltreader(file):
	# Ignore non-utf8 characters

	with open(file, 'r', encoding='utf-8', errors='ignore') as pfile:
		fileLns = pfile.readlines()
		for i in range(37, len(fileLns)):
			row = fileLns[i]
			elems = row.split('\t')
			try:
				elems.pop(1)
			except:
				break
			# Remove blank elements of elems.
			elems = [el for el in elems if el != '']
			elems = [el for el in elems if el != '\n']
			# Convert first column to seconds from HH:MM:SS.
			colTime = elems[0]
			oddTime = colTime.split(':')
			hours = int(oddTime[0])
			minutes = int(oddTime[1])
			seconds = int(oddTime[2])
			elems[0] = hours*3600+minutes*60+seconds
			# Convert elements of elems to int.
			elems = [int(item) for item in elems]
			# Add elements of elems to numpy array.
			if i == 37:
				dArr = np.array(elems)
			else:
				dArr = np.vstack([dArr, elems])
	return dArr

def frmt_horiba(file):
	return 1	

if dataFormat == 0:
	frmtdData = np.loadtxt(dataFile, delimiter='\t')

elif dataFormat == 1:
	print("Not implemented yet.")

elif dataFormat == 2:
	frmtdData = frmt_pltreader(dataFile)
	
elif dataFormat == 3:
	print("Not implemented yet.")

else:
	print("invalid data format")

# Load data into np array
data = np.transpose(frmtdData)
xdata = data[0]
data = np.delete(data, 0, axis=0)

# Create arrays of specific size
optimizedPerameters = np.empty((len(data),numVar))
statistics = np.empty((len(data),3))
n = 0

# Fit the function to the data
for ydata in data:
	try:
		popt, pcov = curve_fit(func, 
			np.transpose(xdata), ydata, bounds = sett_bounds)
	except:
		popt = np.zeros(numVar)
	optimizedPerameters[n] = popt
	# Plot individual trials
	if sett_plotCurv:
		try:
			plt.figure()
			plt.plot(xdata, func(xdata, *ydata_try), '-', label='fit')
			plt.plot(xdata, ydata, 'o', label='data')
		except:
			print("Failed to plot fit data")

	# Calculate integral by Riemann sum
	areaUnderCurve = np.sum(ydata)

	# Make popt the right shape and rename array
	ydata_try = np.tile(popt[:, np.newaxis], (1, len(xdata)))

	# Calculate R squared
	residuals = ydata - func(xdata, *ydata_try)
	ss_res = np.sum(residuals ** 2)
	ss_tot = np.sum((ydata - np.mean(ydata)) ** 2)
	r_squared = 1 - (ss_res / ss_tot)

	# Calculate root mean square error (RMSE)
	rmse = np.sqrt(np.mean(residuals ** 2))
	statistics[n] = (r_squared, rmse, areaUnderCurve)
	n += 1

# Statistical analysis
# avgA = np.mean(optimizedPerameters[:, 0])
# avgB = np.mean(optimizedPerameters[:, 1])
# avgk1 = np.mean(optimizedPerameters[:, 2])
avgRSquared = np.mean(statistics[:, 0])
avgRmse = np.mean(statistics[:, 1])
avgArea = np.mean(statistics[:, 2])

xk1 = list(range(len(optimizedPerameters[:, 2])))

# EXPORT DATA
def export_txt():
	with open(outfile, "w") as f:
		# f.write("Mean of A = " + str(avgA) + "\n")
		# f.write("Mean of B = " + str(avgB) + "\n")
		# f.write("Mean of k1 = " + str(avgk1) + "\n")
		f.write("Mean of R Squared = " + str(avgRSquared) + "\n")
		f.write("Mean of RMSE = " + str(avgRmse) + "\n")
		f.write("Mean of integrals = " + str(avgArea) + "\n")
		# Report parameters and statistics
		f.write("Optimize parameters are: a, b, c...\n" 
			+ str(optimizedPerameters) + "\n")
		f.write("Statistics are: R^2, RMSE, integration\n" 
			+ str(statistics))
	

def export_term():
	# print("Mean of A = " + str(avgA))
	# print("Mean of B = " + str(avgB))
	# print("Mean of k1 = " + str(avgk1))
	print("Mean of R Squared = " + str(avgRSquared))
	print("Mean of RMSE = " + str(avgRmse))
	print("Mean of integrals = " + str(avgArea))
	# Report parameters and statistics
	print("Optimize parameters are: a, b, c...\n" + str(optimizedPerameters))
	print("Statistics are: R^2, RMSE, integration\n" + str(statistics))

if sett_outTxt:
	export_txt()

if sett_outTerm:
	export_term()

# PLOT DATA
# Print k values
def prnt_k():
	try:
		plt.plot(xk1, optimizedPerameters[:, 2], 'o', label='k values')
		plt.ylim(0, 1.1 * max(optimizedParameters[:, 2]))
	except:
		print("Failed to plot data")

# Plot the fitted curve & data
def prnt_dataVsCurv():
	try:
		plt.plot(xdata, func(xdata, *ydata_try), '-', label='fit')
	except:
		print("Failed to plot fit data")


if sett_plot:
	if sett_plotK:
		prnt_k()
	if sett_plotCurv:
		prnt_dataVsCurv()
	plt.legend()
	plt.show()

print("Finished")
