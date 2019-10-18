



import matplotlib.pyplot as plt
import pandas as pd

import stats_aggregator as sAgg


def initSubPlots(label, experimentParams, numberOfRuns):
    #plt.figure("queuelength_simulations")
    fig, axes = plt.subplots(nrows=len(experimentParams), ncols=numberOfRuns, figsize=(12, 8), sharex=True, sharey=True)
    plt.setp(axes.flat, xlabel='step', ylabel='max length')
    for ax in axes.flat:
        ax.label_outer()
    pad = 5 # in points

    for i, ax in zip(range(0, numberOfRuns), axes[0]):
        ax.annotate(i, xy=(0.5, 1), xytext=(0, pad),
                    xycoords='axes fraction', textcoords='offset points',
                    size='large', ha='center', va='baseline')

    for ax, e in zip(axes[:,0], experimentParams):
        ax.annotate(e['prefix'], xy=(0, 0.5), xytext=(-ax.yaxis.labelpad - pad, 0),
                    xycoords=ax.yaxis.label, textcoords='offset points',
                    size='large', ha='right', va='center')
    return fig, axes

def readResults(prefix, statistics, numberOfRuns):
    results = []
    for n in range(0, numberOfRuns):
        r = {}
        for s in statistics:
            df = pd.read_csv(f"output/{prefix}_{n}_{s}.csv")
            r[s] = df
        results.append(r)
    return results

def describe(results, filePrefix, column):
    print(f"\n==== Describe {filePrefix} - {column} ====")
    dfAll = pd.concat([r[filePrefix] for r in results], ignore_index=True)
    dfAll = sAgg.aggregate(dfAll, {column: 'mean'})
    print(dfAll[column].describe())

def createPlot(label, experimentParams, numberOfRuns, file_prefixes, y_columns, kinds, aggregateDFsBy = None, groupByParams = None, groupRunsColumn = None, groupRunsFunc = None, groupRunsFilePrefix = None):
    columnNumber = numberOfRuns
    if groupRunsFilePrefix is not None: columnNumber += 1
    fig, axes = initSubPlots(label, experimentParams, columnNumber)

    r = 0
    for e in experimentParams:
        c = 0
        for er in e['results']:
            #ax = fig.add_subplot(len(experimentParams), columnNumber, (r * columnNumber) + c + 1)
            ax = axes[r, c]
            dfs = []
            for f in file_prefixes:
                dfs.append(er[f])
            if (aggregateDFsBy is not None):
                dfAgg = sAgg.aggregateDataframes(dfs, aggregateDFsBy)
            else:
                dfAgg = dfs[0]
            if (groupByParams is not None):
                dfAgg = sAgg.aggregate(dfAgg, groupByParams)
            sAgg.plot(dfAgg, 'step', y_columns, kinds, ax)
            c += 1
        if (groupRunsFilePrefix is not None):
            dfAll = pd.concat([res[groupRunsFilePrefix] for res in e['results']], ignore_index=True)
            dfAll = sAgg.aggregate(dfAll, {groupRunsColumn: groupRunsFunc})
            #ax = fig.add_subplot(len(experimentParams), columnNumber, (r * columnNumber) + c + 1)
            ax = axes[r, c]
            sAgg.plot(dfAll, 'step', [groupRunsColumn], [sAgg.PLOT_KIND_LINE], ax)
        r += 1

    fig.tight_layout()
    # tight_layout doesn't take these labels into account. We'll need
    # to make some room. These numbers are are manually tweaked.
    # You could automatically calculate them, but it's a pain.
    fig.subplots_adjust(left=0.15, top=0.95)
    fig.savefig(f"out_plots/{label}.png")
    #plt.show()

experimentParams = [{'prefix': 'th2qr1', 'configFile': 'configs/fpvpl_throughput2_queueratio1.cfg'},
                    #{'prefix': 'th1qr1', 'configFile': 'configs/fpvpl_throughput1_queueratio1.cfg'},
                    {'prefix': 'th1qr2', 'configFile': 'configs/fpvpl_throughput1_queueratio2.cfg'}]
numberOfRuns = 2



stats_sc = 'state_change'
stats_ml = 'max_length'
stats_tt = 'travel_time'
col_sc = 'new_state'
col_ml = 'max_length'
col_tt = 'ttime'
label = 'queuelength_simulations'
file_prefixes = [stats_sc, stats_ml]
aggregateDFsBy = ['step']
y_columns = [col_sc, col_ml]
kinds = [sAgg.PLOT_KIND_SCATTER, sAgg.PLOT_KIND_LINE]

for e in experimentParams:
    e['results'] = readResults(e['prefix'], [stats_sc, stats_ml, stats_tt], numberOfRuns)

createPlot(label, experimentParams, numberOfRuns, file_prefixes, y_columns, kinds, aggregateDFsBy=aggregateDFsBy,
            groupRunsColumn = col_ml, groupRunsFunc = 'mean', groupRunsFilePrefix = stats_ml)

createPlot("mean_travel_time", experimentParams, numberOfRuns, [stats_tt], [col_tt], [sAgg.PLOT_KIND_LINE], groupByParams = {col_tt : 'mean'},
            groupRunsColumn = col_tt, groupRunsFunc = 'mean', groupRunsFilePrefix = stats_tt)

for e in experimentParams:
    describe(e['results'], stats_ml, col_ml)

for e in experimentParams:
    describe(e['results'], stats_tt, col_tt)
