

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

    folder = 'exp14_hyperparam_tuning'
    prefix = 'rf_avg_veh_number'
    suffix = 'tripinfo_isolated2.xml'
    numberOfRuns = 4
    params = ['1e-05_0.7_0.6',
                '0.0001_0.7_0.6',
                '0.001_0.7_0.6',
                '0.01_0.7_0.6',
                '0.1_0.7_0.6']

    for p in params: 
        for i in range(0, numberOfRuns):
            convertStatsFile(f"./output/{folder}/{prefix}_{p}_{i}_{suffix}", f"./output/{folder}/sumo_{prefix}_{p}_{i}.csv")
    