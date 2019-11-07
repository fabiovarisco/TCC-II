

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

    for p in experimentParams:
        for i in range(0, numberOfRuns):
            convertStatsFile(f"./output/{folder}/{p['prefix']}_{i}_{suffix}", f"./output/{folder}/sumo_{p['prefix']}_{i}.csv")
