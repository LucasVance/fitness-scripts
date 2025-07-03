# filename: peak_ctl_calculator.py

def get_float_input(prompt_text, default_val=None):
    """Gets a float input from the user with basic validation."""
    while True:
        try:
            # Append default value to prompt if it exists
            prompt_with_default = prompt_text
            if default_val is not None:
                prompt_with_default += f" (default: {default_val}): "
            else:
                prompt_with_default += ": "
                
            val_str = input(prompt_with_default).strip()
            
            # Use default if user just presses Enter
            if not val_str and default_val is not None:
                return default_val
                
            return float(val_str)
        except ValueError:
            print("Invalid input. Please enter a numeric value.")

def calculate_peak_ctl():
    """
    Calculates the target CTL needed to achieve a desired peak Shape,
    given a planned TSB (freshness) for that peak day.
    """
    print("--- Peak CTL Calculator ---")
    print("This tool helps you determine the target Chronic Training Load (CTL)")
    print("needed to achieve a desired 'Shape' (2*CTL - ATL) on your peak day.")
    print("-" * 20)

    # Get user inputs
    target_shape = get_float_input("Enter your Target 'Shape' for your peak performance day")
    peak_tsb = get_float_input("Enter your planned TSB (freshness) for that day", default_val=20.0)

    # --- The Core Calculation ---
    # Based on the derived formula: Target CTL = Target Shape - Peak TSB
    target_ctl = target_shape - peak_tsb

    # --- Display Results ---
    print("\n--- Calculation Result ---")
    print(f"To achieve a 'Shape' of {target_shape:.1f} while being fresh with a TSB of {peak_tsb:+.1f},")
    print(f"you need to build to a peak Chronic Training Load (CTL) of: {target_ctl:.1f}")
    print("\nThis CTL value can now be used as the 'Target CTL' in your planning scripts.")
    print("-" * 26)

if __name__ == "__main__":
    calculate_peak_ctl()
