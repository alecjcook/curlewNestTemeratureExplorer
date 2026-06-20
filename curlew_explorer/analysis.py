import numpy as np
import pandas as pd
from scipy.signal import savgol_filter


def time_in_seconds(time_str):
    h, m, s = map(int, time_str.split(":"))
    return h * 3600 + m * 60 + s


def get_data_chop_index(df):
    """Find start/end indices where ambient and nest readings have converged."""
    nest_std = df.describe(include="all").loc["std"]["temp2"]
    threshold = nest_std * 2

    df["difference"] = np.abs(df["temp1"] - df["temp2"])
    df["converged"] = df["difference"] < threshold
    converged_indices = df.index[df["converged"]].tolist()

    start_index = next(
        i
        for i in range(1, len(converged_indices))
        if converged_indices[i] != converged_indices[i - 1] + 1
    )
    end_index = next(
        i
        for i in range(len(converged_indices) - 2, -1, -1)
        if converged_indices[i] != converged_indices[i + 1] - 1
    )

    print(
        f"Start index: {converged_indices[start_index]}, "
        f"End index: {converged_indices[end_index]}"
    )
    return converged_indices[start_index], converged_indices[end_index]


def smooth_line(y):
    window = 21
    order = 2
    return savgol_filter(y, window, order)


def create_stats(data_rail):
    date_list = data_rail.df["date"].unique()
    stats_df = pd.DataFrame(
        columns=[
            "temp1_min",
            "temp1_max",
            "temp1_mean",
            "temp2_min",
            "temp2_max",
            "temp2_mean",
        ]
    )

    for date in date_list:
        day_data = data_rail.df[data_rail.df["date"] == date]
        stats_df.loc[date] = [
            min(day_data["temp1"]),
            max(day_data["temp1"]),
            np.mean(day_data["temp1"]),
            min(day_data["temp2"]),
            max(day_data["temp2"]),
            np.mean(day_data["temp2"]),
        ]

    data_rail.stats_df = stats_df
    return data_rail

