import numpy as np
import argparse
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import inspect
import openpyxl as xl
from tkinter import Tk
from tkinter.filedialog import askopenfilename

#----------------------------
# SETTINGS
#----------------------------

# PATH to data file. Can just write "fileName.txt" if local directory
dataFile = "data/example.txt"

# Do you want to fit the data?
sett_fit = True

# Define the function to fit
# Make universal usage of variables
# a=A, b=B, c=kobs
parameters = ("a","b")
def func(x, a, b):
	return a * np.exp(-b * x)

# Eg. Worst case function
# a=A, b=B, c=k1, d=k2, f=ti
#a * (np.exp(-c * (x+f)) - np.exp(-d * (x+f))) + b

# Input data format
# 0= .txt where first column x, all other columns y
# Broken 1= .csv, alternating x y columns
# 2= .txt output from plate reader
# Broken 3= .txt output from Horiba
dataFormat = 2

# Print any plots?
sett_plot = True

# Print a value vs column number?
sett_plotK = True
# What is the index of the variable?
kIndex = 1;

# Print the individual kinetic plots vs fit?
sett_plotCurv = True

# Export results to terminal?
sett_outTerm = False

# Export the results to a .txt file?
# Broken
sett_outTxt = False
fname = dataFile.split(".")
outfile = fname[0] + "Analysis.txt"

# Export the results to an excel file?
# Not implemented
sett_outxlsx = True

# Create a plot in the excel file?
# Not implementes
# sett_xlsxGraph = False

#----------------------------
#----------------------------

# Determine number of variables to optimize
def get_numVar(func):
	funcSignature = inspect.signature(func)
	funcParameters = funcSignature.parameters
	return len(funcParameters) - 1

# Fix bounds
def get_bounds(bounds, defaultBounds ,numVar):
	lowerBound = np.zeros(numVar)
	upperBound = np.zeros(numVar)
	for x in range(numVar):
		try:
			lowerBound[x] = bounds[0][x]
		except:
			lowerBound[x] = defaultBounds[0]
		try:
			upperBound[x] = bounds[1][x]
		except:
			upperBound[x] = defaultBounds[1]
		return (lowerBound, upperBound)

# Convert an np array to a tab separated string
def arr2str(arr):
	return np.array2string(arr, separator='\t', precision=5)

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

# if guard to determine value for frmtdData.
def get_frmtdData(dataFormat, dataFile):
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
	return frmtdData

# Fit the function to the data
def fit_data(data, xdata, func, optimizedPerameters, bounds, statistics):
	n = 0
	for ydata in data:
		try:
			popt, pcov = curve_fit(func, 
				np.transpose(xdata), ydata, bounds = sett_bounds)
		except:
			popt = np.zeros(numVar)
		optimizedPerameters[n] = popt

		ydata_try = np.tile(popt[:, np.newaxis], (1, len(xdata)))
		# Plot individual trials
		if sett_plotCurv:
			try:
				plt.figure()
				plt.plot(xdata, func(xdata, *ydata_try), '-', label='fit')
				plt.plot(xdata, ydata, 'o', label='data')
				plt.legend()
			except:
				print("Failed to plot fit data")

		# Calculate integral by Riemann sum
		areaUnderCurve = np.sum(ydata)

		# Calculate R squared
		residuals = ydata - func(xdata, *ydata_try)
		ss_res = np.sum(residuals ** 2)
		ss_tot = np.sum((ydata - np.mean(ydata)) ** 2)
		r_squared = 1 - (ss_res / ss_tot)

		# Calculate root mean square error (RMSE)
		rmse = np.sqrt(np.mean(residuals ** 2))
		statistics[n] = (r_squared, rmse, areaUnderCurve)
		n += 1

# EXPORT DATA
def export_txt(optimizedParameters, statistics):
	with open(outfile, "w") as f:
		# f.write("Mean of R Squared = " + str(avgRSquared) + "\n")
		# f.write("Mean of RMSE = " + str(avgRmse) + "\n")
		# f.write("Mean of integrals = " + str(avgArea) + "\n")
		# Report parameters and statistics
		f.write("Optimize parameters are: a, b, c...\n" 
			+ arr2str(optimizedPerameters) + "\n")
		f.write("Statistics are: R^2, RMSE, integration\n" 
			+ arr2str(statistics))
	

def export_term(optimizedParameters, statistics):
	# print("Mean of R Squared = " + str(avgRSquared))
	# print("Mean of RMSE = " + str(avgRmse))
	# print("Mean of integrals = " + str(avgArea))
	# Report parameters and statistics
	print("Optimize parameters are: a, b, c...\n" + str(optimizedPerameters))
	print("Statistics are: R^2, RMSE, integration\n" + str(statistics))

def export_xlsx(optimizedParameters, statistics):
	wb = xl.Workbook()
	ws = wb.active

	# Label coumns
	ws.append(parameters)

	for row in optimizedParameters:
		ws.append(row.tolist())

	statNames = ("R^2","RMSE","Integral")
	ws.append(statNames)
	for row in statistics:
		ws.append(row.tolist())

	# Save the file
	wb.save(fname[0] + "AnalysisNoBg.xlsx")

# PLOT DATA
# Print k values
def prnt_k():
	try:
		plt.figure()
		plt.plot(xk1, optimizedPerameters[:, kIndex], 'o', label='k values')
		#plt.ylim(0, 1.1 * max(optimizedPerameters[:, kIndex]))
		plt.legend()
	except:
		print("Failed to plot data!")


def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("file", help="files to analyze", nargs='*')
	parser.add_argument("-p", "--plot", help="plot data", action="store_true")
	args = parser.parse_args()
	print(f"File is: {args.file}");
	if args.plot:
		print("ploting data")

	# Only do this when no file from cli
	# if args.file == []:
		# Tk().withdraw()
		# filePath = askopenfilename()

	# if filePath:
	# 	print(f"File path: {filePath}")
	# else:
	# 	print("No file selected")
	# END OF ARG PASRSE -------------------------------------------

	# SETT LOGIC
	if not sett_plot:
		sett_plotK = False
		sett_plotCurv = False

	# Bounds for fitting curve
	# Array size should match number of variables to optimize
	usrBounds = ([0, 0], [10000000, 0.5])
	defaultBounds = [0, 10**12]

	numVar = get_numVar(func)
	bounds = get_bounds(usrBounds, defaultBounds ,numVar)

	frmtdData = get_frmtdData(dataFormat, dataFile)

	data = np.transpose(frmtdData)
	xdata = data[0]
	data = np.delete(data, 0, axis=0)
	optimizedParameters = np.empty((len(data),numVar))
	statistics = np.empty((len(data),3))

	# Statistical analysis
	avgRSquared = np.mean(statistics[:, 0])
	avgRmse = np.mean(statistics[:, 1])
	avgArea = np.mean(statistics[:, 2])
	#Depends on Func
	xk1 = list(range(len(optimizedParameters[:, kIndex])))

	if sett_outTxt:
		export_txt(optimizedParameters, statistics)

	if sett_outTerm:
		export_term(optimizedParameters, statistics)

	if sett_outxlsx:
		export_xlsx(optimizedParameters, statistics)
	
	if sett_plot:
		if sett_plotK:
			prnt_k()
		plt.show()
	
	print("Finished")

if __name__ == "__main__":
	main()
