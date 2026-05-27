# ====================================
# Lightweight imports first
# ====================================

from tkinter import (
    Tk,
    Label,
    Canvas,
    Entry,
    Button,
    PhotoImage
)

import tkinter.filedialog
import tkinter as tk

from pathlib import Path
import sys

import pandas as pd

from version import VERSION

# ====================================
# Splash screen
# ====================================

window = Tk()
window.withdraw()

splash = tk.Toplevel(window)
splash.overrideredirect(True)
splash.geometry("300x120")
splash.configure(bg="#F3EDE5")

Label(
    splash,
    text="Loading Curlew Explorer...",
    font=("Arial", 14),
    bg="#F3EDE5"
).pack(expand=True)

splash.update()

# ====================================
# Heavy imports AFTER splash appears
# ====================================

import curlewExplorer as ce
from curlewExplorer import CurlewDataRailSingleton

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


# Determine the base path for assets
def get_base_path():
    if hasattr(sys, '_MEIPASS'):
        return Path(sys._MEIPASS) / 'assets' / 'frame0'
    return Path(__file__).parent / 'assets' / 'frame0'

ASSETS_PATH = get_base_path()

def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)


# Next we initiate the Data rail for the application
dataRail = CurlewDataRailSingleton()


# This routing will operate every time a button is pressed
def guiButtonPress(buttonNumber):
    # Update data Rail with all UI Data
    dataRail.filename1 = ambient_entry.get()
    dataRail.filename2 = nest_entry.get()

    # Call the Button Press function
    dataRail.update(ce.buttonPress(buttonNumber, dataRail))

    # Update the UI with data from the rail.
    updateGraph(dataRail)
    updateUI(dataRail)

def mouse_event(event):
   #print('x: {} and y: {}'.format(event.xdata, event.ydata))
   # Here we are going to spoof the button press command cause the arcitecture of this program is bad
   dataRail.mouseClick = event.xdata
   guiButtonPress(99)

def updateUI(dataRail):
    nest_entry.delete(0, tk.END)
    ambient_entry.delete(0, tk.END)
    nest_entry.insert(0, dataRail.filename1)
    ambient_entry.insert(0, dataRail.filename2)

