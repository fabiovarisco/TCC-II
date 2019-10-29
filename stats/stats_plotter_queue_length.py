import matplotlib.pyplot as plt
import pandas as pd

import stats_aggregator as sAgg
import stats_plotter as sPlot

if __name__ == '__main__':


    experimentPrefix = 'exp4_deepq1_adaptive'
    experimentParams = [{'experimentPrefix': 'exp4_deepq1_adaptive', 'prefix': 'rf_avg_queue_length', 'configFile': 'configs/simple_deep_avg_queue_length.cfg'},
                        {'experimentPrefix': 'exp4_deepq1_adaptive', 'prefix': 'rf_throughput', 'configFile': 'configs/simple_deep_throughput.cfg'}]
                        #{'experimentPrefix': 'exp4_deepq1_adaptive', 'prefix': 'rf_adaptive_lane_occup', 'configFile': 'configs/simple_deep_adaptive_lane_occupancy.cfg'}]


    numberOfRuns = 1

    stats_sc = 'state_change'
    stats_ml = 'max_length'
    stats_tt = 'travel_time'
    stats_ql = 'queue_length'
    lane_id = 'lane_id'

    col_sc = 'new_state'
    col_ml = 'max_length'
    col_tt = 'ttime'
    col_ql = 'queue_length'
    label_ql = f'actual_queuelength_simulations_{experimentPrefix}'
    label_tt = f"mean_travel_time_{experimentPrefix}"

    file_prefixes = [stats_sc, stats_ml]
    aggregateDFsBy = ['step']
    y_columns = [col_sc, col_ml]
    kinds = [sAgg.PLOT_KIND_SCATTER, sAgg.PLOT_KIND_LINE]

    for e in experimentParams:
        e['results'] = sPlot.readResults(e['experimentPrefix'], e['prefix'], [stats_ql], numberOfRuns)
        df = e['results'][0][stats_ql]
        df = df.groupby(['step', 'tl_id'], as_index=False).agg({'queue_length' : 'mean'})
        e['results'][0][stats_ql] = df


    sPlot.createSinglePlotAveragesOnly(experimentPrefix, f"{label_ql}_avg", experimentParams, stats_ql, col_ql, 'Avg Queue Length', discretizeStepBy = 600)
