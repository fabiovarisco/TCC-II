import random
import sys

from sumolib import checkBinary  # noqa
import traci  # noqa

import matplotlib.pyplot as plt

from stats.StatisticsMaxLength import StatisticsMaxLength
from stats.StatisticsStageChange import StatisticsStageChange
from simulation import Simulation
from simulation.event_constants import *

NUMBER_STEPS = 500

class SimulationManager(object):

    currentSimulation = None
    """docstring for Simulation."""
    def __init__(self, options, experimentPrefix, numberOfRuns):
        super(SimulationManager, self).__init__()

        self._generate_routefile()

        for i in range(0, numberOfRuns):
            self._run(f"{experimentPrefix}_{i}", options)


    def _run(self, simulationId, options):
        s = Simulation.Simulation(simulationId, options)
        SimulationManager.currentSimulation = s
        s.subscribe(EVENT_SIMULATION_STEP, StatisticsMaxLength)
        s.subscribe(EVENT_STAGE_CHANGE, StatisticsStageChange)
        s.init()

    @staticmethod
    def getCurrentSimulation():
        return SimulationManager.currentSimulation

    @staticmethod
    def getCurrentSimulationStep():
        return SimulationManager.currentSimulation.currentStep

    def _generate_routefile(self):
        random.seed(42)  # make tests reproducible
        #N = 3600  # number of time steps
        N = NUMBER_STEPS
        # demand per second from different directions
        pWE = 1. / 4
        pEW = 1. / 5
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
