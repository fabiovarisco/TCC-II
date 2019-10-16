import random
import sys

from sumolib import checkBinary  # noqa
import traci  # noqa

import matplotlib.pyplot as plt

from stats.StatisticsMaxLength import StatisticsMaxLength
from stats.StatisticsStageChange import StatisticsStageChange
from simulation import Simulation
from simulation.event_constants import *
from SimulationConfig import SimulationConfig, DEMAND_NUMBER_SIMULATION_STEPS, ISOLATED_INTERSECTION_DEMAND_PWE, ISOLATED_INTERSECTION_DEMAND_PEW, ISOLATED_INTERSECTION_DEMAND_PNS, ISOLATED_INTERSECTION_DEMAND_PSN

from matplotlib import plt
from stats.Statistics import StatisticsAggregator as sAgg

class SimulationManager(object):

    currentSimulation = None
    """docstring for Simulation."""
    def __init__(self, options, experimentParams, numberOfRuns):
        # experimentParams = [{'prefix': prefix, 'configFile': file}]
        # experimentPrefix, numberOfRuns, configFile):
        super(SimulationManager, self).__init__()

        self._generate_routefile()

        self.simulations = []
        for e in experimentParams: 
            self.config = SimulationConfig(e['configFile'])
            simulations = []
            for i in range(0, numberOfRuns):
                simulations.append(self._run(f"{e['prefix']}_{i}", options))
            e['simulations'] = simulations
        
        
        plt.figure("queuelength_simulations")
        fig, axes = plt.subplots(nrows=len(experimentParams), ncols=numberOfRuns, figsize=(12, 8))
        plt.setp(axes.flat, xlabel='step', ylabel='max length')

        pad = 5 # in points

        for i in range(0, numberOfRuns):
            axes[0].annotate(i, xy=(0.5, 1), xytext=(0, pad),
                        xycoords='axes fraction', textcoords='offset points',
                        size='large', ha='center', va='baseline')

        for e in experimentParams:
            axes[:,0].annotate(e['prefix'], xy=(0, 0.5), xytext=(-ax.yaxis.labelpad - pad, 0),
                        xycoords=ax.yaxis.label, textcoords='offset points',
                        size='large', ha='right', va='center')

        r = 0 
        for e in experimentParams: 
            c = 0
            #dfs_ql = []
            for s in e['simulations']:
                plt.subplots(len(experimentParams), numberOfRuns, (r * numberOfRuns) + c + 1)
                df_ql = s.getIndicators(EVENT_SIMULATION_STEP)[0]
                df_sc = s.getIndicators(EVENT_STAGE_CHANGE)[0]
                dfs = sAgg.aggregateDataframes([df_ql, df_sc], ['step'])
                sAgg.plot(dfs, 'step', ['new_state', 'max_length'], ['scatter', 'line'])
                
        fig.tight_layout()
        # tight_layout doesn't take these labels into account. We'll need 
        # to make some room. These numbers are are manually tweaked. 
        # You could automatically calculate them, but it's a pain.
        fig.subplots_adjust(left=0.15, top=0.95)
        plt.savefig("out_plots/queue_length_simulations.png")




    def _run(self, simulationId, options):
        s = Simulation.Simulation(simulationId, options, self.config)
        SimulationManager.currentSimulation = s
        s.subscribe(EVENT_SIMULATION_STEP, StatisticsMaxLength)
        s.subscribe(EVENT_STAGE_CHANGE, StatisticsStageChange)
        s.init()
        return s

    @staticmethod
    def getCurrentSimulation():
        return SimulationManager.currentSimulation

    @staticmethod
    def getCurrentSimulationStep():
        return SimulationManager.currentSimulation.currentStep

    def _generate_routefile(self):
        random.seed(42)  # make tests reproducible
        #N = 3600  # number of time steps
        N = self.config.getInt(DEMAND_NUMBER_SIMULATION_STEPS)
        # demand per second from different directions
        pWE = 1. / self.config.getInt(ISOLATED_INTERSECTION_DEMAND_PWE)
        pEW = 1. / self.config.getInt(ISOLATED_INTERSECTION_DEMAND_PEW)
        pNS = 1. / self.config.getInt(ISOLATED_INTERSECTION_DEMAND_PNS)
        pSN = 1. / self.config.getInt(ISOLATED_INTERSECTION_DEMAND_PSN)
        with open("data/cross.rou.xml", "w") as routes:
            print("""<routes>
            <vType id="passenger" accel="0.8" decel="4.5" sigma="0.5" length="5" minGap="2.5" maxSpeed="16.67" \
    guiShape="passenger"/>
            <vType id="typeNS" accel="0.8" decel="4.5" sigma="0.5" length="7" minGap="3" maxSpeed="25" guiShape="bus"/>

            <route id="right" edges="51o 1i 2o 52i" />
            <route id="left" edges="52o 2i 1o 51i" />
            <route id="down" edges="54o 4i 3o 53i" />
            <route id="up" edges="53o 3i 4o 54i" />
            """, file=routes)
            vehNr = 0
            for i in range(N):
                if random.uniform(0, 1) < pWE:
                    print('    <vehicle id="right_%i" type="passenger" route="right" depart="%i" />' % (
                        vehNr, i), file=routes)
                    vehNr += 1
                if random.uniform(0, 1) < pEW:
                    print('    <vehicle id="left_%i" type="passenger" route="left" depart="%i" />' % (
                        vehNr, i), file=routes)
                    vehNr += 1
                if random.uniform(0, 1) < pNS:
                    print('    <vehicle id="down_%i" type="passenger" route="down" depart="%i" color="1,0,0"/>' % (
                        vehNr, i), file=routes)
                    vehNr += 1
                if random.uniform(0, 1) < pSN:
                    print('    <vehicle id="up_%i" type="passenger" route="up" depart="%i" color="1,0,0"/>' % (
                        vehNr, i), file=routes)
                    vehNr += 1
            print("</routes>", file=routes)
