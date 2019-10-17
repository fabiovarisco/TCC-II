import random
import sys

from sumolib import checkBinary  # noqa
import traci  # noqa

import matplotlib.pyplot as plt

from stats.StatisticsMaxLength import StatisticsMaxLength
from stats.StatisticsStageChange import StatisticsStageChange
from stats.StatisticsTotalTravelTime import StatisticsTotalTravelTime
from simulation import Simulation
from simulation.event_constants import *
from SimulationConfig import SimulationConfig, DEMAND_NUMBER_SIMULATION_STEPS, ISOLATED_INTERSECTION_DEMAND_PWE, ISOLATED_INTERSECTION_DEMAND_PEW, ISOLATED_INTERSECTION_DEMAND_PNS, ISOLATED_INTERSECTION_DEMAND_PSN

from stats.Statistics import StatisticsAggregator as sAgg

class SimulationManager(object):

    currentSimulation = None
    """docstring for Simulation."""
    def __init__(self, options, experimentParams, numberOfRuns):
        # experimentParams = [{'prefix': prefix, 'configFile': file}]
        # experimentPrefix, numberOfRuns, configFile):
        super(SimulationManager, self).__init__()

        #self._generate_routefile()

        self.simulations = []
        for e in experimentParams:
            self.config = SimulationConfig(e['configFile'])
            simulations = []
            for i in range(0, numberOfRuns):
                simulations.append(self._run(f"{e['prefix']}_{i}", options))
            e['simulations'] = simulations



    def _run(self, simulationId, options):
        s = Simulation.Simulation(simulationId, options, self.config)
        SimulationManager.currentSimulation = s
        s.subscribe(EVENT_SIMULATION_STEP, StatisticsMaxLength)
        s.subscribe(EVENT_STAGE_CHANGE, StatisticsStageChange)
        s.subscribe(EVENT_SIMULATION_STEP, StatisticsTotalTravelTime)
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
