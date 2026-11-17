"""Generate flow-through visualization HTML files from *_calcs_.xlsx files.

Example:
    python flowthrough_visualization_standalone.py

The original project paths are used automatically.
"""

from __future__ import annotations

import argparse
import os
import tempfile
import webbrowser
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


# ---------------------------------------------------------------------------
# SECTION 1: Configuration
# ---------------------------------------------------------------------------
# These are the same locations used by the original notebook and
# flowthrough_analysis.py.
DEFAULT_RESULTS_DIR = Path(
    r"G:/Shared drives/WHOI Argo/BGC/Float Tracking/flow_through_results"
)
DEFAULT_OUTPUT_DIR = Path(r"Z:/www/bgc/flow_through")

# Single output toggle: True saves HTML files; False opens plots in a browser.
SAVE_HTML = False

# Float serial numbers included in the all-float plots.
SERIAL_NUMBERS = [
    "1558", "1557", "1559", "1554", "1540", "1541", "1483", "1358",
    "1528", "1529", "1530", "1539", "1560", "1561", "1562", "1556",
    "1542", "1531", "1565", "1566", "1583", "1633", "1634", "1635",
    "1533", "1567", "1568", "1569", "1573", "1574", "1481", "1577",
    "1581", "1636", "1637", "1638", "1639", "1564", "1640", "1641",
    "1642", "1643", "1481", "1661", "1652", "1555", "1662", "1663",
    "1563", "1580", "1664", "1659", "1664", "1669", "1673", "1665",
    "1757", "1759", "1760", "2002", "2003", "2001", "2004", "1668",
    "1541", "2007", "2008", "2005", "2009", "2010", "2011", "2012",
    "1554", "1754", "1658", "2014", "2015", "2016", "2018", "1660",
    "1755", "1758",
]

# Parameters for plots that include a median-corrected series.
MEDIAN_PARAMETERS = [
    "PSAL", "PH_TOTAL", "TEMP", "PRES", "DOXY", "MCOMS1", "MCOMS2",
    "MCOMS3", "NITRATE",
]
# Parameters for plots that show the original measured values.
RAW_PARAMETERS = ["PSAL", "PH_TOTAL", "TEMP", "DOXY", "NITRATE", "PRES"]

# Sensor groups used for side-by-side comparison plots.
GROUPS = [
    [1558, 1557, 1559, 1554, 1540, 1541],
    [1483, 1358, 1528, 1529, 1530, 1539],
    [1560, 1561, 1562, 1556], [1542, 1531],
    [1565, 1566, 1583, 1633, 1634, 1635],
    [1533, 1567, 1568, 1569, 1573, 1574],
    [1636, 1637, 1638, 1481, 1581, 1577],
    [1639, 1564, 1640, 1641, 1642, 1643],
    [1563, 1662, 1663], [1555, 1661, 1652], [1664, 1580, 1659],
    [1664, 1669, 1673], [1757, 1759, 1665], [1760, 2002, 2003],
    [2001, 2004], [1668, 1541], [2007, 2008, 2005],
    [2009, 2010, 2011, 2012], [1554, 1754, 1658],
    [2014, 2015, 2016, 2018], [1758, 1660, 1755],
]

# Human-readable axis labels used by Plotly.
LABELS = {
    "PSAL": "Salinity (psu)", "PSAL-Median": "Salinity - Median (psu)",
    "PH_TOTAL": "PH (total)", "PH_TOTAL-Median": "PH (total) - Median",
    "TEMP": "Temperature (C)", "TEMP-Median": "Temperature (C) - Median",
    "PRES": "Pressure (dbar)", "PRES-Median": "Pressure (dbar) - Median",
    "DOXY": "Dissolved Oxygen (umol/kg)",
    "DOXY-Median": "Dissolved Oxygen (umol/kg) - Median",
    "MCOMS1": "FDOM (ppb)", "MCOMS1-Median": "FDOM (ppb) - Median",
    "MCOMS2": "Chlorophyll a (mg/m^3)",
    "MCOMS2-Median": "Chlorophyll a (mg/m^3) - Median",
    "MCOMS3": "Backscattering at 700nm (m^-1)",
    "MCOMS3-Median": "Backscattering at 700nm (m^-1) - Median",
    "NITRATE": "Nitrate (uM)", "NITRATE-Median": "Nitrate (uM) - Median",
}


