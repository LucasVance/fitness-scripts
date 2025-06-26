# filename: offline_planner.py

import math

def calculate_days_to_target_ctl(
    ctl_initial, atl_initial, ctl_final, tsb_final_target,
    alb_lower_bound,
    ctl_days,
    atl_days
):
    """
    Calculates the daily training progression based on provided goals and constraints.
    This version is fully generalized to support custom CTL and ATL time periods.
    """
    ctl_current = float(ctl_initial)
    atl_current = float(atl_initial)

    # --- Calculate constants from the user-defined time periods ---
    c = ctl_days
    a = atl_days

    # Multipliers for "yesterday's" load
    kc = (c - 1) / c
    ka = (a - 1) / a
    
    # Multiplier for the TSS difference when calculating TSB: (1/c - 1/a)
    tsb_tss_multiplier = (1/c) - (1/a)

    # Initialize data loggers
    days = 0
    ctl_history = [ctl_current]
    atl_history = [atl_current]
    tss_history = []
    daily_effective_tsb_target_history = []
    daily_alb_actual_history = []

    max_simulation_days = 365 * 10

    if ctl_final <= ctl_current and not (ctl_final < ctl_current):
         return 0, [ctl_current], [atl_current], [], [], []

    building_ctl = ctl_final > ctl_current

    for day_iter in range(max_simulation_days):
        days = day_iter

        # 1. Calculate TSS needed to aim for tsb_final_target
        if abs(tsb_tss_multiplier) > 1e-9:
            numerator = tsb_final_target - (ctl_current * kc) + (atl_current * ka)
            tss_for_tsb_goal = numerator / tsb_tss_multiplier
        else: # Handle c=a case
            tss_for_tsb_goal = atl_current

        # 2. Calculate TSS cap based on the improved ALB definition
        #    TSS_n <= ATL_{n-1} - ALB_lower_bound
        tss_cap_from_alb = atl_current - alb_lower_bound

        # 3. Determine final TSS for the day
        tss_needed = tss_for_tsb_goal
        if tss_needed > tss_cap_from_alb:
            tss_needed = tss_cap_from_alb

        tss_needed = max(0, tss_needed)

        # For logging: what effective TSB target does this tss_needed correspond to?
        effective_tsb_target_for_logging = (ctl_current * kc - atl_current * ka) + tss_needed * tsb_tss_multiplier
        daily_effective_tsb_target_history.append(effective_tsb_target_for_logging)

        # Calculate actual ALB using the new definition: ATL_morning - TSS_day
        actual_alb = atl_current - tss_needed
        daily_alb_actual_history.append(actual_alb)

        # Calculate next day's CTL and ATL
        atl_next = (atl_current * ka) + (tss_needed * (1/a))
        ctl_next = (ctl_current * kc) + (tss_needed * (1/c))

        tss_history.append(tss_needed)
        ctl_history.append(ctl_next)
        atl_history.append(atl_next)

        ctl_current = ctl_next
        atl_current = atl_next

        if (building_ctl and ctl_current >= ctl_final) or \
           (not building_ctl and ctl_current <= ctl_final):
            return days + 1, ctl_history, atl_history, tss_history, daily_effective_tsb_target_history, daily_alb_actual_history

    print(f"\nReached maximum simulation days ({max_simulation_days}).")
    return -1, ctl_history, atl_history, tss_history, daily_effective_tsb_target_history, daily_alb_actual_history

def get_float_input(prompt_text, allow_empty_for_default=False, default_val=0.0):
    while True:
        try:
            val_str = input(prompt_text).strip()
            if allow_empty_for_default and not val_str:
                return default_val
            return float(val_str)
        except ValueError:
            print("Invalid input. Please enter a numeric value.")

def get_int_input(prompt_text, min_val=2):
    while True:
        try:
            value = int(input(prompt_text).strip())
            if value < min_val:
                print(f"Please enter an integer >= {min_val}.")
                continue
            return value
        except ValueError:
            print("Invalid input. Please enter an integer.")

