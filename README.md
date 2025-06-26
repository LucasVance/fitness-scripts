# Fitness Scripts

A collection of Python scripts for analyzing and planning training load over time using the concepts of Chronic Training Load (CTL), Acute Training Load (ATL), and Training Stress Balance (TSB).

## Scripts

*   **`fitness.py`**: Projects the number of days required to reach a target CTL based on initial CTL, ATL, and a desired TSB. Customizable CTL and ATL time periods.
*   **`tsb-finder.py`**: Finds the TSB value that corresponds to a desired weekly TSS ramp rate. This is useful for choosing ideal fatigue ratios when changing fitness constants (moving off the 7/42 day ATL/CTL model)
*   **`contribution_analyzer.py`**: Analyzes the percentage contribution of each day to an exponentially weighted moving average (EWMA), which is the model used for CTL and ATL calculations.