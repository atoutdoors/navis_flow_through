# Flow-through testing

This folder contains the scripts used to collect Navis flow-through data, inspect the resulting files, and generate interactive sensor plots.

## Workflow

Run the processing steps in this order:

1. Connect the float and collect samples with the appropriate collector.
2. Run the `split_results` notebook after data collection is complete to split and organize the collected data by float or test.
3. Run `flowthrough_analysis.py` to analyze the split data and create the processed results used by the visualization step.
4. Run `flowthrough_visualization_standalone.py` to generate comparison plots from those processed results.

The collector saves raw data as pickle files. The analysis step creates processed Excel workbooks named `<serial>_calcs_.xlsx` in the shared `flow_through_results` directory. These workbooks are the inputs to the visualization script.

## Install Python packages

Use Python 3.10 or newer. From PowerShell, install the packages used by the scripts:

```powershell
python -m pip install pandas numpy openpyxl plotly pyserial regex
```

Run all commands from this folder:

```powershell
cd "C:\Users\athay\Documents\navis_flow_through\flowthrough_testing"
```

## Collect flow-through data

### Hardware setup

- Connect the float to the computer over its serial interface.
- Confirm the COM-port number in Windows Device Manager.
- Make sure the shared `G:` drive is connected, or change `save_directory` in the script to a local folder that already exists.

### Configure the collector

Choose the collector that matches the float:

- `flow_through.py` is for NavisV1 floats.
- `flow_through2.py` is for NavisV2 floats and includes the additional NavisV2 sensor columns.

Open the selected script and check these settings near the top:

```python
run_until = "2027-01-01 00:00"  # YYYY-MM-DD HH:MM
save_directory = "G://Shared drives//WHOI Argo//BGC//Float Tracking//flow_through_data"
```

Set `run_until` to the date and time when sampling should stop. The collector writes files such as:

```text
F1558_20261117.pkl
```

The serial number is obtained from the float, so the filename is generated automatically.

### Start a run

From PowerShell:

```powershell
python flow_through.py
```

When prompted, enter the numeric COM-port suffix. For example, for `COM7`, enter:

```text
7
```

The script wakes the float, requests the sensor and pH samples, appends each sample to a DataFrame, and periodically saves the DataFrame as a pickle file. Leave the PowerShell window open while the test is running. Stop safely with `Ctrl+C` only when the collector is not in the middle of a serial transaction.

### Other collectors

- `SBE83test.py` and `SBE83testV1.py` collect SBE83 test data and save Excel files.
- The files with `(1)` or `copy` in their names are older variants; use them only when reproducing an earlier test.

## Split and analyze collected data

After the flow-through collection has finished, open and run the appropriate `split_results` notebook:

- `split_results.ipynb`
- `split_results (1).ipynb` if reproducing the alternate version of that workflow

The split-results step organizes the collected data so that each float or test can be processed separately. Run this step before running the analysis code.

Next, run `flowthrough_analysis.py` or the related analysis notebook. The analysis step calculates the sensor results, including median-corrected values and elapsed time, and writes or updates the processed `<serial>_calcs_.xlsx` workbooks in:

```text
G:\Shared drives\WHOI Argo\BGC\Float Tracking\flow_through_results
```

Only after these workbooks have been created should you run `flowthrough_visualization_standalone.py`.

## Processed data format

The plotting scripts read one processed workbook per sensor from:

```text
G:\Shared drives\WHOI Argo\BGC\Float Tracking\flow_through_results
```

Each workbook must be named:

```text
<serial>_calcs_.xlsx
```

For example:

```text
1558_calcs_.xlsx
```

The workbook should contain at least:

```text
DATE, PRES, PSAL, PH_TOTAL, TEMP, DOXY, MCOMS1, MCOMS2, MCOMS3
```

`NITRATE` is optional. `DATE` must contain timestamps, and the plotted sensor columns must contain numeric values. The visualization script skips nitrate plots when nitrate is not present, but it reports missing required columns for the other parameters.

## Analyze one sensor

`flowthrough_analysis.py` provides two functions for inspecting the processed results:

- `diff_analysis(SN, param)` reads `<SN>_calcs_.xlsx`, calculates the parameter's offset from its median, and adds elapsed time since the test started.
- `split_ftest(lastdate, SNs)` reads a workbook and returns one DataFrame per requested serial number.

For example, from Python or a notebook:

```python
from flowthrough_analysis import diff_analysis

temperature = diff_analysis("1558", "TEMP")
print(temperature.head())
temperature.to_csv("1558_TEMP_analysis.csv", index=False)
```

The returned table includes the raw parameter, `<parameter>-Median`, pressure, date, serial number, and elapsed time in hours and seconds.

## Generate interactive plots

The recommended entry point is `flowthrough_visualization_standalone.py`.

By default, it reads from `G:/Shared drives/WHOI Argo/BGC/Float Tracking/flow_through_results` and opens temporary HTML plots in the browser:

```powershell
python flowthrough_visualization_standalone.py
```

To use different folders, provide command-line overrides:

```powershell
python flowthrough_visualization_standalone.py `
  --results-dir "C:\path\to\flow_through_results" `
  --output-dir "C:\path\to\flow_through_plots"
```

To save plots instead of opening temporary browser files, edit:

```python
SAVE_HTML = True
```

Saved plots go to `Z:/www/bgc/flow_through` by default, or to the folder supplied with `--output-dir`. The script creates:

- raw all-sensor plots for salinity, pH, temperature, oxygen, nitrate, and pressure;
- median-corrected plots for the configured parameters; and
- date-based grouped plots for the sensor groups in the script.

In a Plotly plot, click legend entries to hide or show sensors, and use the toolbar to zoom, pan, or export an image.

## Troubleshooting

- **Cannot open the COM port:** confirm the port number, close other serial-monitor programs, and check that the float is connected.
- **Save directory does not exist:** connect the `G:` drive or change `save_directory` to an existing directory.
- **No input workbook found:** confirm the filename is exactly `<serial>_calcs_.xlsx` and that the `G:` drive is available.
- **Missing parameter:** check the workbook column names against the required columns above. Nitrate is the only optional plotted parameter.
- **No browser plot appears:** set `SAVE_HTML = True` and provide a local `--output-dir`, then open the generated `.html` files manually.
- **Serial read errors:** keep the full traceback and terminal output; it identifies whether the problem occurred while waking the float, requesting a sample, or parsing a response.
