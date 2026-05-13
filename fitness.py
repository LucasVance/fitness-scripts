import math

def calculate_days_to_target_ctl(
    ctl_initial, atl_initial, ctl_final,
    ctl_days,
    atl_days,
    mode='tsb',
    tsb_final_target=None,
    alb_lower_bound=None,
    ramp_rate_per_week=None
):
    """
    Calculates the daily training progression based on provided goals and constraints.
    Supports either TSB/ALB mode or TSS Ramp Rate mode.
    """
    ctl_current = float(ctl_initial)
    atl_current = float(atl_initial)

    # --- Calculate constants from the user-defined time periods ---
    c = ctl_days
    a = atl_days
    kc = (c - 1) / c
    ka = (a - 1) / a
    tsb_tss_multiplier = (1/c) - (1/a)

    # Initialize data loggers
    days = 0
    ctl_history = [ctl_current]
    atl_history = [atl_current]
    tss_history = []
    daily_alb_actual_history = []

    max_simulation_days = 365 * 10

    if ctl_final <= ctl_current and not (ctl_final < ctl_current):
         return 0, [ctl_current], [atl_current], [], []

    building_ctl = ctl_final > ctl_current

    for day_iter in range(max_simulation_days):
        days = day_iter

        if mode == 'tsb':
            # 1. Calculate TSS needed to aim for tsb_final_target
            if abs(tsb_tss_multiplier) > 1e-9:
                numerator = tsb_final_target - (ctl_current * kc) + (atl_current * ka)
                tss_for_tsb_goal = numerator / tsb_tss_multiplier
            else:
                tss_for_tsb_goal = atl_current

            # 2. Calculate TSS cap based on the improved ALB definition
            tss_cap_from_alb = atl_current - alb_lower_bound

            # 3. Determine final TSS for the day
            tss_needed = min(tss_for_tsb_goal, tss_cap_from_alb)
        elif mode == 'ramp_rate':
            tss_needed = ctl_current + (ramp_rate_per_week / 7) * c

        tss_needed = max(0, tss_needed)

        actual_alb = atl_current - tss_needed
        daily_alb_actual_history.append(actual_alb)

        atl_next = (atl_current * ka) + (tss_needed * (1/a))
        ctl_next = (ctl_current * kc) + (tss_needed * (1/c))

        tss_history.append(tss_needed)
        ctl_history.append(ctl_next)
        atl_history.append(atl_next)

        ctl_current = ctl_next
        atl_current = atl_next

        if (building_ctl and ctl_current >= ctl_final) or \
           (not building_ctl and ctl_current <= ctl_final):
            return days + 1, ctl_history, atl_history, tss_history, daily_alb_actual_history

    print(f"\nReached maximum simulation days ({max_simulation_days}).")
    return -1, ctl_history, atl_history, tss_history, daily_alb_actual_history

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
    ctl_period = get_int_input("CTL period in days: ", min_val=2)
    atl_period = get_int_input("ATL period in days: ", min_val=2)
    ctl_initial_val = get_float_input("\nInitial CTL: ")
    atl_initial_val = get_float_input("Initial ATL: ")
    ctl_final_val = get_float_input("Target CTL: ")

    print("\n1. TSB / ALB Target Mode")
    print("2. TSS Ramp Rate Mode")
    while True:
        mode_choice = input("Select mode: ").strip()
        if mode_choice in ['1', '2']:
            break
        print("Invalid choice. Please enter 1 or 2.")

    tsb_final_target_val = None
    alb_lower_bound_val = None
    ramp_rate_val = None

    if mode_choice == '1':
        calc_mode = 'tsb'
        tsb_final_target_val = get_float_input("\nDaily target TSB (CTL - ATL): ")
        default_alb_unrestricted = -200.0
        alb_lower_bound_val = get_float_input(
            f"Minimum ALB (ATL_morning - daily TSS): ",
            allow_empty_for_default=True, default_val=default_alb_unrestricted
        )
    else:
        calc_mode = 'ramp_rate'
        ramp_rate_val = get_float_input("\nRamp rate (increase in CTL per week): ")

    days_needed, ctl_progression, atl_progression, tss_progression, \
    daily_alb_values = calculate_days_to_target_ctl(
        ctl_initial=ctl_initial_val, atl_initial=atl_initial_val, ctl_final=ctl_final_val,
        ctl_days=ctl_period, atl_days=atl_period,
        mode=calc_mode,
        tsb_final_target=tsb_final_target_val,
        alb_lower_bound=alb_lower_bound_val,
        ramp_rate_per_week=ramp_rate_val
    )

    if days_needed != -1:
        final_ctl_val = ctl_progression[-1]
        final_atl_val = atl_progression[-1]
        final_tsb_achieved = final_ctl_val - final_atl_val
        final_alb_achieved = daily_alb_values[-1] if daily_alb_values else "N/A"
        # Calculate final Shape
        final_shape = (2 * final_ctl_val) - final_atl_val

        if days_needed == 0:
            print(f"Initial CTL ({ctl_initial_val:.2f}) already meets or exceeds target CTL ({ctl_final_val:.2f}).")
        else:
            print(f"It will take approximately {days_needed} days to reach a CTL of {final_ctl_val:.2f}.")

        print(f"Final CTL: {final_ctl_val:.2f}, Final ATL: {final_atl_val:.2f}")
        print(f"Final TSB: {final_tsb_achieved:.2f}")
        if calc_mode == 'tsb' and isinstance(final_alb_achieved, float):
            print(f"Final ALB: {final_alb_achieved:.2f}")
        # Print final Shape
        print(f"Final Shape (2*CTL - ATL): {final_shape:.2f}")

        if tss_progression:
            avg_tss = sum(tss_progression) / len(tss_progression) if tss_progression else 0
            max_tss_overall = max(tss_progression) if tss_progression else 0
            print(f"Average TSS needed per day: {avg_tss:.2f}")
            print(f"Peak TSS during entire period: {max_tss_overall:.2f}")

        print("-" * 30)
        if calc_mode == 'tsb':
            start_tsb = ctl_progression[0] - atl_progression[0]
            start_shape = (2 * ctl_progression[0]) - atl_progression[0]
            print(f"Start: CTL={ctl_progression[0]:.2f}, ATL={atl_progression[0]:.2f}, TSB={start_tsb:.2f}, ALB=N/A, Shape={start_shape:.2f}")
            for i in range(days_needed):
                actual_daily_tsb = ctl_progression[i+1] - atl_progression[i+1]
                actual_daily_alb = daily_alb_values[i]
                actual_daily_shape = (2 * ctl_progression[i+1]) - atl_progression[i+1]
                alb_str = f"{actual_daily_alb:.2f}"
                print(f"Day {i+1}: TSS={tss_progression[i]:.2f}, "
                      f"CTL={ctl_progression[i+1]:.2f}, ATL={atl_progression[i+1]:.2f}, TSBAct={actual_daily_tsb:.2f}, ALB={alb_str}, "
                      f"Shape={actual_daily_shape:.2f}")
        else:
            start_tsb = ctl_progression[0] - atl_progression[0]
            start_shape = (2 * ctl_progression[0]) - atl_progression[0]
            print(f"Start: CTL={ctl_progression[0]:.2f}, ATL={atl_progression[0]:.2f}, TSB={start_tsb:.2f}, Shape={start_shape:.2f}")
            for i in range(days_needed):
                actual_daily_tsb = ctl_progression[i+1] - atl_progression[i+1]
                actual_daily_shape = (2 * ctl_progression[i+1]) - atl_progression[i+1]
                print(f"Day {i+1}: TSS={tss_progression[i]:.2f}, "
                      f"CTL={ctl_progression[i+1]:.2f}, ATL={atl_progression[i+1]:.2f}, TSBAct={actual_daily_tsb:.2f}, "
                      f"Shape={actual_daily_shape:.2f}")
            
            # --- UPDATED: Added 'Shape' to weekly summary ---
            num_weeks = (days_needed + 6) // 7
            print("\n")
            print(f"{'Week':<5} | {'Days':<10} | {'Total TSS':<10} | {'End CTL':<10} | {'End ATL':<10} | {'End TSB':<10} | {'End Shape':<10} | {'Ramp Rate':<10}")
            print("-" * 95)
            for week_idx in range(num_weeks):
                week_num = week_idx + 1
                start_day_tss_idx = week_idx * 7
                end_day_tss_idx = min((week_idx + 1) * 7, days_needed)
                
                display_day_start = start_day_tss_idx + 1
                display_day_end = end_day_tss_idx
                
                weekly_tss_values = tss_progression[start_day_tss_idx:end_day_tss_idx]
                total_weekly_tss = sum(weekly_tss_values) if weekly_tss_values else 0
                
                ctl_end_of_week = ctl_progression[display_day_end] 
                atl_end_of_week = atl_progression[display_day_end]
                tsb_end_of_week = ctl_end_of_week - atl_end_of_week
                # --- NEW: Calculate Shape for end of week ---
                shape_end_of_week = (2 * ctl_end_of_week) - atl_end_of_week

                ctl_7_days_prior_idx = max(0, display_day_end - 7)
                ctl_7_days_prior = ctl_progression[ctl_7_days_prior_idx]
                ramp_rate = ctl_end_of_week - ctl_7_days_prior

                print(f"{week_num:<5} | {f'{display_day_start}-{display_day_end}':<10} | {total_weekly_tss:<10.0f} | "
                      f"{ctl_end_of_week:<10.1f} | {atl_end_of_week:<10.1f} | {tsb_end_of_week:<10.1f} | "
                      f"{shape_end_of_week:<10.1f} | {ramp_rate:<+10.1f}")
            print("-" * 95)

    else:
        print(f"Could not reach target CTL ({ctl_final_val}) under constraints.")
