

import matplotlib.pyplot as plt
import pandas as pd
import copy
import os
import numpy as np
import stats_aggregator as sAgg
import stats_plotter as sPlotter

def readFile(folder, prefix, stats_label, fromRun = 0, toRun = 0):
    results = []
    for n in range(fromRun, toRun):
        df = pd.read_csv(f"output/{folder}/{prefix}_{n}_{stats_label}.csv")
        results.append(df)
    return results

def readFiles(folder, params, stats_label, fromRun = 0, toRun = 0):
    for p in params:
        p['results'] = readFile(folder, p['prefix'], stats_label, fromRun, toRun)
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

def createSinglePlotAveragesOnly(folder, label, experimentParams, y_column, title, aggFunc = 'mean', discretizeStepBy = None, input_ax = None, start_at = 0, x_column = 'start_at_step'):

    base_column = x_column
    if (discretizeStepBy is not None):
        base_column = 'disc_step'
        result = sPlotter.discretizeStep(result, discretizeStepBy, base_column)

    result = None
    y_columns = []
    if (input_ax is None):
        fig = plt.figure(label)
        fig.suptitle(title, fontsize=16)
        ax = plt.subplot(111)
    else:
        print('Reusing ax')
        ax = input_ax

    for i, e in enumerate(experimentParams):
        result = e['results'][0]
        ax.plot(result[base_column], result[y_column], color=sPlotter.PLOT_COLORS[i % len(sPlotter.PLOT_COLORS)], label=e['prefix'])

    print(result.head())
    print(y_columns)

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

    plt.savefig(f"output/{folder}/stats/plot_{label}_single.png")

    return ax


def generateStatistics(folder, experimentParams, numberOfRuns, label, col, input_ax = None, x_column = 'step'):
    #createPlot(folder, col, experimentParams, numberOfRuns, [col], [sAgg.PLOT_KIND_LINE], aggregateDFsBy = ['step'],
    #              groupRunsColumn = col, groupRunsFunc = 'mean', discretizeStepBy = 600)

    if not os.path.exists(f"./output/{folder}/stats/"):
        os.makedirs(f"./output/{folder}/stats/")

    writeTableMinMaxMeanStd(experimentParams, f"./output/{folder}/stats/full_stats_{col}_10.csv", col, numberOfRuns)

    return createSinglePlotAveragesOnly(folder, f"{col}_avg_10", experimentParams, col, label, discretizeStepBy = None, input_ax = input_ax, start_at = 0, x_column = x_column)


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

    experimentPrefix = 'exp21_rf_20p'
    experimentPrefix40p = 'exp21_rf_40p'
    experimentPrefix60p = 'exp21_rf_60p'
    experimentPrefix80p = 'exp21_rf_80p'
    experimentParams = [
        {'prefix': 'ql_', 'configFile': 'configs/single_basic_qlearning_avg_queue_length.cfg'},
        {'prefix': 'veh_n_', 'configFile': 'configs/single_basic_qlearning_avg_vehicle_number.cfg'},
        {'prefix': 'delay_', 'configFile': 'configs/single_basic_qlearning_delay.cfg'},
        {'prefix': 'throughput_', 'configFile': 'configs/single_basic_qlearning_throughput.cfg'},
        {'prefix': 'delay_prq_', 'configFile': 'configs/single_basic_qlearning_delay_res_queue_penalty.cfg'},
        {'prefix': 'delay_pwtl_', 'configFile': 'configs/single_basic_qlearning_delay_wasted_time_penalty_log.cfg'},
        {'prefix': 'act_throughput_mqr_', 'configFile': 'configs/single_basic_qlearning_act_throughput_mqr.cfg'},
        {'prefix': 'veh_n_pwtl_', 'configFile': 'configs/single_basic_qlearning_veh_n_wasted_time_penalty_log.cfg'},
        {'prefix': 'throughput_pwtl_', 'configFile': 'configs/single_basic_qlearning_throughput_wasted_time_penalty_log.cfg'}
    ]
    numberOfRuns = 10

    stats_cycle = 'cycle_time'
    stats_stage = 'stage_time'

    experimentParams20p = readFiles(experimentPrefix, copy.deepcopy(experimentParams), stats_stage, fromRun = 0, toRun = 10)
    experimentParams40p = readFiles(experimentPrefix40p, copy.deepcopy(experimentParams), stats_stage, fromRun = 0, toRun = 10)
    experimentParams60p = readFiles(experimentPrefix60p, copy.deepcopy(experimentParams), stats_stage, fromRun = 0, toRun = 10)
    experimentParams80p = readFiles(experimentPrefix80p, copy.deepcopy(experimentParams), stats_stage, fromRun = 0, toRun = 10)

    col_depart_delay = 'departDelay'
    col_duration = 'duration'
    col_waiting_time = 'waitingTime'
    col_waiting_count = 'waitingCount'
    col_time_loss = 'timeLoss'

    col_cycle = 'cycle_time'
    col_stage = 'stage_time'
    col_wasted_time = 'time_beyond_queue_clearance'

    ax = generateStatistics(experimentPrefix, experimentParams20p, numberOfRuns, 'Wasted Time', col_wasted_time, x_column = 'step')
    ax = generateStatistics(experimentPrefix40p, experimentParams40p, numberOfRuns, 'Wasted Time', col_wasted_time, input_ax = None, x_column = 'start_at_step')
    ax = generateStatistics(experimentPrefix60p, experimentParams60p, numberOfRuns, 'Wasted Time', col_wasted_time, input_ax = None, x_column = 'start_at_step')
    generateStatistics(experimentPrefix80p, experimentParams80p, numberOfRuns, 'Wasted Time', col_wasted_time, input_ax = None, x_column = 'start_at_step')
