



import matplotlib.pyplot as plt
import pandas as pd

import stats_aggregator as sAgg

PLOT_COLORS = ['blue', 'gray', 'orange', 'red', 'green', 'black', 'yellow', 'pink', 'magenta']

def initSubPlots(label, row_labels, col_labels, x_label, y_label):
    #plt.figure("queuelength_simulations")

    fig, axes = plt.subplots(nrows=len(row_labels), ncols=len(col_labels), figsize=(12, 8), sharex=True, sharey=True)
    plt.setp(axes.flat, xlabel=x_label, ylabel=y_label)
    for ax in axes.flat:
        ax.label_outer()
    pad = 5 # in points


    if (len(row_labels) == 1):
        row_axes = []
        col_axes = axes
    else:
        row_axes = axes[:,0]
        col_axes = axes[0]

    for r, ax in zip(row_labels, row_axes):
        ax.annotate(r, xy=(0, 0.5), xytext=(-ax.yaxis.labelpad - pad, 0),
                    xycoords=ax.yaxis.label, textcoords='offset points',
                    size='large', ha='right', va='center')

    for c, ax in zip(col_labels, col_axes):
        ax.annotate(c, xy=(0.5, 1), xytext=(0, pad),
                    xycoords='axes fraction', textcoords='offset points',
                    size='large', ha='center', va='baseline')

    return fig, axes

def readResults(folder, prefix, statistics, numberOfRuns):
    results = []
    for n in range(0, numberOfRuns):
        r = {}
        for s in statistics:
            df = pd.read_csv(f"output/{folder}/{prefix}_{n}_{s}.csv")
            r[s] = df
        results.append(r)
    return results

def describe(results, filePrefix, column):
    print(f"\n==== Describe {e['experimentPrefix']} - {e['prefix']} - {column} ====")
    dfAll = pd.concat([r[filePrefix] for r in results], ignore_index=True)
    #dfAll = sAgg.aggregate(dfAll, 'step' {column: 'mean'})
    print(dfAll[column].describe())

def aggregateDFs(results, filePrefix, base_column, groupColumn, groupFunc, discretizeStepBy = None):
    dfAll = pd.concat([res[filePrefix] for res in results], ignore_index=True)
    if (discretizeStepBy is not None):
        dfAll = discretizeStep(dfAll, discretizeStepBy, base_column)
    dfAll = sAgg.aggregate(dfAll, base_column, {groupColumn: groupFunc})
    return dfAll

def discretizeStep(df, by, col_r):
    df[col_r] = (df['step'] / by).round(0)
    return df

def writeTableMinMaxMeanStd(experimentParams, filePrefix, outputFile, col, numberOfRuns):

    #      ,exp0,   ,   ,   ,exp1,...,aggregated
    #prefix,mean,std,min,max,...
    header1 = ['']
    for i in range(0, numberOfRuns):
        header1.extend([f"ext{(i+1)}",'','',''])
    header1.extend(["aggregated",'','',''])
    header2 = ['prefix']
    for i in range(0, numberOfRuns + 1):
        header2.extend(['mean','std','min','max'])
    lines = [header1, header2]
    for e in experimentParams:
        line = [e['prefix']]
        for i in range(0, numberOfRuns):
            line.append(e['results'][i][filePrefix][col].mean())
            line.append(e['results'][i][filePrefix][col].std())
            line.append(e['results'][i][filePrefix][col].min())
            line.append(e['results'][i][filePrefix][col].max())
        dfAll = aggregateDFs(e['results'], filePrefix, 'step', col, 'mean')
        line.append(dfAll[col].mean())
        line.append(dfAll[col].std())
        line.append(dfAll[col].min())
        line.append(dfAll[col].max())
        lines.append(line)

    with open(outputFile, 'w') as f:
        for line in lines:
            print(','.join(map(str, line)), file=f)

    print(f"Successfully written statistics to {outputFile}")


def getMinMeanAndStd(experimentParams, filePrefix, col, func):
    minMean = 999999
    minMeanPrefix = ''
    minStd = 999999
    minStdPrefix = ''
    for e in experimentParams:
        dfAll = aggregateDFs(e['results'], filePrefix, 'step', col, func)
        mean = dfAll[col].mean()
        std = dfAll[col].std()
        if (mean < minMean):
            minMean = mean
            minMeanPrefix = f"{e['experimentPrefix']}_{e['prefix']}"
        if (std < minStd):
            minStd = std
            minStdPrefix = f"{e['experimentPrefix']}_{e['prefix']}"
    print(f'\n\n Min for {filePrefix}')
    print(f'Min Mean: {minMean}. Experiment: {minMeanPrefix}.')
    print(f'Min Std: {minStd}. Experiment: {minStdPrefix}.\n')

