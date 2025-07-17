import math

def calculate_hrss(
    max_hr: int,
    resting_hr: int,
    threshold_hr: int,
    activity_duration_minutes: float,
    avg_activity_hr: float,
    gender: str = 'male'
) -> dict:
    """
    Calculates the Heart Rate Stress Score (HRSS) for a given activity.

    This calculation is a simplification as it uses the average heart rate for the
    entire activity rather than a second-by-second heart rate data stream.

    Args:
        max_hr: The user's maximum heart rate.
        resting_hr: The user's resting (minimum) heart rate.
        threshold_hr: The user's lactate threshold heart rate (LTHR).
        activity_duration_minutes: The total duration of the activity in minutes.
        avg_activity_hr: The average heart rate during the activity.
        gender: The user's gender ('male' or 'female') for the TRIMP constant.

    Returns:
        A dictionary containing the calculated HRSS and intermediate values.
    """
    if resting_hr >= max_hr or resting_hr >= threshold_hr:
        raise ValueError("Resting HR must be lower than Max HR and Threshold HR.")

    # Determine the gender-specific constant for the TRIMP calculation
    k = 1.92 if gender.lower() == 'male' else 1.67

    # --- Step 1: Calculate TRIMP for the entire activity ---
    # Calculate Heart Rate Reserve (%HRR) for the activity's average HR
    if max_hr > resting_hr:
        activity_hrr = (avg_activity_hr - resting_hr) / (max_hr - resting_hr)
    else:
        activity_hrr = 0
    
    # Ensure HRR is not negative if avg_activity_hr is below resting_hr
    activity_hrr = max(0, activity_hrr)

    # Calculate the TRIMP score for the activity
    activity_trimp = (
        activity_duration_minutes *
        activity_hrr *
        0.64 *
        math.exp(k * activity_hrr)
    )

    # --- Step 2: Calculate the 1-hour benchmark TRIMP at Threshold HR ---
    # Calculate Heart Rate Reserve (%HRR) at threshold
    if max_hr > resting_hr:
        threshold_hrr = (threshold_hr - resting_hr) / (max_hr - resting_hr)
    else:
        threshold_hrr = 0

    # Calculate the TRIMP score for 1 hour (60 minutes) at threshold HR
    one_hour_threshold_trimp = (
        60 *
        threshold_hrr *
        0.64 *
        math.exp(k * threshold_hrr)
    )

    # --- Step 3: Calculate the final HRSS ---
    # Scale the activity TRIMP against the 1-hour threshold benchmark
    if one_hour_threshold_trimp > 0:
        hrss = (activity_trimp / one_hour_threshold_trimp) * 100
    else:
        hrss = 0

    return {
        "activity_trimp": round(activity_trimp, 2),
        "one_hour_threshold_trimp": round(one_hour_threshold_trimp, 2),
        "hrss": round(hrss, 2)
    }

def get_user_input():
    """Prompts the user for required data and validates it."""
    inputs = {}
    print("--- Please Enter Your Personal Data ---")
    while True:
        try:
            inputs['max_hr'] = int(input("Enter your Maximum HR (bpm): "))
            break
        except ValueError:
            print("Invalid input. Please enter a whole number.")
    
    while True:
        try:
            inputs['resting_hr'] = int(input("Enter your Resting HR (bpm): "))
            break
        except ValueError:
            print("Invalid input. Please enter a whole number.")

    while True:
        try:
            inputs['threshold_hr'] = int(input("Enter your Threshold HR (bpm): "))
            break
        except ValueError:
            print("Invalid input. Please enter a whole number.")

    while True:
        gender = input("Enter your gender ('male' or 'female'): ").lower()
        if gender in ['male', 'female']:
            inputs['gender'] = gender
            break
        else:
            print("Invalid input. Please enter 'male' or 'female'.")

    print("\n--- Please Enter Activity Data ---")
    while True:
        try:
            inputs['duration'] = float(input("Enter activity duration (in minutes): "))
            break
        except ValueError:
            print("Invalid input. Please enter a number.")

    while True:
        try:
            inputs['avg_hr'] = float(input("Enter average HR for the activity (bpm): "))
            break
        except ValueError:
            print("Invalid input. Please enter a number.")
            
    return inputs

if __name__ == '__main__':
    user_data = get_user_input()

    print("\n--- Calculating HRSS with the following data ---")
    print(f"Max HR: {user_data['max_hr']} bpm")
    print(f"Resting HR: {user_data['resting_hr']} bpm")
    print(f"Threshold HR: {user_data['threshold_hr']} bpm")
    print(f"Gender: {user_data['gender'].capitalize()}")
    print(f"Activity Duration: {user_data['duration']} minutes")
    print(f"Activity Average HR: {user_data['avg_hr']} bpm")
    print("-" * 45)

    try:
        # Calculate the HRSS
        results = calculate_hrss(
            max_hr=user_data['max_hr'],
            resting_hr=user_data['resting_hr'],
            threshold_hr=user_data['threshold_hr'],
            activity_duration_minutes=user_data['duration'],
            avg_activity_hr=user_data['avg_hr'],
            gender=user_data['gender']
        )

        # Print the results
        print(f"Activity TRIMP Score: {results['activity_trimp']}")
        print(f"1-Hour Benchmark TRIMP at Threshold: {results['one_hour_threshold_trimp']}")
        print("\n--- Final Score ---")
        print(f"HRSS: {results['hrss']}")
        print("-------------------")

    except ValueError as e:
        print(f"Error: {e}")
