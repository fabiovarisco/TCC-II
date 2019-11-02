import random
import sys, os

from sumolib import checkBinary  # noqa
import traci  # noqa

import matplotlib.pyplot as plt

from stats.StatisticsMaxLength import StatisticsMaxLength
from stats.StatisticsTrafficLightEvents import StatisticsStageChange, StatisticsStageTime, StatisticsCycleTime
from stats.StatisticsTotalTravelTime import StatisticsTotalTravelTime
from stats.StatisticsQueueLength import StatisticsQueueLength
from stats.StatisticsRewardFunction import StatisticsRewardFunction, StatisticsAdaptiveRewardFunctionWeight
from stats.StatisticsQLearningRewards import StatisticsQLearningRewards
from tl_controller.qlearning.QLearningAlgorithmFactory import QLearningAlgorithmFactory
from simulation import Simulation
from simulation.event_constants import *
from SimulationConfig import SimulationConfig, DEMAND_NUMBER_SIMULATION_STEPS, ISOLATED_INTERSECTION_DEMAND_PWE, ISOLATED_INTERSECTION_DEMAND_PEW, ISOLATED_INTERSECTION_DEMAND_PNS, ISOLATED_INTERSECTION_DEMAND_PSN


class SimulationManager(object):

    currentSimulation = None
    """docstring for Simulation."""
    def __init__(self, options, experimentPrefix, experimentParams, numberOfRuns):
        # experimentParams = [{'prefix': prefix, 'configFile': file}]
        # experimentPrefix, numberOfRuns, configFile):
        super(SimulationManager, self).__init__()

        #self.config = SimulationConfig(experimentParams[0]['configFile'])
        #self._generate_routefile()
        self.experimentPrefix = experimentPrefix
        print(f"====== Starting Experiment {experimentPrefix} ======")
        if not os.path.exists(f"./output/{experimentPrefix}"):
            os.mkdir(f"./output/{experimentPrefix}")

        self.simulations = []
        print('====== Starting Simulation runs ======\n')
        for e in experimentParams:
            print(f"====== Starting Trial {e['prefix']} ======")
            print(f"Reading config file {e['configFile']}...")
            self.config = SimulationConfig(e['configFile'])
            simulations = []
            for i in range(0, numberOfRuns):
                print(f'Starting simulation {i + 1} of {numberOfRuns}...')
                simulations.append(self._run(f"{e['prefix']}_{i}", options))
                print('\n\n')
            e['simulations'] = simulations
            print('\n')



    def _run(self, simulationId, options):
        QLearningAlgorithmFactory.resetFactory()
        s = Simulation.Simulation(self.experimentPrefix, simulationId, options, self.config)
        SimulationManager.currentSimulation = s
        self._subscribeToStatistics(s)
        s.init()
        return s

    def _subscribeToStatistics(self, s):
        s.subscribe(EVENT_SIMULATION_STEP, StatisticsMaxLength)
        s.subscribe(EVENT_STAGE_CHANGE, StatisticsStageChange)
        s.subscribe(EVENT_STAGE_CHANGE, StatisticsStageTime)
        s.subscribe(EVENT_CYCLE_CHANGE, StatisticsCycleTime)
        s.subscribe(EVENT_SIMULATION_STEP, StatisticsTotalTravelTime)
        s.subscribe(EVENT_SIMULATION_STEP, StatisticsQueueLength)
        s.subscribe(EVENT_QLEARNING_DECISION, StatisticsQLearningRewards)
        s.subscribe(EVENT_ADAPTIVE_REWARD_FUNCTION_WEIGHT, StatisticsAdaptiveRewardFunctionWeight)
        s.subscribe(EVENT_REWARD_FUNCTION, StatisticsRewardFunction)

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
        #pWE = 1. / self.config.getInt(ISOLATED_INTERSECTION_DEMAND_PWE)
        #pEW = 1. / self.config.getInt(ISOLATED_INTERSECTION_DEMAND_PEW)
        #pNS = 1. / self.config.getInt(ISOLATED_INTERSECTION_DEMAND_PNS)
        #pSN = 1. / self.config.getInt(ISOLATED_INTERSECTION_DEMAND_PSN)

        pWE = 1. / 9
        pEW = 1. / 11
        pNS = 1. / 10
        pSN = 1. / 12
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