def load_analysis(sensor: str, parameter: str, results_dir: Path) -> pd.DataFrame:
    # SECTION 2: Load and prepare one sensor/parameter dataset
    """Load one float's Excel result and calculate derived plot columns.

    Each input workbook is expected to be named ``<sensor>_calcs_.xlsx``.
    The returned DataFrame contains the original parameter, its offset from
    the sensor's median, and elapsed time measured from the first timestamp.
    """
    path = results_dir / f"{sensor}_calcs_.xlsx"
    if not path.exists():
        raise FileNotFoundError(f"Missing input file: {path}")

    # Read one sensor's processed flow-through data from Excel.
    data = pd.read_excel(path)
    if data.empty:
        raise ValueError(f"Input file has no rows: {path}")

    required_columns = {"DATE", "PRES", parameter}
    missing_columns = required_columns.difference(data.columns)
    if missing_columns:
        raise ValueError(
            f"{path.name} is missing columns {sorted(missing_columns)} "
            f"while processing sensor {sensor}, parameter {parameter}"
        )

    data["DATE"] = pd.to_datetime(data["DATE"], errors="coerce")
    data[parameter] = pd.to_numeric(data[parameter], errors="coerce")
    data["PRES"] = pd.to_numeric(data["PRES"], errors="coerce")
    data = data.dropna(subset=["DATE", parameter]).reset_index(drop=True)
    if data.empty:
        raise ValueError(
            f"No valid DATE/{parameter} values in {path.name} "
            f"for sensor {sensor}"
        )

    values = data[parameter]
    median_value = values.median()
    if pd.isna(median_value):
        raise ValueError(
            f"All {parameter} values are empty/NaN in {path.name} "
            f"for sensor {sensor}"
        )

    start = data["DATE"].iloc[0]

    # Build a smaller DataFrame containing only the columns needed by plots.
    result = pd.DataFrame({
        parameter: values,
        f"{parameter}-Median": values - median_value,
        "Float Number": f"{sensor}, Test Start: {start}",
        "SN": sensor,
        "DATE": data["DATE"],
        "PRES": data["PRES"],
    })
    # Align every sensor to its own test start so sensors can be compared
    # even when their tests occurred on different dates.
    result["Time Since Test Start (hours)"] = (
        data["DATE"] - start
    ).dt.total_seconds() / 3600
    return result


