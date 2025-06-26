# filename: contribution_analyzer.py

import math

def analyze_ewma_contributions():
    """
    Calculates and displays the percentage contribution of each preceding day
    to an exponentially weighted moving average (EWMA), which is the model
    used for CTL and ATL calculations.
    """
    print("--- EWMA Contribution Analyzer ---")
    print("This script shows the % contribution of each day's TSS to a CTL or ATL value.")

    try:
        n_days_str = input("Enter the time period in days for the average (e.g., 42 for CTL, 7 for ATL): ")
        n_days = int(n_days_str)
        if n_days < 2:
            print("Error: Period must be at least 2 days.")
            return

        cutoff_str = input("Enter the cutoff for contribution percentage (e.g., 1 for 1%): ")
        cutoff_pct = float(cutoff_str)
        if cutoff_pct <= 0:
            print("Error: Cutoff must be a positive number.")
            return

    except ValueError:
        print("Invalid input. Please enter valid numbers.")
        return

    # --- Calculation ---
    # The contribution of Today's TSS is 1/N
    # The contribution of Yesterday's TSS is (1/N) * ((N-1)/N)^1
    # The contribution of Day X ago is (1/N) * ((N-1)/N)^X

    today_multiplier = 1.0 / n_days
    decay_multiplier = (n_days - 1.0) / n_days

    day_ago = 0
    cumulative_percentage = 0.0
    contributions = []

    while True:
        # The weight of a given day's TSS contribution
        contribution = today_multiplier * (decay_multiplier ** day_ago)
        contribution_pct = contribution * 100.0
        
        # Stop if the contribution is too small
        if contribution_pct < cutoff_pct:
            break
            
        cumulative_percentage += contribution_pct
        contributions.append({
            "day": day_ago,
            "pct": contribution_pct,
            "cum_pct": cumulative_percentage
        })
        
        day_ago += 1
        # Safety break to prevent infinite loops with unusual inputs
        if day_ago > 365: 
            print("Stopping after 365 days to prevent an infinite loop.")
            break

    # --- Display Results ---
    print(f"\n--- Contribution Analysis for a {n_days}-day Period (Cutoff: {cutoff_pct}%) ---")
    print("-" * 60)
    print(f"{'Day(s) Ago':<15} | {'Contribution %':<18} | {'Cumulative %':<18}")
    print("-" * 60)

    for item in contributions:
        day_label = "0 (Today)" if item['day'] == 0 else str(item['day'])
        print(f"{day_label:<15} | {item['pct']:>15.2f} % | {item['cum_pct']:>15.2f} %")

    print("-" * 60)
    print(f"A total of {len(contributions)} days are shown, accounting for {cumulative_percentage:.2f}% of the total value.")
    print(f"The remaining {(100 - cumulative_percentage):.2f}% is contributed by all prior days.")


if __name__ == "__main__":
    analyze_ewma_contributions()