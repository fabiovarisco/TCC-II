
from scipy.interpolate import make_interp_spline, BSpline
from scipy.interpolate import interp1d

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import copy

import stats_aggregator as sAgg
import stats_plotter as sPlotter

PLOT_COLORS = ['blue', 'orange', 'red', 'green', 'yellow', 'pink', 'black', 'magenta']

def readFile(folder, prefix, fromRun = 0, toRun = 0):
    results = []
    for n in range(fromRun, toRun):
        df = pd.read_csv(f"output/{folder}/sumo_{prefix}_{n}.csv")
        results.append(df)
    return results

def readFiles(folder, params, fromRun = 0, toRun = 0):
    for p in params:
        p['results'] = readFile(folder, p['prefix'], fromRun, toRun)
    return params

def aggregateDFs(results, base_column, groupColumn, groupFunc, discretizeStepBy = None):
    dfAll = pd.concat(results, ignore_index=True)
    if (discretizeStepBy is not None):
        dfAll = sPlotter.discretizeStep(dfAll, discretizeStepBy, base_column)
    dfAll = sAgg.aggregate(dfAll, base_column, {groupColumn: groupFunc})
    return dfAll

def writeTableMinMaxMeanStd(experimentParams, outputFile, col, numberOfRuns):
    #      ,exp0,   ,   ,   ,exp1,...,aggregated
    #prefix,mean,std,min,max,...
    header1 = ['']
    for i in range(0, numberOfRuns):
        header1.extend([f"exp{(i+1)}",'','',''])
    header1.extend(["aggregated",'','',''])
    header2 = ['prefix']
    for i in range(0, numberOfRuns + 1):
        header2.extend(['mean','std','min','max'])
    lines = [header1, header2]
    for e in experimentParams:
        line = [e['prefix']]
        for i in range(0, numberOfRuns):
            line.append(e['results'][i][col].mean())
            line.append(e['results'][i][col].std())
            line.append(e['results'][i][col].min())
            line.append(e['results'][i][col].max())
        dfAll = aggregateDFs(e['results'], 'step', col, 'mean')
        line.append(dfAll[col].mean())
        line.append(dfAll[col].std())
        line.append(dfAll[col].min())
        line.append(dfAll[col].max())
        lines.append(line)

    with open(outputFile, 'w') as f:
        for line in lines:
            print(','.join(map(str, line)), file=f)

    print(f"Successfully written statistics to {outputFile}")

def createPlot(folder, label, experimentParams, numberOfRuns, y_columns, kinds, aggregateDFsBy = None, groupRunsColumn = None, groupRunsFunc = None, discretizeStepBy = None):
    col_labels = [str(i) for i in range(0, numberOfRuns)]
    if groupRunsColumn is not None: col_labels.append('avg')
    fig, axes = sPlotter.initSubPlots(label, [e['prefix'] for e in experimentParams], col_labels, 'step', y_columns[0], size = (30, 30))

    if discretizeStepBy is not None:
        x_column = 'disc_step'
    else: x_column = 'step'
    r = 0
    for e in experimentParams:
        c = 0
        for er in e['results']:
            ax = axes[r, c]
            if (discretizeStepBy is not None):
                dfAgg = sPlotter.discretizeStep(er, discretizeStepBy, x_column)

            sAgg.plot(dfAgg, x_column, y_columns, kinds, ax)
            c += 1
        if (groupRunsColumn is not None):
            dfAll = aggregateDFs(e['results'], x_column, groupRunsColumn, groupRunsFunc, discretizeStepBy = discretizeStepBy)
            ax = axes[r, c]
            sAgg.plot(dfAll, x_column, [groupRunsColumn], [sAgg.PLOT_KIND_LINE], ax)
        r += 1

    fig.tight_layout()
    fig.subplots_adjust(left=0.15, top=0.95)
    fig.savefig(f"output/{folder}/sumo_{label}.png")

def createSinglePlotAveragesOnly(folder, label, experimentParams, y_column, title, aggFunc = 'mean', discretizeStepBy = None, input_ax = None, start_at = 0):

    result = None
    y_columns = []
    for e in experimentParams:
        dfAll = aggregateDFs(e['results'], 'step', y_column, aggFunc)
        new_y_col = f"{y_column}_{e['prefix']}"
        dfAll.rename(columns={y_column: new_y_col}, inplace=True)
        y_columns.append(new_y_col)
        if (result is None): result = dfAll
        else:  result = pd.merge(result, dfAll, on='step', sort = False)

    base_column = 'step'
    if (discretizeStepBy is not None):
        base_column = 'disc_step'
        result = sPlotter.discretizeStep(result, discretizeStepBy, base_column)

    result = sAgg.aggregate(result, base_column, {col:aggFunc for col in y_columns})

    if (input_ax is None):
        fig = plt.figure(label)
        fig.suptitle(title, fontsize=16)
        ax = plt.subplot(111)
    else:
        print('Reusing ax')
        ax = input_ax

    for i, y in enumerate(y_columns):
        ax.plot(result[base_column].iloc[start_at:], result[y].iloc[start_at:], color=PLOT_COLORS[i % len(PLOT_COLORS)], label=y)

    if (input_ax is None):
        # Shrink current axis's height by 10% on the bottom
        box = ax.get_position()
        ax.set_position([box.x0, box.y0 + box.height * 0.1,
                        box.width, box.height * 0.9])
        #ax.set_position([box.x0 + box.width * 0.3, box.y0,
        #                 box.width * 0.7, box.height])

        # Put a legend below current axis
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.075),
            fancybox=True, ncol=2, fontsize='xx-small')

    plt.savefig(f"output/{folder}/stats/sumo_full_{label}_single.png")

    return ax, fig