if __name__ == "__main__":
    print("--- Offline Training Load Projection Calculator ---")
    print("\n--- Model Time Periods ---")
    ctl_period = get_int_input("Enter CTL period in days (e.g., 40): ", min_val=2)
    atl_period = get_int_input("Enter ATL period in days (e.g., 4): ", min_val=2)
    
    print("\n--- Model Inputs ---")
    ctl_initial_val = get_float_input("Enter Initial CTL: ")
    atl_initial_val = get_float_input("Enter Initial ATL: ")
    ctl_final_val = get_float_input("Enter Target CTL (CTL final): ")
    tsb_final_target_val = get_float_input("Enter Final Target TSB (CTL - ATL) to aim for daily: ")

    default_alb_unrestricted = -200.0
    alb_lower_bound_val = get_float_input(
        f"Enter Minimum ALB (ATL_morning - Daily_TSS) you can take (e.g., -30; default {default_alb_unrestricted}): ",
        allow_empty_for_default=True, default_val=default_alb_unrestricted
    )

    print(f"\nCalculating days to reach CTL {ctl_final_val} ...\n")
    days_needed, ctl_progression, atl_progression, tss_progression, \
    daily_effective_tsb_targets, daily_alb_values = calculate_days_to_target_ctl(
        ctl_initial_val, atl_initial_val, ctl_final_val, tsb_final_target_val,
        alb_lower_bound_val, ctl_period, atl_period
    )

    if days_needed != -1:
        final_ctl_val = ctl_progression[-1]
        final_atl_val = atl_progression[-1]
        final_tsb_achieved = final_ctl_val - final_atl_val
        final_alb_achieved = daily_alb_values[-1] if daily_alb_values else "N/A"

        if days_needed == 0:
            print(f"Initial CTL ({ctl_initial_val:.2f}) already meets or exceeds target CTL ({ctl_final_val:.2f}).")
        else:
            print(f"It will take approximately {days_needed} days to reach a CTL of {final_ctl_val:.2f}.")

        print(f"Final CTL: {final_ctl_val:.2f}, Final ATL: {final_atl_val:.2f}")
        effective_tsb_on_final_day = f"{daily_effective_tsb_targets[-1]:.2f}" if daily_effective_tsb_targets else "N/A"
        print(f"Final Actual TSB (CTL-ATL): {final_tsb_achieved:.2f} (Effective TSB target on final day: {effective_tsb_on_final_day})")
        if isinstance(final_alb_achieved, float):
            print(f"Final Actual ALB (ATL_morning - TSS): {final_alb_achieved:.2f} (Target lower bound was {alb_lower_bound_val})")

        if tss_progression:
            avg_tss = sum(tss_progression) / len(tss_progression)
            max_tss_overall = max(tss_progression)
            print(f"Average TSS needed per day: {avg_tss:.2f}")
            print(f"Peak TSS during entire period: {max_tss_overall:.2f}")

        print("-" * 30)
        show_details_q = input("Show full daily progression in console? (yes/no): ").strip().lower()
        if show_details_q == 'yes':
            print("\nDaily Progression (Day: EffTSB_Trg, ActualTSS, CTL, ATL, ActualTSB, ActualALB):")
            start_tsb = ctl_progression[0] - atl_progression[0]
            print(f"Start: ---, ---, CTL={ctl_progression[0]:.2f}, ATL={atl_progression[0]:.2f}, TSB={start_tsb:.2f}, ALB=N/A")
            for i in range(days_needed):
                actual_daily_tsb = ctl_progression[i+1] - atl_progression[i+1]
                actual_daily_alb = daily_alb_values[i]
                eff_tsb_target_for_day = daily_effective_tsb_targets[i]
                alb_str = f"{actual_daily_alb:.2f}"
                print(f"Day {i+1}: EffTSBTrg={eff_tsb_target_for_day:.2f}, TSS={tss_progression[i]:.2f}, "
                      f"CTL={ctl_progression[i+1]:.2f}, ATL={atl_progression[i+1]:.2f}, TSBAct={actual_daily_tsb:.2f}, ALBAct={alb_str}")
            
            print("\n--- Weekly Summary ---")
            # (Weekly summary logic would go here, same as before)

    else:
        print(f"Could not reach target CTL ({ctl_final_val}) under constraints.")