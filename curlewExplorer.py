from curlew_explorer.analysis import (
    create_stats as createStats,
    get_data_chop_index as getDataChopIndex,
    smooth_line as smoothLine,
    time_in_seconds,
)
from curlew_explorer.commands import button_press as buttonPress
from curlew_explorer.data_loader import (
    load_files as loadFiles,
    parse_datetime_column,
)
from curlew_explorer.state import CurlewDataRailSingleton
from curlew_explorer.views import (
    decrement_day as decrementDay,
    fastforward_day as fastforwardDay,
    flip_grid as flipGrid,
    flip_smoothed as flipSmoothed,
    increment_day as incrementDay,
    mouse_click as mouseClick,
    rewind_day as rewindDay,
    show_all as showAll,
    show_change as showChange,
    show_daily_combined as showDailyCombined,
    show_daily_individual as showDailyIndividual,
    show_statistics as showStatistics,
)


def flipFiles(dataRail):
    dataRail.filename1, dataRail.filename2 = dataRail.filename2, dataRail.filename1
    return loadFiles(dataRail)

