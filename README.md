# grafit v0.1.3
A simple python script for fitting and plotting chemical kinetics data.
Some features also work well for other chemical data, such as plotting ESI_MS
data.

## How to install requirements with pip
Run the following in the project directory:
```
pip install -r requirements.txt
```

## How to run grafit
Run grafit by executing the grafit.py script with python3:
`python3 grafit.py <file path> <flags>`

The __file path__ argument is necessary.
If __a file path__ is not given, grafit will open up a gui to select a file.

### Flags 
__-short/--long__ Desription, arg description. (number of arguments)
- __-d/--debug__ Chooses a file to analyze.
- __-f/--fit__ Fit data to function, function. (1)
- __-p/--plot__ Plots the data.
- __-E/--Excel__ Export to excel file.
- __-T/--Txt__ Export to text file.
