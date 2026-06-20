import numpy as np
import pandas as pd

from curlew_explorer.analysis import smooth_line


def _plot_scatter_with_trendline(axes, colour, x, y, label, x_smooth):
    axes.scatter(x, y, color=colour, alpha=0.03, label=label)
    z = np.polyfit(x, y, 5)
    p = np.poly1d(z)
    axes.plot(x_smooth, p(x_smooth), color=colour)


def _plot_two_line_graph(axes, data_rail, plot_one, plot_two, alpha):
    axes.plot(
        data_rail.stats_df.index.values,
        plot_one,
        color="tab:blue",
        linewidth=0.9,
        linestyle="-",
        alpha=alpha,
    )
    axes.plot(
        data_rail.stats_df.index.values,
        plot_two,
        color="tab:red",
        linewidth=0.9,
        linestyle="-",
        alpha=alpha,
    )


def update_graph(data_rail, fig, fig_canvas):
    fig.clear()
    fig_canvas.draw_idle()
    axes = fig.add_subplot(111)

    if data_rail.graphType == "none":
        return

    if data_rail.graphType == "all":
        axes.plot(
            data_rail.x,
            smooth_line(data_rail.y_1),
            color="tab:blue",
            linewidth=0.9,
            linestyle="-",
            label="Ambient",
        )
        axes.plot(
            data_rail.x,
            smooth_line(data_rail.y_2),
            color="tab:red",
            linewidth=0.9,
            linestyle="-",
            label="Nest",
        )
        axes.tick_params(axis="x", labelsize="small", rotation=45)
        tick_positions = data_rail.x.values[:: 24 * 12]
        axes.set_xticks(tick_positions)
        axes.set_xticklabels(
            [pd.to_datetime(tick).strftime("%d-%m") for tick in tick_positions],
            rotation=45,
        )
        axes.legend()

    elif data_rail.graphType == "dailyIndividual":
        if data_rail.smoothedData:
            axes.plot(
                data_rail.x,
                smooth_line(data_rail.y_1),
                color="tab:blue",
                linewidth=0.9,
                linestyle="-",
                label="Ambient",
            )
            axes.plot(
                data_rail.x,
                smooth_line(data_rail.y_2),
                color="tab:red",
                linewidth=0.9,
                linestyle="-",
                label="Nest",
            )
        else:
            axes.plot(
                data_rail.x,
                data_rail.y_1,
                color="darkblue",
                linewidth=0.9,
                linestyle="-",
                label="Ambient (raw)",
            )
            axes.plot(
                data_rail.x,
                data_rail.y_2,
                color="maroon",
                linewidth=0.9,
                linestyle="-",
                label="Nest (raw)",
            )

            upper_bound_1 = data_rail.y_1 + 0.49
            lower_bound_1 = data_rail.y_1 - 0.49
            upper_bound_2 = data_rail.y_2 + 0.49
            lower_bound_2 = data_rail.y_2 - 0.49
            axes.fill_between(
                data_rail.x,
                lower_bound_1,
                upper_bound_1,
                color="tab:blue",
                alpha=0.2,
                label="Ambient +/-0.49 C",
            )
            axes.fill_between(
                data_rail.x,
                lower_bound_2,
                upper_bound_2,
                color="tab:red",
                alpha=0.2,
                label="Nest +/-0.49 C",
            )

        axes.tick_params(axis="x", labelsize="small", rotation=45)
        tick_positions = data_rail.x.values[::6]
        axes.set_xticks(tick_positions)
        axes.set_xticklabels(
            [pd.to_datetime(tick).strftime("%H") for tick in tick_positions],
            rotation=45,
        )
        axes.legend()

    elif data_rail.graphType == "dailyCombined":
        x_smooth = np.linspace(min(data_rail.x), max(data_rail.x), 500)
        _plot_scatter_with_trendline(
            axes, "tab:blue", data_rail.x, data_rail.y_1, "Ambient", x_smooth
        )
        _plot_scatter_with_trendline(
            axes, "tab:red", data_rail.x, data_rail.y_2, "Nest", x_smooth
        )
        for legend_item in axes.legend().legend_handles:
            legend_item.set_alpha(1)

    elif data_rail.graphType == "stats":
        _plot_two_line_graph(
            axes,
            data_rail,
            data_rail.stats_df["temp1_max"],
            data_rail.stats_df["temp2_max"],
            0.5,
        )
        _plot_two_line_graph(
            axes,
            data_rail,
            data_rail.stats_df["temp1_mean"],
            data_rail.stats_df["temp2_mean"],
            1,
        )
        _plot_two_line_graph(
            axes,
            data_rail,
            data_rail.stats_df["temp1_min"],
            data_rail.stats_df["temp2_min"],
            0.5,
        )
        axes.tick_params(axis="x", labelsize="small", rotation=45)
        tick_positions = data_rail.stats_df.index.values[::2]
        axes.set_xticks(tick_positions)
        axes.set_xticklabels(
            [pd.to_datetime(tick).strftime("%d-%m") for tick in tick_positions],
            rotation=45,
        )
        axes.legend(["Ambient", "Nest"])

    elif data_rail.graphType == "change":
        axes.plot(
            data_rail.df["datetime"],
            data_rail.rate_of_change_df["change"],
            color="tab:green",
            linewidth=0.9,
            linestyle="-",
        )
        axes.tick_params(axis="x", labelsize="small", rotation=45)
        tick_positions = data_rail.df["datetime"][:: 24 * 12]
        axes.set_xticks(tick_positions)
        axes.set_xticklabels(
            [pd.to_datetime(tick).strftime("%d-%m") for tick in tick_positions],
            rotation=45,
        )

    else:
        axes.plot(data_rail.x, data_rail.y_1, color="tab:blue", linewidth=0.9)
        axes.plot(data_rail.x, data_rail.y_2, color="tab:red", linewidth=0.9)

    axes.set_ylabel(data_rail.yAxisName, size=12)
    axes.set_xlabel(data_rail.xAxisName, size=12)
    axes.set_title(data_rail.graphTitle)
    if data_rail.grid:
        axes.grid()
    fig.tight_layout()
    fig_canvas.draw()

