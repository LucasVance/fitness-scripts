# filename: tsb_calibrator.py

import math

def _simulate_and_get_ramp_rate(tsb_target, ctl_days, atl_days, start_ctl=60.0):
    """
    Internal helper to simulate a training block and measure the weekly TSS ramp rate.
    Returns the average increase in weekly TSS during a stable period.
    """
    ctl_current = start_ctl
    atl_current = ctl_current - tsb_target 
    
    c = ctl_days
    a = atl_days
    kc = (c - 1) / c
    ka = (a - 1) / a
    tsb_tss_multiplier = (1/c) - (1/a)

    weekly_tss_totals = []
    
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

        if day % 7 == 0:
            weekly_tss_totals.append(current_week_tss)
            current_week_tss = 0
            
    stable_period_start_week = 4
    stable_period_end_week = 11
    
    if len(weekly_tss_totals) <= stable_period_start_week:
        return 0

    ramp_rates = []
    for i in range(stable_period_start_week, stable_period_end_week):
        ramp_rate = weekly_tss_totals[i] - weekly_tss_totals[i-1]
        ramp_rates.append(ramp_rate)

    avg_ramp_rate = sum(ramp_rates) / len(ramp_rates) if ramp_rates else 0
    return avg_ramp_rate

def find_tsb_for_ramp_rate(target_ramp_rate, ctl_days, atl_days):
    """
    Uses a binary search to find the TSB value that produces the target weekly TSS ramp rate.
    """
    print(f"\nSearching for TSB value for a {target_ramp_rate:.1f} TSS/wk ramp with {ctl_days}/{atl_days} constants...")
    
    # Using clearer variable names for the search boundaries
    upper_bound_tsb = 20.0   # The highest, least aggressive TSB
    lower_bound_tsb = -100.0 # The lowest, most aggressive TSB

    for i in range(15):
        mid_tsb = (upper_bound_tsb + lower_bound_tsb) / 2
        
        measured_ramp_rate = _simulate_and_get_ramp_rate(mid_tsb, ctl_days, atl_days)
        
        print(f"  -> Test TSB: {mid_tsb:6.2f} -> Ramp Rate: {measured_ramp_rate:5.1f} TSS/wk", end="")
        
        # --- THIS IS THE DEFINITIVELY CORRECTED LOGIC ---
        if measured_ramp_rate > target_ramp_rate:
            # Measured ramp is too high, so the test TSB is too aggressive (too negative).
            # The true value must be HIGHER (less negative) than mid_tsb.
            # Therefore, mid_tsb becomes the new "most aggressive" possible value (the lower bound).
            print(" (Too High)")
            lower_bound_tsb = mid_tsb
        else:
            # Measured ramp is too low, so the test TSB is not aggressive enough (too positive).
            # The true value must be LOWER (more negative) than mid_tsb.
            # Therefore, mid_tsb becomes the new "least aggressive" possible value (the upper bound).
            print(" (Too Low)")
            upper_bound_tsb = mid_tsb
    
    final_tsb = (upper_bound_tsb + lower_bound_tsb) / 2
    return final_tsb

# --- Main program execution ---
if __name__ == "__main__":
    print("--- TSB Calibration Tool ---")
    print("This script calculates the TSB value that corresponds to a desired")
    print("weekly increase in training load (TSS ramp rate) for any given")
    print("CTL and ATL time constants.")
    
    print("\n--- Model Time Constants ---")
    ctl_period_input = int(input("Enter the CTL period in days (e.g., 32): "))
    atl_period_input = int(input("Enter the ATL period in days (e.g., 4): "))
    
    print("\n--- Target Ramp Rate ---")
    target_ramp_input = float(input("Enter your desired weekly TSS ramp rate (e.g., 49): "))
    
    equivalent_tsb = find_tsb_for_ramp_rate(target_ramp_input, ctl_period_input, atl_period_input)
    
    print("\n--- Calibration Complete ---")
    print(f"For a CTL/ATL period of {ctl_period_input}/{atl_period_input} days, a TSB of ~{equivalent_tsb:.2f}")
    print(f"corresponds to a weekly TSS ramp rate of approximately {target_ramp_input:.1f} TSS/week.")