def updateGraph(dataRail):
    # Clear the data on the existing graph (so we dont end up with a memory leak
    fig.clear()
    fig_canvas.draw_idle()

    # Here we create the subplot to display our data as a figure
    plt = fig.add_subplot(111)

    if dataRail.graphType == "none":
        pass    # This ensures we do not try and display the data if we do not have any.
    else:
        if dataRail.graphType == "all":                                             # Plot the all graph
            # Create the actual plots
            plt.plot(dataRail.x, ce.smoothLine(dataRail.y_1), color='tab:blue',
                     linewidth=0.9, linestyle='-', label="Ambient")
            plt.plot(dataRail.x, ce.smoothLine(dataRail.y_2), color='tab:red',
                     linewidth=0.9, linestyle='-', label="Nest")

            # Next we alight the x-axis

            plt.tick_params(axis='x',labelsize='small', rotation=45)
            tick_positions = dataRail.x.values[::24 * 12]
            plt.set_xticks(tick_positions)
            plt.set_xticklabels([pd.to_datetime(tick).strftime('%d-%m') for tick in tick_positions], rotation=45)

            # Grid and Legend
            plt.legend()

        elif dataRail.graphType == "dailyIndividual":                               # Plot the dailyIndividual graph
            if dataRail.smoothedData == True:
                plt.plot(dataRail.x, ce.smoothLine(dataRail.y_1), color='tab:blue',
                         linewidth=0.9, linestyle='-', label="Ambient")
                plt.plot(dataRail.x, ce.smoothLine(dataRail.y_2), color='tab:red',
                         linewidth=0.9, linestyle='-', label="Nest")
            else:
                # Add the original un-filtered Data
                plt.plot(dataRail.x, dataRail.y_1, color='darkblue',
                         linewidth=0.9, linestyle='-', label="Ambient (raw)")
                plt.plot(dataRail.x, dataRail.y_2, color='maroon',
                         linewidth=0.9, linestyle='-', label="Nest (raw)")

                # Calculate the upper and lower bounds for the ±5°C inaccuracy
                upper_bound_1 = dataRail.y_1 + 0.49
                lower_bound_1 = dataRail.y_1 - 0.49
                upper_bound_2 = dataRail.y_2 + 0.49
                lower_bound_2 = dataRail.y_2 - 0.49

                # Add the inaccuracy as a shaded region
                plt.fill_between(dataRail.x, lower_bound_1, upper_bound_1, color='tab:blue', alpha=0.2, label="Ambient ±0.49°C")
                plt.fill_between(dataRail.x, lower_bound_2, upper_bound_2, color='tab:red', alpha=0.2, label="Nest ±0.49°C")

            #plt.xticks(df.index.values[::24 * 12], rotation=45)
            plt.tick_params(axis='x',labelsize='small', rotation=45)
            tick_positions = dataRail.x.values[::6]
            plt.set_xticks(tick_positions)
            #plt.xaxis.set_major_formatter(DateFormatter('%H:%M'))
            plt.set_xticklabels([pd.to_datetime(tick).strftime('%H') for tick in tick_positions], rotation=45)
            plt.legend()
            '''
            # Label the axes and add a legend
            plt.title("Nest Temperature Data")
            plt.ylabel("Temperature in °C", size=12)
            plt.xlabel("Hour", size=12)
            plt.xticks(df_merged['datetime'][::24 * 12], rotation=45)
            plt.legend()
            '''

        elif dataRail.graphType == "dailyCombined":                                  # Plot the dailyCombined graph
            def scatterPlotWithTrendline(colour, x, y, label):
                # create scatterplot
                plt.scatter(x, y, color=colour, alpha=0.03, label=label)

                # calculate equation for quadratic trendline
                z = np.polyfit(x, y, 5)
                p = np.poly1d(z)

                # add trendline to plot
                plt.plot(x_smooth, p(x_smooth), color=colour)

            # We will smooth out the x-axis to stop the trend line looping back on itself
            x_smooth = np.linspace(min(dataRail.x), max(dataRail.x), 500)

            # Now we will plot both graphs and trend lines on one plot
            scatterPlotWithTrendline('tab:blue', dataRail.x, dataRail.y_1, label="Ambient")
            scatterPlotWithTrendline('tab:red', dataRail.x, dataRail.y_2, label="Nest")
            for l in plt.legend().legend_handles: l.set_alpha(1)

        elif dataRail.graphType == "stats":                                             # Plot the stats graph
            def plotTwoLineGraph(plotOne, plotTwo, alpha):
                # Create a plot containing both temp1 and temp2 value columns
                plt.plot(dataRail.stats_df.index.values, plotOne, color='tab:blue',
                         linewidth=0.9, linestyle='-', alpha=alpha)
                plt.plot(dataRail.stats_df.index.values, plotTwo, color='tab:red',
                         linewidth=0.9, linestyle='-', alpha=alpha)

            plotTwoLineGraph(dataRail.stats_df['temp1_max'], dataRail.stats_df['temp2_max'], 0.5)
            plotTwoLineGraph(dataRail.stats_df['temp1_mean'], dataRail.stats_df['temp2_mean'], 1)
            plotTwoLineGraph(dataRail.stats_df['temp1_min'], dataRail.stats_df['temp2_min'], 0.5)

            # Next we alight the x-axis
            plt.tick_params(axis='x',labelsize='small', rotation=45)
            tick_positions = dataRail.stats_df.index.values[::2]
            plt.set_xticks(tick_positions)
            plt.set_xticklabels([pd.to_datetime(tick).strftime('%d-%m') for tick in tick_positions], rotation=45)

            for l in plt.legend().legend_handles: l.set_alpha(1)
            plt.legend(['Ambient', 'Nest'])


        elif dataRail.graphType == "change":                                        # Plots the Rate of Change graph
            '''
            #Plot the report limit lines
            plt.plot(pd.Series(data=REPORT_THRESHOLD, index=df.index.values), color='black')
            plt.plot(pd.Series(data=-REPORT_THRESHOLD, index=df.index.values), color='black')
            '''
            # Plot the rate of change data
            plt.plot(dataRail.df['datetime'], dataRail.rate_of_change_df, color='tab:green',
                     linewidth=0.9, linestyle='-')

            plt.tick_params(axis='x',labelsize='small', rotation=45)
            tick_positions = dataRail.df['datetime'][::24 * 12]
            plt.set_xticks(tick_positions)
            plt.set_xticklabels([pd.to_datetime(tick).strftime('%d-%m') for tick in tick_positions], rotation=45)


        else:                                                                       # Plot the all other graph types
            plt.plot(dataRail.x, dataRail.y_1, color='tab:blue',
                     linewidth=0.9, linestyle='-')
            plt.plot(dataRail.x, dataRail.y_2, color='tab:red',
                     linewidth=0.9, linestyle='-')

        # Set the x and the y axis names as per the dataRail
        plt.set_ylabel(dataRail.yAxisName, size=12)
        plt.set_xlabel(dataRail.xAxisName, size=12)
        plt.set_title(dataRail.graphTitle)
        if dataRail.grid: plt.grid()    # Plot the Grid if required
        fig.tight_layout()
        # Redraw the graph
        fig_canvas.draw()