def generate_plots(
    results_dir: Path,
    output_dir: Path,
    display_only: bool = not SAVE_HTML,
) -> None:
    # SECTION 3: Generate visualizations
    """Create all-float, grouped, and sensor-comparison visualizations."""
    print(
        f"Plot mode: {'DISPLAY ONLY (temporary browser files)' if display_only else 'SAVE HTML FILES'}"
    )
    if not display_only:
        output_dir.mkdir(parents=True, exist_ok=True)

    # Cache each sensor/parameter pair. The grouped and comparison plots reuse
    # these DataFrames instead of reading the same Excel file repeatedly.
    cache: dict[tuple[str, str], pd.DataFrame] = {}

    def finish_plot(fig: go.Figure, path: Path) -> None:
        # In display-only mode Plotly opens the figure in the system browser
        # without writing HTML files to the configured output directory.
        if display_only:
            # Use an explicit temporary HTML file because the Plotly browser
            # renderer can fail silently when the script is launched from an
            # IDE or terminal without a configured renderer.
            temporary_file = tempfile.NamedTemporaryFile(
                suffix=".html",
                prefix="flowthrough_plot_",
                delete=False,
            )
            temporary_file.close()
            fig.write_html(temporary_file.name, auto_open=False)
            temporary_path = Path(temporary_file.name).resolve()
            if os.name == "nt":
                # Windows' shell association is more reliable than the
                # webbrowser module when launched from an IDE.
                try:
                    os.startfile(str(temporary_path))
                    opened = True
                except OSError:
                    opened = webbrowser.open_new_tab(temporary_path.as_uri())
            else:
                opened = webbrowser.open_new_tab(temporary_path.as_uri())
            print(f"Displayed plot: {temporary_file.name} (browser opened: {opened})")
        else:
            fig.write_html(path)

    def get_analysis(sensor: str, parameter: str) -> pd.DataFrame | None:
        key = (str(sensor), parameter)
        if key not in cache:
            try:
                cache[key] = load_analysis(*key, results_dir)
            except (FileNotFoundError, ValueError) as error:
                # Nitrate is optional because many workbooks do not contain
                # it. Other parameters still raise errors so missing data is
                # not silently hidden.
                if parameter != "NITRATE":
                    raise
                print(f"[skip nitrate] {error}")
                cache[key] = None
        return cache[key]

    print("[1/3] Preparing cached sensor data...")

    # Create one plot containing all selected floats for each parameter,
    # using the median-corrected value on the y-axis.
    for parameter in MEDIAN_PARAMETERS:
        frames = [
            frame for sensor in SERIAL_NUMBERS
            if (frame := get_analysis(sensor, parameter)) is not None
        ]
        if not frames:
            print(f"[skip plot] No usable {parameter} data was found.")
            continue
        frame = pd.concat(frames, ignore_index=True)
        fig = px.scatter(
            frame, x="Time Since Test Start (hours)",
            y=f"{parameter}-Median", color="Float Number",
            labels=LABELS, title=f"{parameter} time series (median corrected)",
        )
        finish_plot(fig, output_dir / f"{parameter}_median.html")

    print("[2/3] Creating all-float raw plots...")

    # Create one plot containing all selected floats using raw values.
    for parameter in RAW_PARAMETERS:
        frames = [
            frame for sensor in SERIAL_NUMBERS
            if (frame := get_analysis(sensor, parameter)) is not None
        ]
        if not frames:
            print(f"[skip plot] No usable {parameter} data was found.")
            continue
        frame = pd.concat(frames, ignore_index=True)
        fig = px.scatter(
            frame, x="Time Since Test Start (hours)", y=parameter,
            color="Float Number", labels=LABELS,
            title=f"{parameter} time series",
        )
        finish_plot(fig, output_dir / f"{parameter}.html")

    print("[3/3] Creating date-based grouped plots...")

    # Create the original date-based grouped plots. These preserve the
    # calendar-date view from the original notebook.
    for group in GROUPS:
        for parameter in MEDIAN_PARAMETERS:
            fig = go.Figure()
            first_date = None
            for sensor in map(str, group):
                frame = get_analysis(sensor, parameter)
                if frame is None:
                    continue
                first_date = first_date or frame["DATE"].iloc[0]
                fig.add_trace(go.Scatter(
                    x=frame["DATE"], y=frame[parameter],
                    mode="markers", name=sensor,
                ))

            if not fig.data:
                print(
                    f"[skip grouped plot] No usable {parameter} data in "
                    f"this sensor group."
                )
                continue

            fig.update_layout(title=f"{parameter}_{first_date}")
            date_label = pd.Timestamp(first_date).strftime("%Y-%m-%d")
            group_dir = output_dir / parameter
            if not display_only:
                group_dir.mkdir(parents=True, exist_ok=True)
            finish_plot(fig, group_dir / f"{date_label}.html")

    print("Finished generating original plots.")


def parse_args() -> argparse.Namespace:
    # SECTION 4: Command-line interface
    """Read optional input/output location overrides."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--results-dir",
        type=Path,
        default=DEFAULT_RESULTS_DIR,
        help=f"Input folder (default: {DEFAULT_RESULTS_DIR})",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Output folder (default: {DEFAULT_OUTPUT_DIR})",
    )
    return parser.parse_args()


if __name__ == "__main__":
    # This block makes the file executable from a terminal while still
    # allowing its functions to be imported by another Python program.
    args = parse_args()
    generate_plots(
        args.results_dir,
        args.output_dir,
        display_only=not SAVE_HTML,
    )
