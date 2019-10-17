



import matplotlib.pyplot as plt
import pandas as pd

from Statistics import StatisticsAggregator as sAgg


def initSubPlots(label, experimentParams, numberOfRuns):
    #plt.figure("queuelength_simulations")
    fig, axes = plt.subplots(nrows=len(experimentParams), ncols=numberOfRuns, figsize=(12, 8))
    plt.setp(axes.flat, xlabel='step', ylabel='max length')

    pad = 5 # in points

    for i, ax in zip(range(0, numberOfRuns), axes[0]):
        ax.annotate(i, xy=(0.5, 1), xytext=(0, pad),
                    xycoords='axes fraction', textcoords='offset points',
                    size='large', ha='center', va='baseline')

    for ax, e in zip(axes[:,0], experimentParams):
        ax.annotate(e['prefix'], xy=(0, 0.5), xytext=(-ax.yaxis.labelpad - pad, 0),
                    xycoords=ax.yaxis.label, textcoords='offset points',
                    size='large', ha='right', va='center')
    return fig

def readResults(prefix, statistics, numberOfRuns):
    results = []
    for n in range(0, numberOfRuns):
        r = {}
        for s in statistics:
            df = pd.read_csv(f"output/{prefix}_{n}_{s}.csv")
            r[s] = df
        results.append(r)
    return results

def createPlot(label, experimentParams, numberOfRuns, file_prefixes, y_columns, kinds, aggregateDFsBy = None, groupByParams = None, groupRunsColumn = None, groupRunsFunc = None, groupRunsFilePrefix = None):
    fig = initSubPlots(label, experimentParams, numberOfRuns)
    for e in experimentParams:
        e['results'] = readResults(e['prefix'], file_prefixes, numberOfRuns)
    r = 0
    columnNumber = numberOfRuns
    if groupRunsFilePrefix is not None: columnNumber += 1
    for e in experimentParams:
        c = 0
        for er in e['results']:
            ax = fig.add_subplot(len(experimentParams), columnNumber, (r * columnNumber) + c + 1)
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
            dfAll = pd.concat(e['results'][:,groupRunsFilePrefix], ignore_index=True)
            dfAll = sAgg.aggregate(dfAll, {groupRunsColumn: groupRunsFunc})
            ax = fig.add_subplot(len(experimentParams), columnNumber, (r * columnNumber) + c + 1)
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
stats_wt = 'wtime'
stats_tt = 'travel_time'
label = 'queuelength_simulations'
file_prefixes = [stats_sc, stats_wt]
aggregateDFsBy = ['step']
y_columns = ['new_state', 'max_length']
kinds = [sAgg.PLOT_KIND_SCATTER, sAgg.PLOT_KIND_LINE]

createPlot(label, experimentParams, numberOfRuns, file_prefixes, y_columns, kinds, aggregateDFsBy=aggregateDFsBy)
createPlot("mean_travel_time", experimentParams, numberOfRuns, [stats_tt], ['ttime'], [sAgg.PLOT_KIND_LINE], groupByParams = {'ttime' : 'mean'})
