

import matplotlib.pyplot as plt
import pandas as pd

import stats_aggregator as sAgg
import stats_plotter as sPlotter

def readFile(folder, prefix, numberOfRuns):
    results = []
    for n in range(0, numberOfRuns):
        df = pd.read_csv(f"output/{folder}/sumo_{prefix}_{n}.csv")
        results.append(df)
    return results

def readFiles(folder, params, numberOfRuns):
    for p in params:
        p['results'] = readFile(folder, p['prefix'], numberOfRuns)
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
    fig, axes = sPlotter.initSubPlots(label, [e['prefix'] for e in experimentParams], col_labels, 'step', y_columns[0])

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

def createSinglePlotAveragesOnly(folder, label, experimentParams, y_column, title, aggFunc = 'mean', discretizeStepBy = None):

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

    fig = plt.figure(label)
    fig.suptitle(title, fontsize=16)
    ax = plt.subplot(111)
    for i, y in enumerate(y_columns):
        ax.plot(result[base_column], result[y], color=sPlotter.PLOT_COLORS[i % len(sPlotter.PLOT_COLORS)], label=y)

    # Shrink current axis's height by 10% on the bottom
    box = ax.get_position()
    ax.set_position([box.x0, box.y0 + box.height * 0.1,
                     box.width, box.height * 0.9])
    #ax.set_position([box.x0 + box.width * 0.3, box.y0,
    #                 box.width * 0.7, box.height])

    # Put a legend below current axis
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.075),
          fancybox=True, ncol=2, fontsize='xx-small')

    plt.savefig(f"output/{folder}/sumo_{label}_single.png")


def generateStatistics(folder, experimentParams, numberOfRuns, label, col):
    createPlot(folder, col, experimentParams, numberOfRuns, [col], [sAgg.PLOT_KIND_LINE], aggregateDFsBy = ['step'],
        groupRunsColumn = col, groupRunsFunc = 'mean', discretizeStepBy = 600)

    createSinglePlotAveragesOnly(folder, f"single_{col}_avg", experimentParams, col, label, discretizeStepBy = 600)

    writeTableMinMaxMeanStd(experimentParams, f"./output/{folder}/stats_{col}.csv", col, numberOfRuns)


if __name__ == '__main__':
    experimentPrefix = 'exp14_hyperparam_tuning'
    experimentParams = [{'experimentPrefix': 'exp14_hyperparam_tuning', 'prefix': 'rf_avg_veh_number_1e-05_0.7_0.6', 'configFile': 'configs/simple_qlearning_avg_vehicle_number.cfg'},
                        {'experimentPrefix': 'exp14_hyperparam_tuning', 'prefix': 'rf_avg_veh_number_0.0001_0.7_0.6', 'configFile': 'configs/simple_qlearning_avg_vehicle_number.cfg'},
                        {'experimentPrefix': 'exp14_hyperparam_tuning', 'prefix': 'rf_avg_veh_number_0.001_0.7_0.6', 'configFile': 'configs/simple_qlearning_avg_vehicle_number.cfg'},
                        {'experimentPrefix': 'exp14_hyperparam_tuning', 'prefix': 'rf_avg_veh_number_0.01_0.7_0.6', 'configFile': 'configs/simple_qlearning_avg_vehicle_number.cfg'},
                        {'experimentPrefix': 'exp14_hyperparam_tuning', 'prefix': 'rf_avg_veh_number_0.1_0.7_0.6', 'configFile': 'configs/simple_qlearning_avg_vehicle_number.cfg'}
    ]
    numberOfRuns = 4

    experimentPrefix = 'exp14_hyperparam_tuning_2'
    experimentParams = [{'experimentPrefix': 'exp14_hyperparam_tuning', 'prefix': 'rf_avg_veh_number_0.001_0.6_0.6', 'configFile': 'configs/simple_qlearning_avg_vehicle_number.cfg'},
                        {'experimentPrefix': 'exp14_hyperparam_tuning', 'prefix': 'rf_avg_veh_number_0.001_0.7_0.6', 'configFile': 'configs/simple_qlearning_avg_vehicle_number.cfg'},
                        {'experimentPrefix': 'exp14_hyperparam_tuning', 'prefix': 'rf_avg_veh_number_0.001_0.7999999999999999_0.6', 'configFile': 'configs/simple_qlearning_avg_vehicle_number.cfg'},
                        {'experimentPrefix': 'exp14_hyperparam_tuning', 'prefix': 'rf_avg_veh_number_0.001_0.8999999999999999_0.6', 'configFile': 'configs/simple_qlearning_avg_vehicle_number.cfg'},
                        {'experimentPrefix': 'exp14_hyperparam_tuning', 'prefix': 'rf_avg_veh_number_0.001_0.6_0.7', 'configFile': 'configs/simple_qlearning_avg_vehicle_number.cfg'},
                        {'experimentPrefix': 'exp14_hyperparam_tuning', 'prefix': 'rf_avg_veh_number_0.001_0.7_0.7', 'configFile': 'configs/simple_qlearning_avg_vehicle_number.cfg'},
                        {'experimentPrefix': 'exp14_hyperparam_tuning', 'prefix': 'rf_avg_veh_number_0.001_0.7999999999999999_0.7', 'configFile': 'configs/simple_qlearning_avg_vehicle_number.cfg'},
                        {'experimentPrefix': 'exp14_hyperparam_tuning', 'prefix': 'rf_avg_veh_number_0.001_0.8999999999999999_0.7', 'configFile': 'configs/simple_qlearning_avg_vehicle_number.cfg'},
                        {'experimentPrefix': 'exp14_hyperparam_tuning', 'prefix': 'rf_avg_veh_number_0.001_0.6_0.7999999999999999', 'configFile': 'configs/simple_qlearning_avg_vehicle_number.cfg'},
                        {'experimentPrefix': 'exp14_hyperparam_tuning', 'prefix': 'rf_avg_veh_number_0.001_0.7_0.7999999999999999', 'configFile': 'configs/simple_qlearning_avg_vehicle_number.cfg'}
                        #{'experimentPrefix': 'exp14_hyperparam_tuning', 'prefix': 'rf_avg_veh_number_0.001_0.7999999999999999_0.7999999999999999', 'configFile': 'configs/simple_qlearning_avg_vehicle_number.cfg'},
                        #{'experimentPrefix': 'exp14_hyperparam_tuning', 'prefix': 'rf_avg_veh_number_0.001_0.8999999999999999_0.7999999999999999', 'configFile': 'configs/simple_qlearning_avg_vehicle_number.cfg'}
    ]
    numberOfRuns = 5

    experimentParams = readFiles(experimentPrefix, experimentParams, numberOfRuns)

    col_depart_delay = 'departDelay'
    col_duration = 'duration'
    col_waiting_time = 'waitingTime'
    col_waiting_count = 'waitingCount'
    col_time_loss = 'timeLoss'

    generateStatistics(experimentPrefix, experimentParams, numberOfRuns, 'Avg Departure Delay', col_depart_delay)

    generateStatistics(experimentPrefix, experimentParams, numberOfRuns, 'Avg Travel Time', col_duration)

    generateStatistics(experimentPrefix, experimentParams, numberOfRuns, 'Avg Waiting Time', col_waiting_time)

    generateStatistics(experimentPrefix, experimentParams, numberOfRuns, 'Avg Waiting Count', col_waiting_count)

    generateStatistics(experimentPrefix, experimentParams, numberOfRuns, 'Avg Time Loss', col_time_loss)