# This is the routine that we run when the "load" object is pressed
# Remember, the load buttons below need the following command
# lambda: select_path('ambient_entry')
def select_path(outputObject):
    output_path = tk.filedialog.askopenfile(mode='r', filetypes=(('csv files', '*.csv'), ('All files', '*.*')))
    if outputObject == "ambient_entry":
        ambient_entry.delete(0, tk.END)
        ambient_entry.insert(0, output_path.name)
    elif outputObject == "nest_entry":
        nest_entry.delete(0, tk.END)
        nest_entry.insert(0, output_path.name)


window.title("Curlew Explorer")

window.geometry("1080x640")
window.configure(bg = "#F3EDE5")


canvas = Canvas(
    window,
    bg = "#F3EDE5",
    height = 640,
    width = 1080,
    bd = 0,
    highlightthickness = 0,
    relief = "ridge"
)

canvas.place(x = 0, y = 0)
image_image_1 = PhotoImage(
    file=relative_to_assets("image_1.png"))
image_1 = canvas.create_image(
    540.0,
    320.0,
    image=image_image_1
)

entry_image_1 = PhotoImage(
    file=relative_to_assets("ambient_entry.png"))
entry_bg_1 = canvas.create_image(
    555.5,
    88.5,
    image=entry_image_1
)
ambient_entry = Entry(
    bd=0,
    bg="#D9D9D9",
    fg="#000716",
    highlightthickness=0
)
ambient_entry.place(
    x=57.0,
    y=79.0,
    width=997.0,
    height=17.0
)

canvas.create_text(
    57.0,
    61.0,
    anchor="nw",
    text="Ambient Temperature File",
    fill="#000000",
    font=("Inter", 14 * -1)
)

canvas.create_text(
    810.0,
    166.0,
    anchor="nw",
    text="Data Displays",
    fill="#000000",
    font=("Inter", 14 * -1)
)

canvas.create_text(
    803.0,
    316.0,
    anchor="nw",
    text="Report Displays",
    fill="#000000",
    font=("Inter", 14 * -1)
)

entry_image_2 = PhotoImage(
    file=relative_to_assets("nest_entry.png"))
entry_bg_2 = canvas.create_image(
    555.5,
    38.5,
    image=entry_image_2
)
nest_entry = Entry(
    bd=0,
    bg="#D9D9D9",
    fg="#000716",
    highlightthickness=0
)
nest_entry.place(
    x=57.0,
    y=29.0,
    width=997.0,
    height=17.0
)

canvas.create_text(
    57.0,
    11.0,
    anchor="nw",
    text="Nest Temperature File",
    fill="#000000",
    font=("Inter", 14 * -1)
)

button_image_1 = PhotoImage(
    file=relative_to_assets("button_1.png"))
button_1 = Button(
    image=button_image_1,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: select_path('nest_entry'),
    relief="flat"
)
button_1.place(
    x=13.0,
    y=11.0,
    width=40.0,
    height=40.0
)

button_image_hover_1 = PhotoImage(
    file=relative_to_assets("button_hover_1.png"))

def button_1_hover(e):
    button_1.config(
        image=button_image_hover_1
    )
