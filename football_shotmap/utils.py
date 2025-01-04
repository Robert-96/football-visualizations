import pandas as pd


def get_season_label(year):
    """
    Generate a season label string in the format "YYYY/YY".

    Args:
        year (int): The starting year of the season.

    Returns:
        str: A string representing the season in the format "YYYY/YY".
    """

    return f"{year}/{int(year) % 100 + 1}"


def prepare_shot_data(data):
    """Prepare shot data by converting it to a DataFrame and adjusting coordinates.

    Takes raw shot data and converts it to a pandas DataFrame, ensuring proper data types
    for xG (Expected Goals), X and Y coordinates. Scales X and Y coordinates by multiplying
    them by 100 to match mplsoccer pitch dimensions.

    Args:
        data: Raw shot data that can be converted to a pandas DataFrame. Must contain
            columns 'xG', 'X', and 'Y'.

    Returns:
        pd.DataFrame: DataFrame containing the processed shot data with adjusted coordinates.
            Contains at minimum the following columns:
            - xG (float): Expected Goals value
            - X (float): X-coordinate multiplied by 100
            - Y (float): Y-coordinate multiplied by 100
    """

    df = pd.DataFrame(data)
    df = df.astype({"xG": float, "X": float, "Y": float})

    # Convert x and y for mplsoccer
    df["X"] = df["X"] * 100
    df["Y"] = df["Y"] * 100

    return df


def calculate_shots_stats(df):
    """Calculate statistics from a dataframe containing shot information.

    This function processes shot data and calculates various statistics including total shots,
    goals, expected goals (xG), and distance metrics.

    Args:
        df (pandas.DataFrame): DataFrame containing shot data with columns:
            - 'result': Shot outcome ('Goal' or other)
            - 'xG': Expected goals value for each shot
            - 'X': X-coordinate of shot location (in percentage of pitch length)

    Returns:
        dict: Dictionary containing the following statistics:
            - total_shots (int): Total number of shots
            - total_goals (int): Number of goals scored
            - total_xG (float): Sum of expected goals
            - xG_per_shot (float): Average expected goals per shot
            - points_average_distance (float): Average X coordinate of shots
            - actual_average_distance (float): Average shot distance in meters
    """

    total_shots = df.shape[0]
    total_goals = df[df['result'] == 'Goal'].shape[0]
    total_xG = df['xG'].sum()
    xG_per_shot = total_xG / total_shots
    points_average_distance = df['X'].mean()

    average_pitch_size = 105
    actual_average_distance = average_pitch_size - (df['X'] * average_pitch_size / 100).mean()

    return {
        'total_shots': total_shots,
        'total_goals': total_goals,
        'total_xG': total_xG,
        'xG_per_shot': xG_per_shot,
        'points_average_distance': points_average_distance,
        'actual_average_distance': actual_average_distance
    }
