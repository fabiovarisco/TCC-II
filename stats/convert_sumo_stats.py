

import xml.etree.ElementTree as ET

def convertStatsFile(input, output):
    tree = ET.parse(input)
    root = tree.getroot()
    lines = []
    lines.append(['step',
                   'vehicle_id',
                   'departDelay',
                   'duration',
                   'routeLength',
                   'waitingTime',
                   'waitingCount',
                   'timeLoss'])
    for tripinfo in root.iter('tripinfo'):
        lines.append([tripinfo.get('arrival'),
                        tripinfo.get('id'),
                        tripinfo.get('departDelay'),
                        tripinfo.get('duration'),
                        tripinfo.get('routeLength'),
                        tripinfo.get('waitingTime'),
                        tripinfo.get('waitingCount'),
                        tripinfo.get('timeLoss')])

    with open(output, 'w') as f:
        for line in lines:
            print(','.join(map(str, line)), file=f)

    print(f"Successfully written {len(lines)} to {output}")


if __name__ == '__main__':

    folder = 'exp14_hyperparam_tuning_2'
    prefix = 'rf_avg_veh_number'
    suffix = 'tripinfo_isolated2.xml'
    numberOfRuns = 5
    experimentParams = [{'experimentPrefix': 'exp14_hyperparam_tuning_2', 'prefix': 'rf_avg_veh_number_0.001_0.6_0.6', 'configFile': 'configs/simple_qlearning_avg_vehicle_number.cfg'},
                        {'experimentPrefix': 'exp14_hyperparam_tuning_2', 'prefix': 'rf_avg_veh_number_0.001_0.7_0.6', 'configFile': 'configs/simple_qlearning_avg_vehicle_number.cfg'},
                        {'experimentPrefix': 'exp14_hyperparam_tuning_2', 'prefix': 'rf_avg_veh_number_0.001_0.7999999999999999_0.6', 'configFile': 'configs/simple_qlearning_avg_vehicle_number.cfg'},
                        {'experimentPrefix': 'exp14_hyperparam_tuning_2', 'prefix': 'rf_avg_veh_number_0.001_0.8999999999999999_0.6', 'configFile': 'configs/simple_qlearning_avg_vehicle_number.cfg'},
                        {'experimentPrefix': 'exp14_hyperparam_tuning_2', 'prefix': 'rf_avg_veh_number_0.001_0.6_0.7', 'configFile': 'configs/simple_qlearning_avg_vehicle_number.cfg'},
                        {'experimentPrefix': 'exp14_hyperparam_tuning_2', 'prefix': 'rf_avg_veh_number_0.001_0.7_0.7', 'configFile': 'configs/simple_qlearning_avg_vehicle_number.cfg'},
                        {'experimentPrefix': 'exp14_hyperparam_tuning_2', 'prefix': 'rf_avg_veh_number_0.001_0.7999999999999999_0.7', 'configFile': 'configs/simple_qlearning_avg_vehicle_number.cfg'},
                        {'experimentPrefix': 'exp14_hyperparam_tuning_2', 'prefix': 'rf_avg_veh_number_0.001_0.8999999999999999_0.7', 'configFile': 'configs/simple_qlearning_avg_vehicle_number.cfg'},
                        {'experimentPrefix': 'exp14_hyperparam_tuning_2', 'prefix': 'rf_avg_veh_number_0.001_0.6_0.7999999999999999', 'configFile': 'configs/simple_qlearning_avg_vehicle_number.cfg'},
                        {'experimentPrefix': 'exp14_hyperparam_tuning_2', 'prefix': 'rf_avg_veh_number_0.001_0.7_0.7999999999999999', 'configFile': 'configs/simple_qlearning_avg_vehicle_number.cfg'}
#                        {'experimentPrefix': 'exp14_hyperparam_tuning_2', 'prefix': 'rf_avg_veh_number_0.001_0.7999999999999999_0.7999999999999999', 'configFile': 'configs/simple_qlearning_avg_vehicle_number.cfg'},
#                        {'experimentPrefix': 'exp14_hyperparam_tuning_2', 'prefix': 'rf_avg_veh_number_0.001_0.8999999999999999_0.7999999999999999', 'configFile': 'configs/simple_qlearning_avg_vehicle_number.cfg'}
    ]

    folder = 'exp21_rf_80p'
    experimentParams = [
        {'prefix': 'ql_', 'configFile': 'configs/single_basic_qlearning_avg_queue_length.cfg'},
        {'prefix': 'veh_n_', 'configFile': 'configs/single_basic_qlearning_avg_vehicle_number.cfg'},
        {'prefix': 'delay_', 'configFile': 'configs/single_basic_qlearning_delay.cfg'},
        {'prefix': 'throughput_', 'configFile': 'configs/single_basic_qlearning_throughput.cfg'},
        {'prefix': 'delay_prq_', 'configFile': 'configs/single_basic_qlearning_delay_res_queue_penalty.cfg'},
        {'prefix': 'delay_pwtl_', 'configFile': 'configs/single_basic_qlearning_delay_wasted_time_penalty_log.cfg'},
        {'prefix': 'act_throughput_mqr_', 'configFile': 'configs/single_basic_qlearning_act_throughput_mqr.cfg'}]
    folder = 'exp21_rf_80p' 
    experimentParams = [
        {'prefix': 'veh_n_pwtl_', 'configFile': 'configs/single_basic_qlearning_veh_n_wasted_time_penalty_log.cfg'},
        {'prefix': 'throughput_pwtl_', 'configFile': 'configs/single_basic_qlearning_throughput_wasted_time_penalty_log.cfg'}
    ]
    folder = 'exp22' 
    
    experimentParams = [
        {'prefix': 'adapt_veh_n_thp_-0.2', 'configFile': 'configs/single_basic_qlearning_adaptative_veh_n_throughput.cfg'},
        {'prefix': 'adapt_veh_n_thp_-0.1', 'configFile': 'configs/single_basic_qlearning_adaptative_veh_n_throughput.cfg'},
        {'prefix': 'adapt_veh_n_thp_0.0', 'configFile': 'configs/single_basic_qlearning_adaptative_veh_n_throughput.cfg'},
        {'prefix': 'adapt_veh_n_thp_0.1', 'configFile': 'configs/single_basic_qlearning_adaptative_veh_n_throughput.cfg'},
        {'prefix': 'adapt_veh_n_thp_0.2', 'configFile': 'configs/single_basic_qlearning_adaptative_veh_n_throughput.cfg'},
        {'prefix': 'adapt_veh_n_thp_0.30000000000000004', 'configFile': 'configs/single_basic_qlearning_adaptative_veh_n_throughput.cfg'},
        {'prefix': 'adapt_veh_n_thp_0.4', 'configFile': 'configs/single_basic_qlearning_adaptative_veh_n_throughput.cfg'},
        {'prefix': 'adapt_veh_n_thp_0.5', 'configFile': 'configs/single_basic_qlearning_adaptative_veh_n_throughput.cfg'},
    ]

    suffix = 'tripinfo_isolated.xml'
    numberOfRuns = 10

    experimentParams = [
        {'prefix': 'adap_vehn_', 'configFile': 'configs/single_final_qlearning_adaptative_veh_n_throughput.cfg'},
        {'prefix': 'veh_n_', 'configFile': 'configs/single_final_qlearning_avg_vehicle_number.cfg'},
        {'prefix': 'thp_', 'configFile': 'configs/single_final_qlearning_throughput.cfg'},
        {'prefix': 'fxm_', 'configFile': 'configs/single_final_fixed_time.cfg'},
        {'prefix': 'adap_dwtp_', 'configFile': 'configs/single_final_qlearning_adaptative_delay_throughput.cfg'},
        {'prefix': 'dwtp_', 'configFile': 'configs/single_final_qlearning_delay_wasted_time_penalty_log.cfg'}
    ]
    folder = 'exp23'
    numberOfRuns = 15


    for p in experimentParams:
        for i in range(0, numberOfRuns):
            convertStatsFile(f"./output/{folder}/{p['prefix']}_{i}_{suffix}", f"./output/{folder}/sumo_{p['prefix']}_{i}.csv")