def button_1_leave(e):
    button_1.config(
        image=button_image_1
    )

button_1.bind('<Enter>', button_1_hover)
button_1.bind('<Leave>', button_1_leave)


button_image_2 = PhotoImage(
    file=relative_to_assets("button_2.png"))
button_2 = Button(
    image=button_image_2,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: select_path('ambient_entry'),
    relief="flat"
)
button_2.place(
    x=13.0,
    y=61.0,
    width=40.0,
    height=40.0
)

button_image_hover_2 = PhotoImage(
    file=relative_to_assets("button_hover_2.png"))

def button_2_hover(e):
    button_2.config(
        image=button_image_hover_2
    )
def button_2_leave(e):
    button_2.config(
        image=button_image_2
    )

button_2.bind('<Enter>', button_2_hover)
button_2.bind('<Leave>', button_2_leave)


image_image_2 = PhotoImage(
    file=relative_to_assets("image_2.png"))
image_2 = canvas.create_image(
    317.0,
    372.0,
    image=image_image_2
)

canvas.create_rectangle(
    700.0,
    517.0,
    997.0,
    541.0,
    fill="#D9D9D9",
    outline="")

button_image_3 = PhotoImage(
    file=relative_to_assets("button_3.png"))
button_3 = Button(
    image=button_image_3,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: guiButtonPress(3),
    relief="flat"
)
button_3.place(
    x=1003.0,
    y=516.0,
    width=24.0,
    height=24.0
)

button_image_hover_3 = PhotoImage(
    file=relative_to_assets("button_hover_3.png"))

def button_3_hover(e):
    button_3.config(
        image=button_image_hover_3
    )
def button_3_leave(e):
    button_3.config(
        image=button_image_3
    )

button_3.bind('<Enter>', button_3_hover)
button_3.bind('<Leave>', button_3_leave)


button_image_4 = PhotoImage(
    file=relative_to_assets("button_4.png"))
button_4 = Button(
    image=button_image_4,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: guiButtonPress(4),
    relief="flat"
)
button_4.place(
    x=1033.0,
    y=516.0,
    width=24.0,
    height=24.0
)

button_image_hover_4 = PhotoImage(
    file=relative_to_assets("button_hover_4.png"))

def button_4_hover(e):
    button_4.config(
        image=button_image_hover_4
    )
def button_4_leave(e):
    button_4.config(
        image=button_image_4
    )

button_4.bind('<Enter>', button_4_hover)
button_4.bind('<Leave>', button_4_leave)


button_image_5 = PhotoImage(
    file=relative_to_assets("button_5.png"))
button_5 = Button(
    image=button_image_5,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: guiButtonPress(5),
    relief="flat"
)
button_5.place(
    x=668.0,
    y=517.0,
    width=24.0,
    height=24.0
)

button_image_hover_5 = PhotoImage(
    file=relative_to_assets("button_hover_5.png"))

def button_5_hover(e):
    button_5.config(
        image=button_image_hover_5
    )
def button_5_leave(e):
    button_5.config(
        image=button_image_5
    )

button_5.bind('<Enter>', button_5_hover)
button_5.bind('<Leave>', button_5_leave)


button_image_6 = PhotoImage(
    file=relative_to_assets("button_6.png"))
button_6 = Button(
    image=button_image_6,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: guiButtonPress(6),
    relief="flat"
)
button_6.place(
    x=1030.0,
    y=51.0,
    width=24.0,
    height=24.0
)

button_image_hover_6 = PhotoImage(
    file=relative_to_assets("button_hover_6.png"))

def button_6_hover(e):
    button_6.config(
        image=button_image_hover_6
    )
def button_6_leave(e):
    button_6.config(
        image=button_image_6
    )

button_6.bind('<Enter>', button_6_hover)
button_6.bind('<Leave>', button_6_leave)


button_image_7 = PhotoImage(
    file=relative_to_assets("button_7.png"))
button_7 = Button(
    image=button_image_7,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: guiButtonPress(7),
    relief="flat"
)
button_7.place(
    x=638.0,
    y=516.0,
    width=24.0,
    height=24.0
)

