import random
import sys

'''
params should be an array of dicts containing the keys:
{'steps', 'pWE', 'pEW', 'pNS', 'pSN', 'start_change_in'}
'''
def generate_routefile(params, filename):
    random.seed(42)  # make tests reproducible
    #N = 3600  # number of time steps
    #N = self.config.getInt(DEMAND_NUMBER_SIMULATION_STEPS)
    # demand per second from different directions
    #pWE = 1. / self.config.getInt(ISOLATED_INTERSECTION_DEMAND_PWE)
    #pEW = 1. / self.config.getInt(ISOLATED_INTERSECTION_DEMAND_PEW)
    #pNS = 1. / self.config.getInt(ISOLATED_INTERSECTION_DEMAND_PNS)
    #pSN = 1. / self.config.getInt(ISOLATED_INTERSECTION_DEMAND_PSN)

    #"data/cross.rou.xml"
    with open(filename, "w") as routes:
        print("""<routes>
        <vType id="passenger" accel="0.8" decel="4.5" sigma="0.5" length="5" minGap="2.5" maxSpeed="16.67" \
guiShape="passenger"/>
        <vType id="typeNS" accel="0.8" decel="4.5" sigma="0.5" length="7" minGap="3" maxSpeed="25" guiShape="bus"/>

        <route id="right" edges="51o 1i 2o 52i" />
        <route id="left" edges="52o 2i 1o 51i" />
        <route id="down" edges="54o 4i 3o 53i" />
        <route id="up" edges="53o 3i 4o 54i" />
        """, file=routes)

        totalVehNr = 0
        stepCounter = 0
        for i, p in enumerate(params):
            pWE, pEW, pNS, pSN = getProbabilities(p)
            vehNr = 0
            delta = False
            if (i + 1) < len(params):
                startChangeIn = p['start_change_in']
                delta_pWE, delta_pEW, delta_pNS, delta_pSN = getChangeRatios(pWE, pEW, pNS, pSN,
                                                                params[i+1],
                                                                (p['steps'] - startChangeIn))
                delta = True

            for s in range(p['steps']):
                for j in range(p['repeat']):
                    if random.uniform(0, 1) < pWE:
                        print('    <vehicle id="right__%i_%i_%i" type="passenger" route="right" depart="%i" />' % (
                            i, j, vehNr, stepCounter), file=routes)
                        vehNr += 1
                    if random.uniform(0, 1) < pEW:
                        print('    <vehicle id="left_%i_%i_%i" type="passenger" route="left" depart="%i" />' % (
                            i, j, vehNr, stepCounter), file=routes)
                        vehNr += 1
                    if random.uniform(0, 1) < pNS:
                        print('    <vehicle id="down_%i_%i_%i" type="passenger" route="down" depart="%i" color="1,0,0"/>' % (
                            i, j, vehNr, stepCounter), file=routes)
                        vehNr += 1
                    if random.uniform(0, 1) < pSN:
                        print('    <vehicle id="up_%i_%i_%i" type="passenger" route="up" depart="%i" color="1,0,0"/>' % (
                            i, j, vehNr, stepCounter), file=routes)
                        vehNr += 1
                if delta and s >= startChangeIn:
                    pWE += delta_pWE
                    pEW += delta_pEW
                    pNS += delta_pNS
                    pSN += delta_pSN
                stepCounter += 1
            print(f"Params: {p} generated {vehNr} vehicles")
            totalVehNr += vehNr
        print("</routes>", file=routes)
        print(f"Total: {totalVehNr} vehicles.")

def getChangeRatios(pWE, pEW, pNS, pSN, nextParam, delta_time_steps):
    npWE, npEW, npNS, npSN = getProbabilities(nextParam)
    return (calculateDelta(pWE, npWE, delta_time_steps),
        calculateDelta(pEW, npEW, delta_time_steps),
        calculateDelta(pNS, npNS, delta_time_steps),
        calculateDelta(pSN, npSN, delta_time_steps))

def calculateDelta(curP, nextP, delta_time_steps):
    return (nextP - curP) / delta_time_steps

def getProbabilities(param):
    return (1./param['pWE']), (1./param['pEW']), (1./param['pNS']), (1./param['pSN'])

