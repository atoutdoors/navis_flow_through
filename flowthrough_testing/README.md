# Flow-Through Visualization

This program reads flow-through Excel files and creates interactive plots for the sensor data.

The main file is:

```text
flowthrough_visualization_standalone.py
```

## 1. Check that Python is installed

Open **PowerShell** and type:

```powershell
python --version
```

Python 3.10 or newer is recommended. If PowerShell cannot find Python, install Python from [python.org](https://www.python.org/downloads/).

## 2. Install the required packages

In PowerShell, run:

```powershell
pip install pandas plotly openpyxl
```

These packages allow the program to read Excel files and create plots.

## 3. Check the input files

By default, the program looks for Excel files in:

```text
G:\Shared drives\WHOI Argo\BGC\Float Tracking\flow_through_results
```

The folder must be available on your computer, and the files must be named like this:

```text
1558_calcs_.xlsx
1557_calcs_.xlsx
1559_calcs_.xlsx
```

The sensor number in the filename must match one of the sensor numbers listed in the Python script.

Each Excel file should contain a `DATE` column, a `PRES` column, and the sensor-data columns being plotted, such as:

```text
PSAL, PH_TOTAL, TEMP, PRES, DOXY, MCOMS1, MCOMS2, MCOMS3, NITRATE
```

Nitrate is optional. Files without usable nitrate data are skipped only for nitrate plots.

## 4. Choose whether to save plots

Open `flowthrough_visualization_standalone.py` in a text editor such as VS Code or Notepad++.

Near the beginning of the file, find:

```python
SAVE_HTML = False
```

Choose one setting:

```python
SAVE_HTML = False
```

This opens the plots in your web browser using temporary files. It does not save the plots in the output folder.

Or:

```python
SAVE_HTML = True
```

This saves the plots as interactive HTML files.

Saved plots are placed in:

```text
Z:\www\bgc\flow_through
```

## 5. Run the program

In PowerShell, move to the project folder:

```powershell
cd "C:\Users\athay\Documents\Repositories\bgc-testing\flowthrough_testing"
```

Then run:

```powershell
python flowthrough_visualization_standalone.py
```

The program will print progress messages, such as:

```text
Plot mode: DISPLAY ONLY (temporary browser files)
[1/3] Preparing cached sensor data...
[2/3] Creating all-float raw plots...
[3/3] Creating date-based grouped plots...
Finished generating original plots.
```

## 6. What the plots show

The program creates:

- Plots containing all selected sensors.
- Raw sensor-value plots.
- Median-corrected plots from the original workflow.
- Grouped plots comparing related sensors.

If `SAVE_HTML = True`, open an HTML file in a web browser to interact with the plot. You can zoom, pan, hide sensors by clicking the legend, and save an image from the plot menu.

## Common problems

### No plots appear

Confirm that:

1. You set `SAVE_HTML = False`.
2. You ran the correct script file.
3. A web browser is installed and set as the default browser.

### A file cannot be found

Check that the `G:` drive is connected and that the Excel filename follows the required format.

### A parameter is missing

The script skips missing nitrate data. Other missing columns may require adding the column to the Excel file or removing that parameter from the parameter list in the script.

### The program stops with an error

Keep the PowerShell window open and copy the complete error message. It usually identifies the specific file, sensor, or column causing the problem.
