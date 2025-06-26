# Fitness Scripts

This repository contains a collection of Python scripts for analyzing and planning training load using the concepts of Chronic Training Load (CTL), Acute Training Load (ATL), and Training Stress Balance (TSB).

## Scripts

*   **`fitness.py`**: A command-line tool to project the number of days required to reach a target CTL based on initial CTL, ATL, and a desired TSB. It allows for customizable CTL and ATL time periods.
*   **`tsb-finder.py`**: A command-line tool to find the TSB value that corresponds to a desired weekly TSS ramp rate. This is useful for calibrating your training plan.
*   **`contribution_analyzer.py`**: A script to analyze the percentage contribution of each preceding day to an exponentially weighted moving average (EWMA), which is the model used for CTL and ATL calculations.

## Usage

Each script can be run from the command line:

```bash
python fitness.py
python tsb-finder.py
python contribution_analyzer.py
```

The scripts will prompt you for the necessary inputs.
