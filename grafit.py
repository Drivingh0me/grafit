import numpy as np
import argparse
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import inspect
import openpyxl as xl
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import math

# class Function:
#     def __init__(self, func: str):
#         self.string = str(func)
#
#     def lambda(self) -> int:
#         return 1
#
#     # id is and optional arg
#     def format(self, id: int | None = None) -> self:
#         """ Formats the file to ba analyzed """
#         return self
#
#     # Can take either an int or str
#     def bounds(self, data: int | str):
#         return 0

# Make this a user input
usr_func = "a * np.exp(-b * x)"

# Restrict variables to prevent malicous function formation
class Function:
    def __init__(self, function: str, numvar: int):
        self.func = lambda x, a, b: eval(function)
        self.numvar = numvar

my_func = Function(usr_func, 3)

# parameters = ("a","b")
def dflt_func_exp(x, a, b):
    return a * np.exp(-b * x)

# parameters = ("a","b")
def dflt_func_dbl_exp(x, a, b):
    return a * (np.exp(-b * x) - np.exp(-c * x)) + d

# parameters = ("a","b")
def dflt_func_exp_s(x, a, b):
    return a * np.exp(-b * (x + c))

# parameters = ("a","b")
def dflt_func_dbl_exp_ind(x, a, b):
    return a * np.exp(-b * x) - c * np.exp(-d * x) + f

# parameters = ("a","b")
def dflt_func_poly(x, a, b):
    return a * x**4 + b * x**3 + c * x**2 + d * x + f

# Determine number of variables to optimize
def get_numVar(func):
    funcSignature = inspect.signature(func)
    funcParameters = funcSignature.parameters
    return len(funcParameters) - 1

# Fix bounds
def get_bounds(bounds, defaultBounds ,numVar):
    lowerBound = []
    upperBound = []
    for x in range(numVar):
        try:
            lowerBound.append(bounds[0][x])
        except:
            lowerBound.append(defaultBounds[0])
        try:
            upperBound.append(bounds[1][x])
        except:
            upperBound.append(defaultBounds[1])
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

    # Pull out the read as a separate function
    try:
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
                # Assume overflow is 6E6.
                # elems = [el for el in elems if el != "OVRFLW"]
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
    except:
        raise ValueError("File does not exist!")

    return dArr

def frmt_horiba(file):
    return 1

# if guard to determine value for frmtdData.
def get_frmtdData(dataFormat, dataFile):
    if dataFormat == 0: # Simple x column + y columns
        try:
            frmtdData = np.loadtxt(dataFile, delimiter='\t')
        except:
            raise ValueError("File does not exist!")

    elif dataFormat == 1: # .csv file
        raise ValueError("csv format not implemented")

    elif dataFormat == 2: # Plate reader .txt file
        frmtdData = frmt_pltreader(dataFile)

    elif dataFormat == 3: # Horiba .txt file
        raise ValueError("horiba.txt format not implemented")

    else:
        raise ValueError(f"Format value: {dataFormat} is out of range: 0-3")
    return frmtdData

# Fit the function to the data
def fit_data(
        data, xdata, func, optimizedPerameters,
        bounds, statistics, sett_plot
    ):
    n = 0
    for ydata in data:
        try:
            popt, pcov = curve_fit(
                func, 
                np.transpose(xdata), 
                ydata, bounds = bounds
            )
        except:
            popt = np.zeros(numVar)
            print(f"Failed to fit {n}th curve")

        # Trying to use pcov:
        # perr = np.sqrt(np.diag(pcov))
        # print(f"perr is: \n{perr}\n")

        optimizedPerameters[n] = popt

        ydata_try = np.tile(popt[:, np.newaxis], (1, len(xdata)))
        # Plot individual trials
        if sett_plot:
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
def export_txt(optimizedParameters, statistics, outfile):
    with open(outfile, "w") as f:
        # Report parameters and statistics
        f.write("Optimize parameters are: a, b, c...\n" 
            + arr2str(optimizedParameters) + "\n")
        f.write("Statistics are: R^2, RMSE, integration\n" 
            + arr2str(statistics))


