# grafit v0.1.3
A simple python script for fitting and plotting chemical kinetics data.
Some features also work well for other chemical data, such as plotting ESI_MS
data.

## How to install requirements with pip
Run the following command in the project directory (chlorine35):
    pip install -r requirements.txt

## How to run grafit
Run grafit by executing the grafit.py script with python3:
    python3 grafit.py `<file path>` `<flags>`

The `file path` argument is necessary.
If a `file path` is not given grafit will open up a gui to select a file.

### Flags 
(-short/--long) Desription, arg description. (number of arguments)
- `-d/--debug` Chooses a file to analyze.
- `-f/--fit` Fit data to function, function. (1)
- `-p/--plot` Plots the data.
- `-E/--Excel` Export to excel file.
- `-T/--Txt` Export to text file.
