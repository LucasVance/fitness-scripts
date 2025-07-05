# filename: tsb-finder.py

import math
import platform
import os

def get_float_input(prompt_text):
    """
    Gets a float input from the user. Returns None if the user enters nothing.
    """
    while True:
        try:
            val_str = input(f"{prompt_text}: ").strip()
            if not val_str:
                return None  # Return None for blank input
            return float(val_str)
        except ValueError:
            print("Invalid input. Please enter a numeric value or leave it blank.")

def _simulate_and_get_metrics(tsb_target, ctl_days, atl_days, start_ctl=60.0):
    """
    Internal helper to simulate a block and return key metrics.
    
    Returns:
        - avg_weekly_tss_total: The average total TSS per week in a stable period.
        - avg_ctl_ramp_rate: The average weekly change in CTL.
        - avg_weekly_tss_change: The average weekly change in total TSS.
    """
    ctl_current = start_ctl
    atl_current = ctl_current - tsb_target 
    
    c = ctl_days
    a = atl_days
    kc = (c - 1) / c
    ka = (a - 1) / a
    tsb_tss_multiplier = (1/c) - (1/a)

    weekly_tss_totals = []
    daily_ctl_history = [ctl_current]
    
    num_days_to_simulate = 12 * 7 
    current_week_tss = 0

    for day in range(1, num_days_to_simulate + 1):
        if abs(tsb_tss_multiplier) > 1e-9:
            numerator = tsb_target - (ctl_current * kc) + (atl_current * ka)
            tss_needed = numerator / tsb_tss_multiplier
        else:
            tss_needed = atl_current

        tss_needed = max(0, tss_needed)
        current_week_tss += tss_needed
        
        atl_current = (atl_current * ka) + (tss_needed * (1/a))
        ctl_current = (ctl_current * kc) + (tss_needed * (1/c))
        daily_ctl_history.append(ctl_current)

        if day % 7 == 0:
            weekly_tss_totals.append(current_week_tss)
            current_week_tss = 0
            
    # --- Define Stable Period for Analysis ---
    stable_period_start_week = 4
    stable_period_end_week = 11
    
    if len(daily_ctl_history) < stable_period_end_week * 7 or len(weekly_tss_totals) <= stable_period_start_week:
        return 0, 0, 0

    # --- Metric 1: Average Weekly CTL Ramp Rate ---
    ctl_ramp_rates = []
    for week_num in range(stable_period_start_week, stable_period_end_week + 1):
        ctl_end = daily_ctl_history[week_num * 7]
        ctl_start = daily_ctl_history[(week_num - 1) * 7]
        ctl_ramp_rates.append(ctl_end - ctl_start)
    avg_ctl_ramp_rate = sum(ctl_ramp_rates) / len(ctl_ramp_rates) if ctl_ramp_rates else 0
    
    # --- Metric 2: Average Total Weekly TSS ---
    stable_weekly_tss = weekly_tss_totals[stable_period_start_week-1:stable_period_end_week]
    avg_weekly_tss_total = sum(stable_weekly_tss) / len(stable_weekly_tss) if stable_weekly_tss else 0

    # --- Metric 3: Average Weekly TSS Change (The Fix) ---
    tss_change_rates = []
    for i in range(stable_period_start_week, stable_period_end_week):
        change = weekly_tss_totals[i] - weekly_tss_totals[i-1]
        tss_change_rates.append(change)
    avg_weekly_tss_change = sum(tss_change_rates) / len(tss_change_rates) if tss_change_rates else 0

    return avg_weekly_tss_total, avg_ctl_ramp_rate, avg_weekly_tss_change

def _find_tsb_for_metric(target_value, metric_to_target, ctl_days, atl_days):
    """
    Generic binary search function to find the TSB for a given target metric.
    """
    print(f"\nSearching for TSB value that produces a target {metric_to_target} of {target_value:.1f}...")
    
    upper_bound_tsb, lower_bound_tsb = 20.0, -100.0

    for i in range(15):
        mid_tsb = (upper_bound_tsb + lower_bound_tsb) / 2
        avg_tss_total, avg_ctl_ramp, avg_tss_change = _simulate_and_get_metrics(mid_tsb, ctl_days, atl_days)
        
        if metric_to_target == "CTL Ramp":
            measured_value = avg_ctl_ramp
        elif metric_to_target == "Weekly TSS Change":
            measured_value = avg_tss_change
        else: # Default to Total Weekly TSS
            measured_value = avg_tss_total

        if measured_value > target_value:
            lower_bound_tsb = mid_tsb
        else:
            upper_bound_tsb = mid_tsb
            
    return (upper_bound_tsb + lower_bound_tsb) / 2

def run_calibrator():
    """Runs one cycle of the calibration calculation."""
    print("\n--- Model Time Constants ---")
    ctl_period_input = int(input("Enter the CTL period in days (e.g., 40): "))
    atl_period_input = int(input("Enter the ATL period in days (e.g., 4): "))

    print("\n--- Enter ONE of the following metrics ---")
    print("Leave the other two blank and press Enter.")
    
    target_tsb = get_float_input("Constant TSB")
    target_ctl_ramp = get_float_input("Ramp Rate")
    target_tss_change = get_float_input("Weekly TSS Change")

    inputs = {
        "TSB": target_tsb,
        "CTL Ramp": target_ctl_ramp,
        "Weekly TSS Change": target_tss_change,
    }
    
    provided_values = {k: v for k, v in inputs.items() if v is not None}
    
    if len(provided_values) != 1:
        print("\nERROR: Please provide a value for exactly ONE of the three metrics.")
        return

    # --- Calculations ---
    final_tsb = 0
    input_metric_name, input_metric_value = list(provided_values.items())[0]

    if input_metric_name == "TSB":
        final_tsb = input_metric_value
    else:
        final_tsb = _find_tsb_for_metric(input_metric_value, input_metric_name, ctl_period_input, atl_period_input)
    
    final_weekly_tss_total, final_ctl_ramp, final_tss_change = _simulate_and_get_metrics(final_tsb, ctl_period_input, atl_period_input)
    
    print("\n--- Calibration Complete ---")
    print(f"For a {ctl_period_input}/{atl_period_input} day model, the following values are equivalent:")
    print("\n")
    print(f"Constant TSB:      {final_tsb:.2f}")
    print(f"Ramp rate:         {final_ctl_ramp:+.1f} CTL/wk")
    print(f"Weekly TSS change: {final_tss_change:+.1f} TSS/wk")

def main():
    """Main execution for the calibrator tool."""
    print("--- Training Model Calibrator ---")
    print("This tool translates between key progression metrics:")
    print("TSB, Ramp Rate, and Weekly TSS Change.")
    
    run_calibrator() # Runs the main calculation once

if __name__ == "__main__":
    main()