def createSinglePlotAveragesOnly(folder, label, experimentParams, file_prefix, y_column, title, aggFunc = 'mean', discretizeStepBy = None):

    result = None
    y_columns = []
    for e in experimentParams:
        dfAll = aggregateDFs(e['results'], file_prefix, 'step', y_column, aggFunc)
        #new_y_col = f"{y_column}_{e['experimentPrefix']}_{e['prefix']}"
        new_y_col = f"{y_column}_{e['prefix']}"
        dfAll.rename(columns={y_column: new_y_col}, inplace=True)
        y_columns.append(new_y_col)
        if (result is None): result = dfAll
        else:  result = pd.merge(result, dfAll, on='step', sort = False)

    base_column = 'step'
    if (discretizeStepBy is not None):
        base_column = 'disc_step'
        result = discretizeStep(result, discretizeStepBy, base_column)

    result = sAgg.aggregate(result, base_column, {col:aggFunc for col in y_columns})

    fig = plt.figure(label)
    fig.suptitle(title, fontsize=16)
    ax = plt.subplot(111)
    for i, y in enumerate(y_columns):
        ax.plot(result[base_column], result[y], color=PLOT_COLORS[i % len(PLOT_COLORS)], label=y)

    # Shrink current axis's height by 10% on the bottom
    box = ax.get_position()
    ax.set_position([box.x0, box.y0 + box.height * 0.25,
                     box.width, box.height * 0.75])
    #ax.set_position([box.x0 + box.width * 0.3, box.y0,
    #                 box.width * 0.7, box.height])

    # Put a legend below current axis
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.075),
          fancybox=True, ncol=2)


    plt.savefig(f"output/{folder}/{label}_single.png")

def createPlotAveragesOnly(folder, label, experimentParams, file_prefix, y_column, discretizeStepBy = None):
    fig, axes = initSubPlots(label, ['avg'], [e['prefix'] for e in experimentParams], 'step', y_column)

    if discretizeStepBy is not None:
        x_column = 'disc_step'
    else: x_column = 'step'

    c = 0
    for e in experimentParams:
        dfAll = aggregateDFs(e['results'], file_prefix, x_column, y_column, 'mean', discretizeStepBy = discretizeStepBy)
        ax = axes[c]
        sAgg.plot(dfAll, x_column, [y_column], [sAgg.PLOT_KIND_LINE], ax)
        c += 1

    fig.tight_layout()
    fig.subplots_adjust(left=0.15, top=0.95)
    fig.savefig(f"output/{folder}/{label}.png")


def createPlot(folder, label, experimentParams, numberOfRuns, file_prefixes, y_columns, kinds, aggregateDFsBy = None, groupByParams = None, groupRunsColumn = None, groupRunsFunc = None, groupRunsFilePrefix = None, discretizeStepBy = None):
    col_labels = [str(i) for i in range(0, numberOfRuns)]
    if groupRunsFilePrefix is not None: col_labels.append('avg')
    fig, axes = initSubPlots(label, [e['prefix'] for e in experimentParams], col_labels, 'step', y_columns[0])

    if discretizeStepBy is not None:
        x_column = 'disc_step'
    else: x_column = 'step'
    r = 0
    for e in experimentParams:
        c = 0
        for er in e['results']:
            ax = axes[r, c]
            dfs = []
            for f in file_prefixes:
                dfs.append(er[f])
            if (aggregateDFsBy is not None):
                dfAgg = sAgg.aggregateDataframes(dfs, aggregateDFsBy)
            else:
                dfAgg = dfs[0]
            if (discretizeStepBy is not None):
                dfAgg = discretizeStep(dfAgg, discretizeStepBy, x_column)
            if (groupByParams is not None):
                dfAgg = sAgg.aggregate(dfAgg, x_column, groupByParams)

            sAgg.plot(dfAgg, x_column, y_columns, kinds, ax)
            c += 1
        if (groupRunsFilePrefix is not None):
            dfAll = aggregateDFs(e['results'], groupRunsFilePrefix, x_column, groupRunsColumn, groupRunsFunc, discretizeStepBy = discretizeStepBy)