button_image_hover_7 = PhotoImage(
    file=relative_to_assets("button_hover_7.png"))

def button_7_hover(e):
    button_7.config(
        image=button_image_hover_7
    )
def button_7_leave(e):
    button_7.config(
        image=button_image_7
    )

button_7.bind('<Enter>', button_7_hover)
button_7.bind('<Leave>', button_7_leave)


button_image_8 = PhotoImage(
    file=relative_to_assets("button_8.png"))
button_8 = Button(
    image=button_image_8,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: guiButtonPress(8),
    relief="flat"
)
button_8.place(
    x=657.0,
    y=202.0,
    width=108.0,
    height=24.0
)

button_image_hover_8 = PhotoImage(
    file=relative_to_assets("button_hover_8.png"))

def button_8_hover(e):
    button_8.config(
        image=button_image_hover_8
    )
def button_8_leave(e):
    button_8.config(
        image=button_image_8
    )

button_8.bind('<Enter>', button_8_hover)
button_8.bind('<Leave>', button_8_leave)


button_image_9 = PhotoImage(
    file=relative_to_assets("button_9.png"))
button_9 = Button(
    image=button_image_9,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: guiButtonPress(9),
    relief="flat"
)
button_9.place(
    x=662.0,
    y=352.0,
    width=108.0,
    height=24.0
)

button_image_hover_9 = PhotoImage(
    file=relative_to_assets("button_hover_9.png"))

def button_9_hover(e):
    button_9.config(
        image=button_image_hover_9
    )
def button_9_leave(e):
    button_9.config(
        image=button_image_9
    )

button_9.bind('<Enter>', button_9_hover)
button_9.bind('<Leave>', button_9_leave)


button_image_10 = PhotoImage(
    file=relative_to_assets("button_10.png"))
button_10 = Button(
    image=button_image_10,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: guiButtonPress(10),
    relief="flat"
)
button_10.place(
    x=946.0,
    y=202.0,
    width=108.0,
    height=24.0
)

button_image_hover_10 = PhotoImage(
    file=relative_to_assets("button_hover_10.png"))

def button_10_hover(e):
    button_10.config(
        image=button_image_hover_10
    )
def button_10_leave(e):
    button_10.config(
        image=button_image_10
    )

button_10.bind('<Enter>', button_10_hover)
button_10.bind('<Leave>', button_10_leave)


button_image_11 = PhotoImage(
    file=relative_to_assets("button_11.png"))
button_11 = Button(
    image=button_image_11,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: guiButtonPress(11),
    relief="flat"
)
button_11.place(
    x=946.0,
    y=113.0,
    width=108.0,
    height=24.0
)

button_image_hover_11 = PhotoImage(
    file=relative_to_assets("button_hover_11.png"))

def button_11_hover(e):
    button_11.config(
        image=button_image_hover_11
    )
def button_11_leave(e):
    button_11.config(
        image=button_image_11
    )

button_11.bind('<Enter>', button_11_hover)
button_11.bind('<Leave>', button_11_leave)


button_image_12 = PhotoImage(
    file=relative_to_assets("button_12.png"))
button_12 = Button(
    image=button_image_12,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: guiButtonPress(12),
    relief="flat"
)
button_12.place(
    x=801.0,
    y=251.0,
    width=108.0,
    height=24.0
)

button_image_hover_12 = PhotoImage(
    file=relative_to_assets("button_hover_12.png"))

def button_12_hover(e):
    button_12.config(
        image=button_image_hover_12
    )
def button_12_leave(e):
    button_12.config(
        image=button_image_12
    )

button_12.bind('<Enter>', button_12_hover)
button_12.bind('<Leave>', button_12_leave)


button_image_13 = PhotoImage(
    file=relative_to_assets("button_13.png"))
button_13 = Button(
    image=button_image_13,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: guiButtonPress(13),
    relief="flat"
)
button_13.place(
    x=801.0,
    y=202.0,
    width=108.0,
    height=24.0
)

button_image_hover_13 = PhotoImage(
    file=relative_to_assets("button_hover_13.png"))

def button_13_hover(e):
    button_13.config(
        image=button_image_hover_13
    )
def button_13_leave(e):
    button_13.config(
        image=button_image_13
    )