def plotDemand(ax, fig, output_file, discretizeBy = 600, start_at = 0):
    print(f"Start At: {start_at}")
    factor = 1800 / discretizeBy
    x = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18])
    y = np.array([10, 10, 20, 20, 40, 40, 60, 80, 100, 80, 60, 60, 40, 40, 20, 20, 20, 20])
    x = (x * factor)
    x_new = np.linspace(x.min(), x.max(), 100, endpoint=True)
    spl = make_interp_spline(x, y, k = 3)
    f2 = interp1d(x, y, kind='cubic')
    #y_smooth = spl(x_new)
    y_smooth = f2(x_new)
    ax2 = ax.twinx()
    ax2.set_ylabel('demand', color='#A9A9A9')
    ax2.plot(x_new, y_smooth, color='#A9A9A9', linestyle='--')
    #fig.tight_layout()
    # Shrink current axis's height by 10% on the bottom
    box = ax2.get_position()
    ax2.set_position([box.x0, box.y0 + box.height * 0.1,
                    box.width, box.height * 0.9])
    plt.savefig(output_file)

def generateStatistics(folder, experimentParams, numberOfRuns, label, col, input_ax = None):
    #createPlot(folder, col, experimentParams, numberOfRuns, [col], [sAgg.PLOT_KIND_LINE], aggregateDFsBy = ['step'],
    #              groupRunsColumn = col, groupRunsFunc = 'mean', discretizeStepBy = 600)


    writeTableMinMaxMeanStd(experimentParams, f"./output/{folder}/stats/sumo_full_stats_vehn_{col}.csv", col, numberOfRuns)

    ax, fig = createSinglePlotAveragesOnly(folder, f"vehn_{col}_avg", experimentParams, col, label, discretizeStepBy = 600, input_ax = input_ax, start_at = 2)
    plotDemand(ax, fig, f"output/{folder}/stats/sumo_full_vehn_{col}_single_w_demand.png", discretizeBy = 600, start_at=2)
    return ax

if __name__ == '__main__':

    experimentPrefix = 'exp23'
    experimentParams = [
        {'prefix': 'adap_vehn_', 'configFile': 'configs/single_final_qlearning_adaptative_veh_n_throughput.cfg'},
        {'prefix': 'veh_n_', 'configFile': 'configs/single_final_qlearning_avg_vehicle_number.cfg'},
        #{'prefix': 'adap_dwtp_', 'configFile': 'configs/single_final_qlearning_adaptative_delay_throughput.cfg'},
        #{'prefix': 'dwtp_', 'configFile': 'configs/single_final_qlearning_delay_wasted_time_penalty_log.cfg'},
        {'prefix': 'thp_', 'configFile': 'configs/single_final_qlearning_throughput.cfg'},
        {'prefix': 'fxm_', 'configFile': 'configs/single_final_fixed_time.cfg'},
    ]
    numberOfRuns = 10

    experimentPrefix = 'exp25'
    experimentParams = [{'prefix': 'adap_vehn_', 'configFile': 'configs/single_final_qlearning_adaptative_veh_n_throughput.cfg'},
                {'prefix': 'veh_n_', 'configFile': 'configs/single_final_qlearning_avg_vehicle_number.cfg'},
                {'prefix': 'thp_', 'configFile': 'configs/single_final_qlearning_throughput.cfg'}]
    
    numberOfRuns = 25

    experimentParams = readFiles(experimentPrefix, copy.deepcopy(experimentParams), fromRun = 50, toRun = 75)

    col_depart_delay = 'departDelay'
    col_duration = 'duration'
    col_waiting_time = 'waitingTime'
    col_waiting_count = 'waitingCount'
    col_time_loss = 'timeLoss'

    ax = generateStatistics(experimentPrefix, experimentParams, numberOfRuns, 'Avg Departure Delay', col_depart_delay)

    ax = generateStatistics(experimentPrefix, experimentParams, numberOfRuns, 'Avg Travel Time', col_duration)

    ax = generateStatistics(experimentPrefix, experimentParams, numberOfRuns, 'Avg Waiting Time', col_waiting_time)

    ax = generateStatistics(experimentPrefix, experimentParams, numberOfRuns, 'Avg Waiting Count', col_waiting_count)

    ax = generateStatistics(experimentPrefix, experimentParams, numberOfRuns, 'Avg Time Loss', col_time_loss)
