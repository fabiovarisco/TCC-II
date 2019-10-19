

from stats_plotter import *

experimentParams = [{'prefix': 'th2qr1', 'configFile': 'configs/fpvpl_throughput2_queueratio1.cfg'},
                    {'prefix': 'th1qr1', 'configFile': 'configs/fpvpl_throughput1_queueratio1.cfg'},
                    {'prefix': 'th1qr2', 'configFile': 'configs/fpvpl_throughput1_queueratio2.cfg'}]
numberOfRuns = 5



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

e = experimentParams[0]
e['results'] = readResults(e['prefix'], [stats_tt], 1)
#print(e['results'])
df_tt = e['results'][0][stats_tt]

print(df_tt.head())

df_tt['disc_step'] = (df_tt['step'] / 30).round(0)

print(df_tt.head(60))