if __name__ == '__main__':
    params = [
        {'steps': 1000, 'pWE':20, 'pEW':19, 'pNS':23, 'pSN':21, 'repeat':1, 'start_change_in': 900},
        {'steps': 1000, 'pWE':13, 'pEW':15, 'pNS':12, 'pSN':14, 'repeat':1, 'start_change_in': 950},
        {'steps': 1000, 'pWE':3, 'pEW':2, 'pNS':4, 'pSN':3, 'repeat':1, 'start_change_in': 850},
        {'steps': 1000, 'pWE':1, 'pEW':1.5, 'pNS':2, 'pSN':1.5, 'repeat':1, 'start_change_in': 850},
        {'steps': 1000, 'pWE':13, 'pEW':15, 'pNS':9, 'pSN':8, 'repeat':1, 'start_change_in': 850},
        {'steps': 4000, 'pWE':19, 'pEW':23, 'pNS':18, 'pSN':20, 'repeat':1, 'start_change_in': 3800},
        {'steps': 1000, 'pWE':13, 'pEW':15, 'pNS':12, 'pSN':14, 'repeat':1, 'start_change_in': 950},
        {'steps': 400, 'pWE':3, 'pEW':2, 'pNS':4, 'pSN':3, 'repeat':1, 'start_change_in': 350},
        {'steps': 500, 'pWE':3, 'pEW':2, 'pNS':4, 'pSN':3, 'repeat':2, 'start_change_in': 450},
        {'steps': 500, 'pWE':1, 'pEW':1.5, 'pNS':2, 'pSN':1.5, 'repeat':2, 'start_change_in': 180},
        {'steps': 200, 'pWE':1, 'pEW':1.5, 'pNS':2, 'pSN':1.5, 'repeat':1, 'start_change_in': 180},
        {'steps': 1000, 'pWE':13, 'pEW':15, 'pNS':9, 'pSN':8, 'repeat':1, 'start_change_in': 850},
        {'steps': 5000, 'pWE':19, 'pEW':23, 'pNS':18, 'pSN':20, 'repeat':1, 'start_change_in': 950},
    ]

    params = [
        {'steps': 5000, 'pWE':20, 'pEW':19, 'pNS':23, 'pSN':21, 'repeat':1, 'start_change_in': 4900},
        {'steps': 5000, 'pWE':13, 'pEW':15, 'pNS':12, 'pSN':14, 'repeat':1, 'start_change_in': 4950},
        {'steps': 5000, 'pWE':3, 'pEW':2, 'pNS':4, 'pSN':3, 'repeat':1, 'start_change_in': 4850},
        {'steps': 3000, 'pWE':1, 'pEW':1.5, 'pNS':2, 'pSN':1.5, 'repeat':1, 'start_change_in': 2850},
        {'steps': 2000, 'pWE':1, 'pEW':1.5, 'pNS':2, 'pSN':1.5, 'repeat':1, 'start_change_in': 1900},
        {'steps': 5000, 'pWE':13, 'pEW':15, 'pNS':9, 'pSN':8, 'repeat':1, 'start_change_in': 4850},
        {'steps': 10000, 'pWE':19, 'pEW':23, 'pNS':18, 'pSN':20, 'repeat':1, 'start_change_in': 950},
    ]

    params = [
        {'steps': 20000, 'pWE':20, 'pEW':19, 'pNS':23, 'pSN':21, 'repeat':1, 'start_change_in': 19500},
        {'steps': 20000, 'pWE':13, 'pEW':15, 'pNS':12, 'pSN':14, 'repeat':1, 'start_change_in': 950}
    ]
    # ========= ENTIRE DAY ============
    params = [
        {'steps': 3600, 'pWE':20, 'pEW':22, 'pNS':26, 'pSN':27, 'repeat':1, 'start_change_in': 2400}, # 4
        {'steps': 3600, 'pWE':17, 'pEW':16, 'pNS':21, 'pSN':21, 'repeat':1, 'start_change_in': 3000}, # 5
        {'steps': 3600, 'pWE':9, 'pEW':10, 'pNS':15, 'pSN':14, 'repeat':1, 'start_change_in': 900}, # 6
        {'steps': 1800, 'pWE':6, 'pEW':6, 'pNS':9, 'pSN':10, 'repeat':1, 'start_change_in': 900}, # 7
        {'steps': 1800, 'pWE':3, 'pEW':2, 'pNS':6, 'pSN':5, 'repeat':1, 'start_change_in': 1200}, # 7:30
        {'steps': 1800, 'pWE':1.5, 'pEW':1.2, 'pNS':4, 'pSN':3, 'repeat':1, 'start_change_in': 900}, # 8
        {'steps': 1800, 'pWE':1.5, 'pEW':1.2, 'pNS':5, 'pSN':5, 'repeat':2, 'start_change_in': 900}, # 8:30
        {'steps': 1800, 'pWE':3, 'pEW':2, 'pNS':7, 'pSN':8, 'repeat':1, 'start_change_in': 900}, # 9
        {'steps': 1800, 'pWE':8, 'pEW':7, 'pNS':11, 'pSN':12, 'repeat':1, 'start_change_in': 900}, # 9:30
        {'steps': 3600, 'pWE':12, 'pEW':11, 'pNS':15, 'pSN':15, 'repeat':1, 'start_change_in': 2100}, # 10
        {'steps': 3600, 'pWE':14, 'pEW':15, 'pNS':18, 'pSN':19, 'repeat':1, 'start_change_in': 1800}, # 11
        {'steps': 3600, 'pWE':10, 'pEW':11, 'pNS':15, 'pSN':14, 'repeat':1, 'start_change_in': 1800}, # 12
        {'steps': 3600, 'pWE':10, 'pEW':11, 'pNS':15, 'pSN':14, 'repeat':1, 'start_change_in': 1800}, # 13
        {'steps': 3600, 'pWE':16, 'pEW':17, 'pNS':20, 'pSN':22, 'repeat':1, 'start_change_in': 1800}, # 14
        {'steps': 3600, 'pWE':20, 'pEW':22, 'pNS':25, 'pSN':26, 'repeat':1, 'start_change_in': 2400}, # 15
        {'steps': 1800, 'pWE':14, 'pEW':15, 'pNS':20, 'pSN':20, 'repeat':1, 'start_change_in': 1200}, # 16
        {'steps': 1800, 'pWE':9, 'pEW':8, 'pNS':14, 'pSN':15, 'repeat':1, 'start_change_in': 1200}, # 16:30
        {'steps': 1800, 'pWE':5, 'pEW':6, 'pNS':10, 'pSN':11, 'repeat':1, 'start_change_in': 900}, # 17
        {'steps': 1800, 'pWE':2, 'pEW':2, 'pNS':5, 'pSN':5, 'repeat':1, 'start_change_in': 900}, # 17:30
        {'steps': 1800, 'pWE':1.3, 'pEW':1.2, 'pNS':3, 'pSN':4, 'repeat':1, 'start_change_in': 900}, # 18
        {'steps': 1800, 'pWE':2, 'pEW':3, 'pNS':6, 'pSN':6, 'repeat':1, 'start_change_in': 900}, # 18:30
        {'steps': 3600, 'pWE':5, 'pEW':4, 'pNS':10, 'pSN':11, 'repeat':1, 'start_change_in': 1800}, # 19
        {'steps': 3600, 'pWE':10, 'pEW':8, 'pNS':15, 'pSN':16, 'repeat':1, 'start_change_in': 1800}, # 20
        {'steps': 3600, 'pWE':16, 'pEW':17, 'pNS':20, 'pSN':22, 'repeat':1, 'start_change_in': 1800}, # 21
        {'steps': 3600, 'pWE':20, 'pEW':20, 'pNS':25, 'pSN':26, 'repeat':1, 'start_change_in': 2400}, # 2
        {'steps': 3600, 'pWE':25, 'pEW':24, 'pNS':30, 'pSN':29, 'repeat':1, 'start_change_in': 2400} # 23
    ]

    # ========= HALF DAY ============
    params = [
        {'steps': 3600, 'pWE':20, 'pEW':22, 'pNS':26, 'pSN':27, 'repeat':1, 'start_change_in': 2400}, # 4
        {'steps': 3600, 'pWE':17, 'pEW':16, 'pNS':21, 'pSN':21, 'repeat':1, 'start_change_in': 3000}, # 5
        {'steps': 3600, 'pWE':9, 'pEW':10, 'pNS':15, 'pSN':14, 'repeat':1, 'start_change_in': 900}, # 6
        {'steps': 1800, 'pWE':6, 'pEW':6, 'pNS':9, 'pSN':10, 'repeat':1, 'start_change_in': 900}, # 7
        {'steps': 1800, 'pWE':3, 'pEW':2, 'pNS':6, 'pSN':5, 'repeat':1, 'start_change_in': 1200}, # 7:30
        {'steps': 1800, 'pWE':1.5, 'pEW':1.2, 'pNS':4, 'pSN':3, 'repeat':1, 'start_change_in': 900}, # 8
        {'steps': 1800, 'pWE':1.5, 'pEW':1.2, 'pNS':5, 'pSN':5, 'repeat':2, 'start_change_in': 900}, # 8:30
        {'steps': 1800, 'pWE':3, 'pEW':2, 'pNS':7, 'pSN':8, 'repeat':1, 'start_change_in': 900}, # 9
        {'steps': 1800, 'pWE':8, 'pEW':7, 'pNS':11, 'pSN':12, 'repeat':1, 'start_change_in': 900}, # 9:30
        {'steps': 3600, 'pWE':12, 'pEW':11, 'pNS':15, 'pSN':15, 'repeat':1, 'start_change_in': 2100}, # 10
        {'steps': 3600, 'pWE':14, 'pEW':15, 'pNS':18, 'pSN':19, 'repeat':1, 'start_change_in': 1800}, # 11
        {'steps': 3600, 'pWE':10, 'pEW':11, 'pNS':15, 'pSN':14, 'repeat':1, 'start_change_in': 1800}, # 12
        {'steps': 3600, 'pWE':10, 'pEW':11, 'pNS':15, 'pSN':14, 'repeat':1, 'start_change_in': 1800}, # 13
        {'steps': 3600, 'pWE':16, 'pEW':17, 'pNS':20, 'pSN':22, 'repeat':1, 'start_change_in': 1800}, # 14
        {'steps': 3600, 'pWE':20, 'pEW':22, 'pNS':25, 'pSN':26, 'repeat':1, 'start_change_in': 2400} # 15 
        ]
    
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("out_file")
    args = parser.parse_args()
    #"./simulation_files/routes/single.rou.xml"
    generate_routefile(params, args.out_file)