button_13.bind('<Enter>', button_13_hover)
button_13.bind('<Leave>', button_13_leave)


button_image_14 = PhotoImage(
    file=relative_to_assets("button_14.png"))
button_14 = Button(
    image=button_image_14,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: guiButtonPress(14),
    relief="flat"
)
button_14.place(
    x=1011.0,
    y=577.0,
    width=50.0,
    height=50.0
)

button_image_hover_14 = PhotoImage(
    file=relative_to_assets("button_hover_14.png"))

def button_14_hover(e):
    button_14.config(
        image=button_image_hover_14
    )
def button_14_leave(e):
    button_14.config(
        image=button_image_14
    )

button_14.bind('<Enter>', button_14_hover)
button_14.bind('<Leave>', button_14_leave)


button_image_15 = PhotoImage(
    file=relative_to_assets("button_15.png"))
button_15 = Button(
    image=button_image_15,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: guiButtonPress(15),
    relief="flat"
)
button_15.place(
    x=638.0,
    y=476.0,
    width=24.0,
    height=24.0
)

button_image_hover_15 = PhotoImage(
    file=relative_to_assets("button_hover_15.png"))

def button_15_hover(e):
    button_15.config(
        image=button_image_hover_15
    )
def button_15_leave(e):
    button_15.config(
        image=button_image_15
    )

button_15.bind('<Enter>', button_15_hover)
button_15.bind('<Leave>', button_15_leave)


button_image_16 = PhotoImage(
    file=relative_to_assets("button_15.png"))
button_16 = Button(
    image=button_image_16,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: guiButtonPress(16),
    relief="flat"
)
button_16.place(
    x=718.0,
    y=476.0,
    width=24.0,
    height=24.0
)

button_image_hover_16 = PhotoImage(
    file=relative_to_assets("button_hover_15.png"))

def button_16_hover(e):
    button_16.config(
        image=button_image_hover_15
    )
def button_16_leave(e):
    button_16.config(
        image=button_image_15
    )

button_16.bind('<Enter>', button_16_hover)
button_16.bind('<Leave>', button_16_leave)


canvas.create_text(
    640.0,
    479.0,
    anchor="nw",
    text="X",
    fill="#000000",
    font=("Inter Bold", 14 * -1)
)

canvas.create_text(
    780.0,
    615.0,
    anchor="nw",
    text=f"Version {VERSION}",
    fill="#000000",
    font=("Inter", 12 * -1)
)

canvas.create_text(
    669.0,
    480.0,
    anchor="nw",
    text="Grid",
    fill="#000000",
    font=("Inter", 14 * -1)
)

canvas.create_text(
    749.0,
    480.0,
    anchor="nw",
    text="Smoothing",
    fill="#000000",
    font=("Inter", 14 * -1)
)

canvas.create_rectangle(
    635.0,
    153.0,
    1061.0,
    154.0,
    fill="#000000",
    outline="")

canvas.create_rectangle(
    635.0,
    299.0,
    1061.0,
    300.0,
    fill="#000000",
    outline="")

canvas.create_rectangle(
    635.0,
    562.0,
    1061.0,
    563.0,
    fill="#000000",
    outline="")

entry_image_3 = PhotoImage(
    file=relative_to_assets("entry_3.png"))
entry_bg_3 = canvas.create_image(
    1030.0,
    488.0,
    image=entry_image_3
)
entry_3 = Entry(
    bd=0,
    bg="#D9D9D9",
    fg="#000716",
    highlightthickness=0
)
entry_3.place(
    x=1003.0,
    y=476.0,
    width=54.0,
    height=22.0
)
# Prepopulate the paths
ambient_entry.insert(0, "Select ambient temperature CSV...")
nest_entry.insert(0, "Select nest temperature CSV...")

# Draw the Graph so we are ready to go for next time
fig = Figure()
cid = fig.canvas.mpl_connect('button_press_event', mouse_event) # Resister for mouse events on the graph
fig_canvas = FigureCanvasTkAgg(fig, master=window)
fig_canvas.get_tk_widget().place(x=17, y=117, width=600, height=510)

window.deiconify()

splash.update()
splash.destroy()

window.resizable(False, False)
window.mainloop()