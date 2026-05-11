# Fitness Scripts

A collection of Python scripts for analyzing and planning training load over time using the concepts of Chronic Training Load (CTL), Acute Training Load (ATL), and Training Stress Balance (TSB).

## Scripts

*   **`fitness.py`**: Projects the number of days required to reach a target CTL based on initial CTL, ATL, and a desired TSB. Customizable CTL and ATL time periods.
*   **`progression_calibrator.py`**: Translates between TSB, CTL ramp rate, and weekly TSS change for a given training model.
*   **`contribution_analyzer.py`**: Analyzes the percentage contribution of each day to an exponentially weighted moving average.
*   **`hrss.py`**: Calculates Heart Rate Stress Score (HRSS) for an activity using heart rate data (max, resting, threshold) and duration.