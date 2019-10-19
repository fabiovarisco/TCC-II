

import pandas as pd
from matplotlib import pyplot as plt

PLOT_KIND_LINE = 0
PLOT_KIND_SCATTER = 1

def aggregateDataframes(dataframes, onColumns):
    if (len(dataframes) == 0): raise Exception("No dataframes were passed.")
    df = dataframes[0]
    for i in range(1, len(dataframes)):
        df = pd.merge(df, dataframes[i], on=onColumns)
    return df

def aggregate(df, gbColumn, aggregationOptions):
    return df.groupby(gbColumn, as_index=False).agg(aggregationOptions)

def _scatter(ax, x, y):
    ax.scatter(x, y)

def _linePlot(ax, x, y):
    ax.plot(x, y)

plotter_switch = {
    PLOT_KIND_LINE: _linePlot,
    PLOT_KIND_SCATTER: _scatter
}

def plot(df, x_column, y_columns, kinds, ax = None):
    for i in range(0, len(y_columns)):
        if (ax is None):
            df.plot(kind=kinds[i], x=x_column, y=y_columns[i])
        else:
            plot_function = plotter_switch.get(kinds[i])
            plot_function(ax, df[x_column], df[y_columns[i]])

def plotAndSaveFigure(figureName, df, x_column, y_columns, kinds):
    plt.figure(figureName)
    plot(df, x_column, y_columns, kinds)
    plt.savefig(f"out_plots/{figureName}.png")
