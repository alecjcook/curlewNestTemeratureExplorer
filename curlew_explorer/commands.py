from enum import IntEnum

from curlew_explorer import views
from curlew_explorer.data_loader import load_files


class Action(IntEnum):
    NEXT_DAY = 3
    LAST_DAY = 4
    PREVIOUS_DAY = 5
    FLIP_FILES = 6
    FIRST_DAY = 7
    SHOW_ALL = 8
    SHOW_CHANGE = 9
    SHOW_DAILY = 10
    LOAD_FILES = 11
    SHOW_INDIVIDUAL = 12
    SHOW_COMBINED = 13
    SHOW_STATISTICS = 14
    TOGGLE_GRID = 15
    TOGGLE_SMOOTHING = 16
    GRAPH_CLICK = 99


def flip_files(data_rail):
    data_rail.filename1, data_rail.filename2 = data_rail.filename2, data_rail.filename1
    return load_files(data_rail)


def button_press(button_number, data_rail):
    print(f"Button {button_number} pressed")

    try:
        action = Action(button_number)
    except ValueError:
        return data_rail

    handlers = {
        Action.LOAD_FILES: load_files,
        Action.SHOW_ALL: views.show_all,
        Action.SHOW_DAILY: views.show_daily_individual,
        Action.SHOW_INDIVIDUAL: views.show_daily_individual,
        Action.SHOW_COMBINED: views.show_daily_combined,
        Action.SHOW_STATISTICS: views.show_statistics,
        Action.SHOW_CHANGE: views.show_change,
        Action.NEXT_DAY: views.increment_day,
        Action.PREVIOUS_DAY: views.decrement_day,
        Action.FIRST_DAY: views.rewind_day,
        Action.LAST_DAY: views.fastforward_day,
        Action.FLIP_FILES: flip_files,
        Action.TOGGLE_GRID: views.flip_grid,
        Action.TOGGLE_SMOOTHING: views.flip_smoothed,
        Action.GRAPH_CLICK: views.mouse_click,
    }
    return handlers[action](data_rail)

