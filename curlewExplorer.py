import numpy as np
import pandas as pd

from scipy.signal import savgol_filter

# Define a singleton object for the data rail for this project
class CurlewDataRailSingleton(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(CurlewDataRailSingleton, cls).__new__(cls)
        return cls.instance

    def update(self,rail):
        self.rail = rail

    # Initialise the object
    filename1 = ""
    filename2 = ""
    df = pd.DataFrame()
    df_graph = pd.DataFrame()
    stats_df = pd.DataFrame()
    rate_of_change_df = pd.DataFrame()
    x = 0
    y_1 = 0
    y_2 = 0
    xAxisName = "x-axis"
    yAxisName = "y-axis"
    graphTitle = "None"
    graphType = "none"
    graphDay = 0
    totalDays = 0
    data_by_days = (pd.DataFrame())
    grid = False
    mouseClick = 0.0
    daysList = ()
    smoothedData = True


def time_in_seconds(time_str):
    # Split the time string into hours, minutes, and seconds
    h, m, s = map(int, time_str.split(':'))
    # Calculate total seconds since midnight
    total_seconds = h * 3600 + m * 60 + s
    return total_seconds

    # Chop the hed and tail off the data
def getDataChopIndex(df):
    ''' This routine will take calculate the standard deviation
    of the nest temperature and find the data points at the
    start and end that fall outside of this. These values
    can then be used to trim the beginning and end from the datafram
    '''
    # Top and Tail the Data
    # Calculate the Standard Deviation of the nest data
    nestStd = df.describe(include='all').loc['std']['temp2']

    # Define a convergence threshold, 2 being 2 standard deviations
    threshold = nestStd * 2

    # Step 1: Calculate the absolute difference
    df['difference'] = np.abs(df['temp1'] - df['temp2'])

    # Step 2: Identify sections where the difference is below the threshold
    df['converged'] = df['difference'] < threshold

    # Step 3: Find the indices of converged regions
    converged_indices = df.index[df['converged']].tolist()

    # Identify the start and end of the middle convergence
    start_index = next(
        i for i in range(1, len(converged_indices)) if converged_indices[i] != converged_indices[i - 1] + 1)
    end_index = next(
        i for i in range(len(converged_indices) - 2, -1, -1) if converged_indices[i] != converged_indices[i + 1] - 1)

    print(f'Start index: {converged_indices[start_index]}, End index: {converged_indices[end_index]}')

    startChop=converged_indices[start_index]
    endChop=converged_indices[end_index]
    #startChop=550
    #endChop=4345
    return (startChop,endChop)

def smoothLine(y):
    ''' This routine will use a Savitzky-Golay filter
    to smooth the curve of a line'''
    window = 21
    order = 2
    y_sf = savgol_filter(y, window, order)
    return y_sf

def parse_datetime_column(df, column_name='datetime', formats=None):
    """
    Attempts to parse the datetime column in a DataFrame using a list of possible date formats.

    Parameters:
    - df: DataFrame containing the datetime column
    - column_name: The name of the datetime column to parse
    - formats: List of datetime formats to try

    Returns:
    - DataFrame with the parsed datetime column, or None if no format was successful
    """
    if formats is None:
        formats = [
            '%d/%m/%Y %H:%M:%S',
            '%d/%m/%y %H:%M:%S',
            '%d/%m/%Y %H:%M',
            '%d/%m/%y %H:%M',
            '%m/%d/%y %H:%M:%S',
            '%m/%d/%Y %H:%M:%S',
            '%Y-%m-%d %H:%M:%S',
            '%y-%m-%d %H:%M:%S',
            # Add any additional formats here as needed
        ]

    for fmt in formats:
        try:
            df[column_name] = pd.to_datetime(df[column_name], format=fmt)
            print(f"Successfully parsed {column_name} using format: {fmt}")
            return df
        except ValueError:
            continue  # Try the next format if this one fails

    print(f"Unable to parse {column_name} column with provided formats.")
    return None

def loadFiles(dataRail):
    global df1, df2
    for fn, df_name in zip([dataRail.filename1, dataRail.filename2], ["df1", "df2"]):
        print(f'Loading files {fn} into {df_name}')

        # Load CSV into DataFrame
        df = pd.read_csv(fn, skiprows=20, index_col=False, names=['date', 'time', 'unit', 'temp'])

        # Some files have only 3 columns and not 4
        # Check to see if the format loaded has a completly empty 'temp' column.
        if (df['temp'].isna().sum()) == df.shape[0]:
            print('This is in Legacy data format... Retying...')

            # Load data frame in legacy format (ie, 3 data columns)
            df = pd.read_csv(fn, skiprows=20, index_col=False, names=['datetime', 'unit', 'temp'])
            df = parse_datetime_column(df, column_name='datetime')

            # Create 'date' and 'time' columns
            df['date'] = df['datetime'].dt.date  # Date only
            df['time'] = df['datetime'].dt.strftime('%H:%M').astype(str)  # Time as string
        else:
            # Add a 'datetime' column by combining 'date' and 'time' columns
            df['datetime'] = pd.to_datetime(df['date'] + ' ' + df['time'], format='%d/%m/%Y %H:%M:%S')

            # Convert the 'date' column into datetime format separately
            df['date'] = pd.to_datetime(df['date'], dayfirst=True)

        # Assign the modified DataFrame to the global variable
        globals()[df_name] = df

        # Print the first few rows to confirm
        print(globals()[df_name].head())

        # Merge the two tables, fitting the data in the time series as closely as possible
    df_merged = pd.merge_asof(df1, df2, on='datetime', suffixes=('', '2'))

    # Remove unwanted columns and rename temperature column
    df = df_merged[['datetime', 'date', 'time', 'temp', 'temp2']]
    df = df.rename(columns={'temp': 'temp1'})

    # Chop the hed and tail off the data
    chopVal = getDataChopIndex(df)
    print(f'Chop value: {chopVal}')
    df = df.iloc[(chopVal[0]):(chopVal[1])]
    #df = df.iloc[550:4345]
    df.reset_index(inplace=True)

    # Fill any NaN value with zero
    df.fillna(0.0, inplace=True)

    # Create a "Time Since Midnight" column
    # Here we create the new column using the `apply` function
    df["sincemidnight"] = df["time"].apply(time_in_seconds)

    # Calculate how many unique days of data we have
    dataRail.totalDays = df["date"].drop_duplicates().sort_values().size
    daysList = df["date"].drop_duplicates().sort_values().tolist()
    dataRail.daysList = [ts.strftime('%Y-%m-%d') for ts in daysList]

    # Remove Seconds from Time column
    df['time'] = df['datetime'].dt.strftime('%H:%M')  # Hour and Minute format

    # Remove seconds from 'datetime' column
    df['datetime'] = df['datetime'].dt.floor('min')  # Floors the datetime to the nearest minute

    print(f'Finished loading...')
    print(df.head())
    print(df.columns)

    # Update the object with the newly loaded DataFrame
    dataRail.df = df

    # Create a frame that only contains the data for a 24-hour period
    list_of_dates = dataRail.df["date"].drop_duplicates().sort_values().reset_index()
    data_by_days = pd.Series()
    for n, row in list_of_dates.iterrows():
        data_by_days[n] = dataRail.df[dataRail.df["date"].isin([row["date"]])]
    dataRail.data_by_days = data_by_days

    # Calculate the statistic graph
    dataRail = createStats(dataRail)

    # Set the graph to "All"
    dataRail = showAll(dataRail)
    return (dataRail)



def showAll(dataRail):
    dataRail.graphType = "all"

    dataRail.graphTitle = "All Nest Data"
    dataRail.xAxisName = ""
    dataRail.yAxisName = "Temperature (°C)"

    dataRail.x = dataRail.df["datetime"]
    dataRail.y_1 = dataRail.df["temp1"]
    dataRail.y_2 = dataRail.df["temp2"]
    return (dataRail)

def showDailyIndividual(dataRail):
    dataRail.graphType = "dailyIndividual"

    dataRail.graphTitle = pd.to_datetime(dataRail.data_by_days[dataRail.graphDay]["date"].iloc[0]).strftime('%d-%m-%Y')
    dataRail.xAxisName = "Hour"
    dataRail.yAxisName = "Temperature (°C)"

    #dataRail.x = (dataRail.df["sincemidnight"] / 60 / 60).tolist()
    #dataRail.x = list(range(len(dataRail.df["sincemidnight"] / 60 / 60).tolist()))
    #dataRail.x = dataRail.data_by_days[dataRail.graphDay]["time"]
    #print(type(dataRail.x))
    #print(dataRail.x.dt.strftime('%H:%M:%S'))
    dataRail.x = dataRail.data_by_days[dataRail.graphDay]["time"]
    dataRail.y_1 = dataRail.data_by_days[dataRail.graphDay]["temp1"]
    dataRail.y_2 = dataRail.data_by_days[dataRail.graphDay]["temp2"]
    return (dataRail)

def showDailyCombined(dataRail):
    dataRail.graphType = "dailyCombined"

    dataRail.graphTitle = "All Nest Data per Day"
    dataRail.xAxisName = "Hour"
    dataRail.yAxisName = "Temperature (°C)"

    dataRail.x = (dataRail.df["sincemidnight"] / 60 / 60).tolist()
    dataRail.y_1 = dataRail.df["temp1"].values.tolist()
    dataRail.y_2 = dataRail.df["temp2"].values.tolist()
    return (dataRail)

def showStatistics(dataRail):
    dataRail.graphType = "stats"

    dataRail.graphTitle = "Min, Max and Mean Temperatures"
    dataRail.xAxisName = "Hour"
    dataRail.yAxisName = "Temperature (°C)"

    return (dataRail)

def showChange(dataRail):
    dataRail.graphType = "change"

    RATE_OF_CHANGE = 20  # Minutes
    REPORT_THRESHOLD = 0.15  # % change

    dataRail.rate_of_change_df['change'] = dataRail.df['temp2'].pct_change(RATE_OF_CHANGE)

    dataRail.graphTitle = "Rate of Change"
    dataRail.xAxisName = "Date"
    dataRail.yAxisName = (f"% Change over {RATE_OF_CHANGE} min.")

    return (dataRail)

def createStats(dataRail):
    # Create a list of all of the unique dates
    date_list = dataRail.df['date'].unique()

    # Create an empty data frame to put the statistics in
    stats_df = pd.DataFrame(columns=['temp1_min', 'temp1_max', 'temp1_mean', 'temp2_min', 'temp2_max', 'temp2_mean'])

    # Loop around all of the unique dates
    for date in date_list:
        day_data = dataRail.df[dataRail.df["date"] == date]

        # Add a data series that constains the statistics
        stats_df.loc[date] = [min(day_data['temp1']),
                              max(day_data['temp1']),
                              np.mean(day_data['temp1']),
                              min(day_data['temp2']),
                              max(day_data['temp2']),
                              np.mean(day_data['temp2']), ]

    dataRail.stats_df = stats_df
    return(dataRail)


def incrementDay(dataRail):
    if dataRail.graphDay < (dataRail.totalDays - 1):
        dataRail.graphDay = dataRail.graphDay + 1
        dataRail = showDailyIndividual(dataRail)
    return (dataRail)

def decrementDay(dataRail):
    if dataRail.graphDay > 0:
        dataRail.graphDay = dataRail.graphDay - 1
        dataRail = showDailyIndividual(dataRail)
    return (dataRail)

def rewindDay(dataRail):
    dataRail.graphDay = 0
    dataRail = showDailyIndividual(dataRail)
    return (dataRail)

def fastforwardDay(dataRail):
    dataRail.graphDay = dataRail.totalDays - 1
    dataRail = showDailyIndividual(dataRail)
    return (dataRail)

def flipFiles(dataRail):
    fileaname1 = dataRail.filename1
    fileaname2 = dataRail.filename2
    dataRail.filename1 = fileaname2
    dataRail.filename2 = fileaname1
    dataRail = loadFiles(dataRail)
    return (dataRail)

def flipGrid(dataRail):
    if dataRail.grid == True:
        dataRail.grid = False
    else:
        dataRail.grid = True
    return (dataRail)

def flipSmoothed(dataRail):
    if dataRail.smoothedData == True:
        dataRail.smoothedData = False
    else:
        dataRail.smoothedData = True
    return (dataRail)


def mouseClick(dataRail):
    if dataRail.graphType == "all": # we only want to naviagate on a graph click if the 'all' view is active
        # Convert the event.xdata (float) to a datetime object, and make it timezone-naive
        event_datetime = mdates.num2date(dataRail.mouseClick).replace(tzinfo=None)

        # Convert event_datetime to pandas datetime
        event_datetime_pd = pd.to_datetime(event_datetime)

        # Ensure  DataFrame's datetime column is also timezone-naive
        dataRail.df['datetime'] = pd.to_datetime(dataRail.df['datetime']).dt.tz_localize(None)

        # Find the closest match in DataFrame
        nearest_index = (dataRail.df['datetime'] - event_datetime_pd).abs().idxmin()

        # Get the row corresponding to the nearest datetime in the DataFrame
        nearest_row = dataRail.df.iloc[nearest_index]

        # set the graph day to the nearest day to the event
        dataRail.graphDay = dataRail.daysList.index(nearest_row['datetime'].strftime('%Y-%m-%d'))

        # Immediatley plot the correct day
        dataRail = showDailyIndividual(dataRail)
    return (dataRail)

def buttonPress(buttonNumber, dataRail):
    print(f'Button {buttonNumber} pressed')
    if buttonNumber == 11: # Load Files
        dataRail = loadFiles(dataRail)

    if buttonNumber == 8: # All
        dataRail = showAll(dataRail)

    if buttonNumber == 10: # Daily
        dataRail = showDailyIndividual(dataRail)

    if buttonNumber == 12: # Individual
        dataRail = showDailyIndividual(dataRail)

    if buttonNumber == 13: # Combined
        dataRail = showDailyCombined(dataRail)

    if buttonNumber == 10: # Statistics
        dataRail = showStatistics(dataRail)

    if buttonNumber == 9: # Change
        dataRail = showChange(dataRail)

    if buttonNumber == 3: # Increment Day
        dataRail = incrementDay(dataRail)

    if buttonNumber == 5: # Decrement Day
        dataRail = decrementDay(dataRail)

    if buttonNumber == 7: # Rewind Day
        dataRail = rewindDay(dataRail)

    if buttonNumber == 4: # Fast Forward Day
        dataRail = fastforwardDay(dataRail)

    if buttonNumber == 6: # Flip Files
        dataRail = flipFiles(dataRail)

    if buttonNumber == 15: # Flip Grid
        dataRail = flipGrid(dataRail)

    if buttonNumber == 16: # Flip Grid
        dataRail = flipSmoothed(dataRail)

    if buttonNumber == 99: # Flip Grid
        dataRail = mouseClick(dataRail)

    return(dataRail)