import pandas as pd
import matplotlib.dates as mdates


def show_all(data_rail):
    data_rail.graphType = "all"
    data_rail.graphTitle = "All Nest Data"
    data_rail.xAxisName = ""
    data_rail.yAxisName = "Temperature (deg C)"
    data_rail.x = data_rail.df["datetime"]
    data_rail.y_1 = data_rail.df["temp1"]
    data_rail.y_2 = data_rail.df["temp2"]
    return data_rail


def show_daily_individual(data_rail):
    data_rail.graphType = "dailyIndividual"
    data_rail.graphTitle = pd.to_datetime(
        data_rail.data_by_days[data_rail.graphDay]["date"].iloc[0]
    ).strftime("%d-%m-%Y")
    data_rail.xAxisName = "Hour"
    data_rail.yAxisName = "Temperature (deg C)"
    data_rail.x = data_rail.data_by_days[data_rail.graphDay]["time"]
    data_rail.y_1 = data_rail.data_by_days[data_rail.graphDay]["temp1"]
    data_rail.y_2 = data_rail.data_by_days[data_rail.graphDay]["temp2"]
    return data_rail


def show_daily_combined(data_rail):
    data_rail.graphType = "dailyCombined"
    data_rail.graphTitle = "All Nest Data per Day"
    data_rail.xAxisName = "Hour"
    data_rail.yAxisName = "Temperature (deg C)"
    data_rail.x = (data_rail.df["sincemidnight"] / 60 / 60).tolist()
    data_rail.y_1 = data_rail.df["temp1"].values.tolist()
    data_rail.y_2 = data_rail.df["temp2"].values.tolist()
    return data_rail


def show_statistics(data_rail):
    data_rail.graphType = "stats"
    data_rail.graphTitle = "Min, Max and Mean Temperatures"
    data_rail.xAxisName = "Hour"
    data_rail.yAxisName = "Temperature (deg C)"
    return data_rail


def show_change(data_rail):
    rate_of_change = 20
    data_rail.graphType = "change"
    data_rail.rate_of_change_df["change"] = data_rail.df["temp2"].pct_change(
        rate_of_change
    )
    data_rail.graphTitle = "Rate of Change"
    data_rail.xAxisName = "Date"
    data_rail.yAxisName = f"% Change over {rate_of_change} min."
    return data_rail


def increment_day(data_rail):
    if data_rail.graphDay < (data_rail.totalDays - 1):
        data_rail.graphDay = data_rail.graphDay + 1
        data_rail = show_daily_individual(data_rail)
    return data_rail


def decrement_day(data_rail):
    if data_rail.graphDay > 0:
        data_rail.graphDay = data_rail.graphDay - 1
        data_rail = show_daily_individual(data_rail)
    return data_rail


def rewind_day(data_rail):
    data_rail.graphDay = 0
    return show_daily_individual(data_rail)


def fastforward_day(data_rail):
    data_rail.graphDay = data_rail.totalDays - 1
    return show_daily_individual(data_rail)


def flip_grid(data_rail):
    data_rail.grid = not data_rail.grid
    return data_rail


def flip_smoothed(data_rail):
    data_rail.smoothedData = not data_rail.smoothedData
    return data_rail


def mouse_click(data_rail):
    if data_rail.graphType == "all" and data_rail.mouseClick is not None:
        event_datetime = mdates.num2date(data_rail.mouseClick).replace(tzinfo=None)
        event_datetime_pd = pd.to_datetime(event_datetime)
        data_rail.df["datetime"] = pd.to_datetime(
            data_rail.df["datetime"]
        ).dt.tz_localize(None)
        nearest_index = (data_rail.df["datetime"] - event_datetime_pd).abs().idxmin()
        nearest_row = data_rail.df.iloc[nearest_index]
        data_rail.graphDay = data_rail.daysList.index(
            nearest_row["datetime"].strftime("%Y-%m-%d")
        )
        data_rail = show_daily_individual(data_rail)
    return data_rail