#            dfAll = pd.concat([res[groupRunsFilePrefix] for res in e['results']], ignore_index=True)
#            if (discretizeStepBy is not None):
#                dfAll = discretizeStep(dfAll, discretizeStepBy, x_column)
#            dfAll = sAgg.aggregate(dfAll, x_column, {groupRunsColumn: groupRunsFunc})
            #ax = fig.add_subplot(len(experimentParams), columnNumber, (r * columnNumber) + c + 1)
            ax = axes[r, c]
            sAgg.plot(dfAll, x_column, [groupRunsColumn], [sAgg.PLOT_KIND_LINE], ax)
        r += 1

    fig.tight_layout()
    # tight_layout doesn't take these labels into account. We'll need
    # to make some room. These numbers are are manually tweaked.
    # You could automatically calculate them, but it's a pain.
    fig.subplots_adjust(left=0.15, top=0.95)
    fig.savefig(f"output/{folder}/{label}.png")
    #plt.show()


if __name__ == '__main__':

    #experimentPrefix = 'hd14400stps'
    experimentPrefix = 'md14400stps'
    experimentParams = [{'prefix': f'{experimentPrefix}_th2qr1', 'configFile': 'configs/fpvpl_throughput2_queueratio1.cfg'},
                        {'prefix': f'{experimentPrefix}_th1qr1', 'configFile': 'configs/fpvpl_throughput1_queueratio1.cfg'},
                        {'prefix': f'{experimentPrefix}_th1qr2', 'configFile': 'configs/fpvpl_throughput1_queueratio2.cfg'}]
    numberOfRuns = 10
    experimentPrefix = 'deepq1_adaptive'
    #experimentParams = [{'prefix': f'{experimentPrefix}_th2qr1', 'configFile': 'configs/fpvpl_throughput2_queueratio1.cfg'},
    #                    {'prefix': f'{experimentPrefix}_th1qr1', 'configFile': 'configs/fpvpl_throughput1_queueratio1.cfg'},
    #                    {'prefix': f'{experimentPrefix}_th1qr2', 'configFile': 'configs/fpvpl_throughput1_queueratio2.cfg'}]
    experimentParams = [{'experimentPrefix': 'deepq1', 'prefix': 'exp1', 'configFile': 'configs/simple_config.cfg'},
                        {'experimentPrefix': 'deepq1_adaptive', 'prefix': 'exp1', 'configFile': 'configs/simple_config.cfg'},
                        {'experimentPrefix': 'deepq1_adaptive', 'prefix': 'steep15_inf-04', 'configFile': 'configs/simple_config.cfg'}]
    experimentPrefix = 'exp4_deepq1_adaptive'
    experimentParams = [{'experimentPrefix': 'exp4_deepq1_adaptive', 'prefix': 'rf_avg_queue_length', 'configFile': 'configs/simple_deep_avg_queue_length.cfg'},
                        {'experimentPrefix': 'exp4_deepq1_adaptive', 'prefix': 'rf_throughput', 'configFile': 'configs/simple_deep_throughput.cfg'},
                        {'experimentPrefix': 'exp4_deepq1_adaptive', 'prefix': 'rf_adaptive_lane_occup', 'configFile': 'configs/simple_deep_adaptive_lane_occupancy.cfg'}]

    experimentPrefix = 'exp8_deepq1_vehicle_delay'
    #experimentParams = [{'prefix': f'{experimentPrefix}_th2qr1', 'configFile': 'configs/fpvpl_throughput2_queueratio1.cfg'},
    #                    {'prefix': f'{experimentPrefix}_th1qr1', 'configFile': 'configs/fpvpl_throughput1_queueratio1.cfg'},
    #                    {'prefix': f'{experimentPrefix}_th1qr2', 'configFile': 'configs/fpvpl_throughput1_queueratio2.cfg'}]
    experimentParams = [{'experimentPrefix': 'exp5_deepq1_decision_point', 'prefix': 'rf_avg_veh_number', 'configFile': 'configs/simple_deep_avg_vehicle_number.cfg'},
                        {'experimentPrefix': 'exp5_deepq1_decision_point', 'prefix': 'rf_throughput', 'configFile': 'configs/simple_deep_throughput.cfg'},
                        {'experimentPrefix': 'exp8_deepq1_vehicle_delay', 'prefix': 'rf_vehicle_delay'}]

    experimentParams = [{'experimentPrefix': 'exp8_deepq1_vehicle_delay', 'prefix': 'rf_avg_veh_number', 'configFile': 'configs/simple_deep_avg_vehicle_number.cfg'},
                        {'experimentPrefix': 'exp8_deepq1_vehicle_delay', 'prefix': 'rf_throughput', 'configFile': 'configs/simple_deep_throughput.cfg'},
                        {'experimentPrefix': 'exp8_deepq1_vehicle_delay', 'prefix': 'rf_vehicle_delay', 'configFile': 'configs/simple_deep_reward_vehicle_delay.cfg'}]

    experimentPrefix = 'exp9_deepq1_rfs'
    #experimentParams = [{'prefix': f'{experimentPrefix}_th2qr1', 'configFile': 'configs/fpvpl_throughput2_queueratio1.cfg'},
    #                    {'prefix': f'{experimentPrefix}_th1qr1', 'configFile': 'configs/fpvpl_throughput1_queueratio1.cfg'},
    #                    {'prefix': f'{experimentPrefix}_th1qr2', 'configFile': 'configs/fpvpl_throughput1_queueratio2.cfg'}]
    experimentParams = [{'experimentPrefix': 'exp9_deepq1_rfs', 'prefix': 'rf_avg_queue_length', 'configFile': 'configs/simple_deep_avg_queue_length.cfg'},
                        {'experimentPrefix': 'exp9_deepq1_rfs', 'prefix': 'rf_avg_veh_number', 'configFile': 'configs/simple_deep_avg_vehicle_number.cfg'},
                        {'experimentPrefix': 'exp9_deepq1_rfs', 'prefix': 'rf_throughput', 'configFile': 'configs/simple_deep_throughput.cfg'},
                        {'experimentPrefix': 'exp9_deepq1_rfs', 'prefix': 'rf_vehicle_delay', 'configFile': 'configs/simple_deep_reward_vehicle_delay.cfg'},
                        {'experimentPrefix': 'exp9_deepq1_rfs', 'prefix': 'rf_vehicle_delay_diff', 'configFile': 'configs/simple_deep_reward_vehicle_delay_diff.cfg'}]
    experimentPrefix = 'dummy'
    experimentParams = [{'experimentPrefix': 'dummy', 'prefix': 'rf_number_stops', 'configFile': 'configs/simple_deep_number_stops.cfg'},
                        {'experimentPrefix': 'dummy', 'prefix': 'rf_number_stops_diff', 'configFile': 'configs/simple_deep_number_stops_diff.cfg'},
                        {'experimentPrefix': 'dummy', 'prefix': 'rf_vehicle_delay', 'configFile': 'configs/simple_deep_reward_vehicle_delay.cfg'}]

    experimentPrefix = 'exp10_deepq1_rfs_no_reset'
    experimentParams = [{'experimentPrefix': 'exp10_deepq1_rfs_no_reset', 'prefix': 'rf_avg_queue_length', 'configFile': 'configs/simple_deep_avg_queue_length.cfg'},
                        {'experimentPrefix': 'exp10_deepq1_rfs_no_reset', 'prefix': 'rf_avg_veh_number', 'configFile': 'configs/simple_deep_avg_vehicle_number.cfg'},
                        {'experimentPrefix': 'exp10_deepq1_rfs_no_reset', 'prefix': 'rf_throughput', 'configFile': 'configs/simple_deep_throughput.cfg'},
                        {'experimentPrefix': 'exp10_deepq1_rfs_no_reset', 'prefix': 'rf_vehicle_delay', 'configFile': 'configs/simple_deep_reward_vehicle_delay.cfg'},
                        {'experimentPrefix': 'exp10_deepq1_rfs_no_reset', 'prefix': 'rf_vehicle_delay_diff', 'configFile': 'configs/simple_deep_reward_vehicle_delay_diff.cfg'},
                        {'experimentPrefix': 'exp10_deepq1_rfs_no_reset', 'prefix': 'rf_number_stops', 'configFile': 'configs/simple_deep_number_stops.cfg'},
                        {'experimentPrefix': 'exp10_deepq1_rfs_no_reset', 'prefix': 'rf_number_stops_diff', 'configFile': 'configs/simple_deep_number_stops_diff.cfg'}]
    experimentPrefix = 'exp11_entire_day'
    experimentParams = [{'experimentPrefix': 'exp11_entire_day', 'prefix': 'rf_avg_queue_length', 'configFile': 'configs/simple_deep_avg_queue_length.cfg'},
                        {'experimentPrefix': 'exp11_entire_day', 'prefix': 'rf_avg_veh_number', 'configFile': 'configs/simple_deep_avg_vehicle_number.cfg'},
                        {'experimentPrefix': 'exp11_entire_day', 'prefix': 'rf_throughput', 'configFile': 'configs/simple_deep_throughput.cfg'},
                        {'experimentPrefix': 'exp11_entire_day', 'prefix': 'rf_vehicle_delay', 'configFile': 'configs/simple_deep_reward_vehicle_delay.cfg'},
                        {'experimentPrefix': 'exp11_entire_day', 'prefix': 'rf_vehicle_delay_diff', 'configFile': 'configs/simple_deep_reward_vehicle_delay_diff.cfg'},
                        {'experimentPrefix': 'exp11_entire_day', 'prefix': 'rf_number_stops', 'configFile': 'configs/simple_deep_number_stops.cfg'},
                        {'experimentPrefix': 'exp11_entire_day', 'prefix': 'rf_number_stops_diff', 'configFile': 'configs/simple_deep_number_stops_diff.cfg'},
                        #{'experimentPrefix': 'exp11_entire_day', 'prefix': 'webster_like', 'configFile': 'configs/simple_webster_like.cfg'},
                        {'experimentPrefix': 'exp11_entire_day', 'prefix': 'fixed_time', 'configFile': 'configs/simple_fixed_time.cfg'}]
    experimentPrefix = 'exp12_half_day'
    experimentParams = [{'experimentPrefix': 'exp12_half_day', 'prefix': 'rf_avg_queue_length', 'configFile': 'configs/simple_qlearning_avg_queue_length.cfg'},
                        {'experimentPrefix': 'exp12_half_day', 'prefix': 'rf_avg_veh_number', 'configFile': 'configs/simple_qlearning_avg_vehicle_number.cfg'}]

    experimentPrefix = 'exp12_half_day'
    experimentParams = [{'experimentPrefix': 'exp12_half_day', 'prefix': 'rf_avg_queue_length', 'configFile': 'configs/simple_qlearning_avg_queue_length.cfg'},
                        {'experimentPrefix': 'exp12_half_day', 'prefix': 'rf_avg_veh_number', 'configFile': 'configs/simple_qlearning_avg_vehicle_number.cfg'},
                        {'experimentPrefix': 'exp12_half_day', 'prefix': 'rf_throughput', 'configFile': 'configs/simple_qlearning_throughput.cfg'},
                        {'experimentPrefix': 'exp12_half_day', 'prefix': 'rf_vehicle_delay', 'configFile': 'configs/simple_qlearning_reward_vehicle_delay.cfg'},
                        {'experimentPrefix': 'exp12_half_day', 'prefix': 'rf_number_stops', 'configFile': 'configs/simple_qlearning_number_stops.cfg'},
                        {'experimentPrefix': 'exp12_half_day', 'prefix': 'rf_avg_queue_length_w_p_stps', 'configFile': 'configs/simple_qlearning_avg_queue_length_w_penalty_stops.cfg'},
                        {'experimentPrefix': 'exp12_half_day', 'prefix': 'rf_vehicle_number_w_p_stps', 'configFile': 'configs/simple_qlearning_avg_vehicle_number_w_penalty_stops.cfg'},
                        {'experimentPrefix': 'exp12_half_day', 'prefix': 'rf_veh_delay_w_p_stps', 'configFile': 'configs/simple_qlearning_veh_delay_w_penalty_stops.cfg'},
                        {'experimentPrefix': 'exp12_half_day', 'prefix': 'fixed_time', 'configFile': 'configs/simple_fixed_time.cfg'}]
    experimentPrefix = 'exp14_hyperparam_tuning'
    experimentParams = [{'experimentPrefix': 'exp14_hyperparam_tuning', 'prefix': 'rf_avg_veh_number_1e-05_0.7_0.6', 'configFile': 'configs/simple_qlearning_avg_vehicle_number.cfg'},
                        {'experimentPrefix': 'exp14_hyperparam_tuning', 'prefix': 'rf_avg_veh_number_0.0001_0.7_0.6', 'configFile': 'configs/simple_qlearning_avg_vehicle_number.cfg'},
                        {'experimentPrefix': 'exp14_hyperparam_tuning', 'prefix': 'rf_avg_veh_number_0.001_0.7_0.6', 'configFile': 'configs/simple_qlearning_avg_vehicle_number.cfg'},
                        {'experimentPrefix': 'exp14_hyperparam_tuning', 'prefix': 'rf_avg_veh_number_0.01_0.7_0.6', 'configFile': 'configs/simple_qlearning_avg_vehicle_number.cfg'},
                        {'experimentPrefix': 'exp14_hyperparam_tuning', 'prefix': 'rf_avg_veh_number_0.1_0.7_0.6', 'configFile': 'configs/simple_qlearning_avg_vehicle_number.cfg'}
    ]

    numberOfRuns = 4

    stats_sc = 'state_change'
    stats_ml = 'max_length'
    stats_tt = 'travel_time'
    stats_ql = 'queue_length'
    lane_id = 'lane_id'

    col_ql = 'queue_length'
    col_sc = 'new_state'
    col_ml = 'max_length'
    col_tt = 'ttime'
    label_ql = f'queuelength_simulations_{experimentPrefix}'
    label_tt = f"mean_travel_time_{experimentPrefix}"
    file_prefixes = [stats_sc, stats_ml]
    aggregateDFsBy = ['step']
    y_columns = [col_sc, col_ml]
    kinds = [sAgg.PLOT_KIND_SCATTER, sAgg.PLOT_KIND_LINE]

    for e in experimentParams:
        e['results'] = readResults(e['experimentPrefix'], e['prefix'], [stats_sc, stats_ml, stats_tt, stats_ql], numberOfRuns)
        df = e['results'][0][stats_ql]
        df = df.groupby(['step', 'tl_id'], as_index=False).agg({'queue_length' : 'mean'})
        e['results'][0][stats_ql] = df

    #createPlot(experimentPrefix, f"max_{label_ql}", experimentParams, numberOfRuns, [stats_ml], [col_ml], [sAgg.PLOT_KIND_LINE], aggregateDFsBy=aggregateDFsBy,
    #            groupRunsColumn = col_ml, groupRunsFunc = 'mean', groupRunsFilePrefix = stats_ml, discretizeStepBy = 600)

    #createPlot(experimentPrefix, label_tt, experimentParams, numberOfRuns, [stats_tt], [col_tt], [sAgg.PLOT_KIND_LINE], groupByParams = {col_tt : 'mean'},
    #            groupRunsColumn = col_tt, groupRunsFunc = 'mean', groupRunsFilePrefix = stats_tt, discretizeStepBy = 600)

    #createPlot(experimentPrefix, label_ql, experimentParams, numberOfRuns, [stats_ql], [col_ql], [sAgg.PLOT_KIND_LINE], groupByParams = {col_ql : 'mean'},
    #            groupRunsColumn = col_ql, groupRunsFunc = 'mean', groupRunsFilePrefix = stats_ql, discretizeStepBy = 600)

    #createPlotAveragesOnly(experimentPrefix, f"{label_ql}_avg", experimentParams, stats_ml, col_ml, discretizeStepBy = 120)
    #createPlotAveragesOnly(experimentPrefix, f"{label_tt}_avg", experimentParams, stats_tt, col_tt, discretizeStepBy = 120)

    #createSinglePlotAveragesOnly(experimentPrefix, f"single_max_{label_ql}_avg", experimentParams, stats_ml, col_ml, 'Max Queue Length', aggFunc = 'max', discretizeStepBy = 600)
    #createSinglePlotAveragesOnly(experimentPrefix, f"single_{label_tt}_avg", experimentParams, stats_tt, col_tt, 'Avg Travel Time', discretizeStepBy = 600)
    #createSinglePlotAveragesOnly(experimentPrefix, f"single_{label_ql}_avg", experimentParams, stats_ql, col_ql, 'Avg Queue Length', discretizeStepBy = 600)

    writeTableMinMaxMeanStd(experimentParams, stats_ml, f"./output/{experimentPrefix}/stats_max_{label_ql}.csv", col_ml, numberOfRuns)
    writeTableMinMaxMeanStd(experimentParams, stats_tt, f"./output/{experimentPrefix}/stats_{label_tt}.csv", col_tt, numberOfRuns)
    writeTableMinMaxMeanStd(experimentParams, stats_ql, f"./output/{experimentPrefix}/stats_{label_ql}.csv", col_ql, numberOfRuns)

    #for e in experimentParams:
    #    describe(e['results'], stats_ql, col_ql)

    #for e in experimentParams:
    #    describe(e['results'], stats_tt, col_tt)

    #getMinMeanAndStd(experimentParams, stats_ql, col_ql, 'mean')
    #getMinMeanAndStd(experimentParams, stats_tt, col_tt, 'mean')
