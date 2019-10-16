



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


experimentParams = [{'prefix': 'th2qr1', 'configFile': 'configs/fpvpl_throughput2_queueratio1.cfg'},
                    #{'prefix': 'th1qr1', 'configFile': 'configs/fpvpl_throughput1_queueratio1.cfg'},
                    {'prefix': 'th1qr2', 'configFile': 'configs/fpvpl_throughput1_queueratio2.cfg'}]
numberOfRuns = 2

stats_sc = 'state_change'
stats_wt = 'wtime'


fig = initSubPlots('queuelength_simulations', experimentParams, numberOfRuns)

for e in experimentParams:
    e['results'] = readResults(e['prefix'], [stats_sc, stats_wt], numberOfRuns)

r = 0
for e in experimentParams:
    c = 0
    #dfs_ql = []
    for er in e['results']:
        ax = fig.add_subplot(len(experimentParams), numberOfRuns, (r * numberOfRuns) + c + 1)
        df_ql = er[stats_wt]
        df_sc = er[stats_sc]
        dfs = sAgg.aggregateDataframes([df_ql, df_sc], ['step'])
        sAgg.plot(dfs, 'step', ['new_state', 'max_length'], ['scatter', 'line'], ax)
        c += 1
    r += 1

fig.tight_layout()
# tight_layout doesn't take these labels into account. We'll need
# to make some room. These numbers are are manually tweaked.
# You could automatically calculate them, but it's a pain.
fig.subplots_adjust(left=0.15, top=0.95)
fig.savefig("out_plots/queue_length_simulations.png")
#plt.show()