def export_term(optimizedParameters, statistics):
    # Report parameters and statistics
    print("Optimize parameters are: a, b, c...\n" + str(optimizedParameters))
    print("Statistics are: R^2, RMSE, integration\n" + str(statistics))

def export_xlsx(optimizedParameters, statistics, fname):
    wb = xl.Workbook()
    ws = wb.active

    # Label coumns
    # ws.append(parameters)

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
def prnt_k(xk1, optimizedPerameters, kIndex):
    try:
        plt.figure()
        plt.plot(xk1, optimizedPerameters[:, kIndex], 'o', label='k values')
        #plt.ylim(0, 1.1 * max(optimizedPerameters[:, kIndex]))
        plt.legend()
    except:
        print("Failed to plot data!")


def main():
    dataFormat = 2
    # What is the index of the variable of interest?
    kIndex = 1;

    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="files to analyze", nargs='*')
    parser.add_argument("-p", "--plot", help="plot data", action="store_true")
    parser.add_argument(
        "-e", "--equation", help="function to fit to", nargs=1
    )
    parser.add_argument(
        "-d", "--debug", help="debug mode", action="store_true"
    )

    parser.add_argument(
        "-E", "--Excel", help="export xlsx", action="store_true"
    )

    parser.add_argument(
        "-T", "--Txt", help="export txt", action="store_true"
    )

    # This is inverted, intentionally. -f True means to NOT fit.
    parser.add_argument("-f", "--fit", help="fit data", action="store_true")
    args = parser.parse_args()
    if args.plot:
        sett_plot = True
        sett_plotK = True
        print("ploting data")
    else:
        sett_plot = False
        sett_plotk = False

    # Only do this when no file from cli
    if args.file == []:
        Tk().withdraw()
        dataFile = askopenfilename()
    else:
        # Cheaply grabs first filename
        dataFile = args.file[0]

    if args.debug:
        print(f"File:{dataFile}")

    # if agrgs.equation = "se" || "Ae^(-bx)"

    fname = dataFile.split(".")
    outfile = fname[0] + "Analysis.txt"

    # Make sure there is a file to analyze!\

    if not sett_plot:
        sett_plotK = False
        sett_plotCurv = False

    # Bounds for fitting curve
    # Array size should match number of variables to optimize
    usrBounds = ([0, 0], [10000000, 0.5])

    if args.debug:
        print(F"usrBounds:{usrBounds}")

    defaultBounds = [0, 10**12]

    # numVar = get_numVar(func)
    numVar = my_func.numvar - 1
    # Broken! Somehow the lowerbound is higher than the upper
    bounds = get_bounds(usrBounds, defaultBounds ,numVar)

    if args.debug:
        print(f"Bounds:{bounds}")

    frmtdData = get_frmtdData(dataFormat, dataFile)

    data = np.transpose(frmtdData)
    xdata = data[0]
    data = np.delete(data, 0, axis=0)
    optimizedParameters = np.empty((len(data),numVar))
    statistics = np.empty((len(data),3))

    if not args.fit:
        fit_data(
            data, xdata, my_func.func,
            optimizedParameters, bounds, statistics, sett_plot
        )

    # Statistical analysis
    avgRSquared = np.mean(statistics[:, 0])
    avgRmse = np.mean(statistics[:, 1])
    avgArea = np.mean(statistics[:, 2])
    #Depends on Func
    xk1 = list(range(len(optimizedParameters[:, kIndex])))

    if args.Txt:
        export_txt(optimizedParameters, statistics, outfile)

    if not(args.Txt or args.Excel):
        export_term(optimizedParameters, statistics)

    if args.Excel:
        # Add plot data in excel!
        export_xlsx(optimizedParameters, statistics, fname)

    if sett_plot:
        if sett_plotK:
            prnt_k(xk1, optimizedParameters, kIndex)
        plt.show()

    if args.debug:
        print("Finished")

if __name__ == "__main__":
    main()
