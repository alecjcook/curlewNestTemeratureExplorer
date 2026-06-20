import pandas as pd


class CurlewDataRailSingleton(object):
    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(CurlewDataRailSingleton, cls).__new__(cls)
        return cls.instance

    def update(self, rail):
        self.rail = rail

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
    data_by_days = pd.DataFrame()
    grid = False
    mouseClick = 0.0
    daysList = ()
    smoothedData = True

