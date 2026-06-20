import pandas as pd

from curlew_explorer.analysis import create_stats, get_data_chop_index, time_in_seconds
from curlew_explorer.views import show_all


def parse_datetime_column(df, column_name="datetime", formats=None):
    if formats is None:
        formats = [
            "%d/%m/%Y %H:%M:%S",
            "%d/%m/%y %H:%M:%S",
            "%d/%m/%Y %H:%M",
            "%d/%m/%y %H:%M",
            "%m/%d/%y %H:%M:%S",
            "%m/%d/%Y %H:%M:%S",
            "%Y-%m-%d %H:%M:%S",
            "%y-%m-%d %H:%M:%S",
        ]

    for fmt in formats:
        try:
            df[column_name] = pd.to_datetime(df[column_name], format=fmt)
            print(f"Successfully parsed {column_name} using format: {fmt}")
            return df
        except ValueError:
            continue

    print(f"Unable to parse {column_name} column with provided formats.")
    return None


def load_temperature_file(filename):
    df = pd.read_csv(
        filename,
        skiprows=20,
        index_col=False,
        names=["date", "time", "unit", "temp"],
    )

    if (df["temp"].isna().sum()) == df.shape[0]:
        print("This is in Legacy data format... Retrying...")
        df = pd.read_csv(
            filename,
            skiprows=20,
            index_col=False,
            names=["datetime", "unit", "temp"],
        )
        df = parse_datetime_column(df, column_name="datetime")
        df["date"] = df["datetime"].dt.date
        df["time"] = df["datetime"].dt.strftime("%H:%M:%S").astype(str)
    else:
        df["datetime"] = pd.to_datetime(
            df["date"] + " " + df["time"],
            format="%d/%m/%Y %H:%M:%S",
        )
        df["date"] = pd.to_datetime(df["date"], dayfirst=True)

    return df


def load_files(data_rail):
    print(f"Loading files {data_rail.filename1} and {data_rail.filename2}")
    df1 = load_temperature_file(data_rail.filename1)
    df2 = load_temperature_file(data_rail.filename2)

    print(df1.head())
    print(df2.head())

    df_merged = pd.merge_asof(df1, df2, on="datetime", suffixes=("", "2"))
    df = df_merged[["datetime", "date", "time", "temp", "temp2"]]
    df = df.rename(columns={"temp": "temp1"})

    chop_val = get_data_chop_index(df)
    print(f"Chop value: {chop_val}")
    df = df.iloc[chop_val[0] : chop_val[1]]
    df.reset_index(inplace=True)
    df.fillna(0.0, inplace=True)

    df["sincemidnight"] = df["time"].apply(time_in_seconds)

    data_rail.totalDays = df["date"].drop_duplicates().sort_values().size
    days_list = df["date"].drop_duplicates().sort_values().tolist()
    data_rail.daysList = [ts.strftime("%Y-%m-%d") for ts in days_list]

    df["time"] = df["datetime"].dt.strftime("%H:%M")
    df["datetime"] = df["datetime"].dt.floor("min")

    print("Finished loading...")
    print(df.head())
    print(df.columns)

    data_rail.df = df

    list_of_dates = data_rail.df["date"].drop_duplicates().sort_values().reset_index()
    data_by_days = pd.Series()
    for n, row in list_of_dates.iterrows():
        data_by_days[n] = data_rail.df[data_rail.df["date"].isin([row["date"]])]
    data_rail.data_by_days = data_by_days

    data_rail = create_stats(data_rail)
    return show_all(data_rail)

