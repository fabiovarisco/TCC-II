

from __future__ import absolute_import
from __future__ import print_function

import random
import sys

from sumolib import checkBinary  # noqa
import traci  # noqa

import matplotlib.pyplot as plt

from simulation.event_constants import *
from simulation.TrafficLightFactory import TrafficLightFactory
from SimulationConfig import SUMO_SIMULATION_CONFIGURATION_FILE, SUMO_SIMULATION_OUTPUT_FILE, SUMO_SIMULATION_STEP_LENGTH, DEMAND_NUMBER_SIMULATION_STEPS, TLC_TYPE

class Simulation(object):

    LOG_EVERY_STEPS = 1000

    """docstring for Simulation."""
    def __init__(self, experimentPrefix, runID, options, config):
        super(Simulation, self).__init__()

        self.config = config
        self.indicators = {}

        self.experimentPrefix = experimentPrefix
        self.runID = runID
        self.options = options
        self.currentStep = 0

    def init(self):

        if self.options.nogui:
            sumoBinary = checkBinary('sumo')
        else:
            sumoBinary = checkBinary('sumo-gui')


        # this is the normal way of using traci. sumo is started as a
        # subprocess and then the python script connects and runs
        #traci.start([sumoBinary, "-c", "simulation_files/sumocfgs/grid10.sumocfg",
        #                         "--tripinfo-output", "tripinfo_grid10.xml"])
        #traci.start([sumoBinary, "-c", "simulation_files/sumocfgs/grid5.sumocfg",
        #                 "--tripinfo-output", "tripinfo_grid5.xml",
        #                 "--step-length", "1"])
        #traci.start([sumoBinary, "-c", self.config.get(SUMO_SIMULATION_CONFIGURATION_FILE),
        #                 "--tripinfo-output", self.config.get(SUMO_SIMULATION_OUTPUT_FILE),
        #                 "--step-length", self.config.get(SUMO_SIMULATION_STEP_LENGTH)])

        self.connection = traci.connect(port=8813)
        self.connection.load(["-c", self.config.get(SUMO_SIMULATION_CONFIGURATION_FILE),
                         "--tripinfo-output", f"{self.runID}_{self.config.get(SUMO_SIMULATION_OUTPUT_FILE)}",
                         "--step-length", self.config.get(SUMO_SIMULATION_STEP_LENGTH)])
        self._preRun()
        self._run()

    def _preRun(self):
        self.trafficLights = []
        for id in traci.trafficlight.getIDList():
            self.trafficLights.append(TrafficLightFactory.createTrafficLightFromType(id,
                                        self.config.get(TLC_TYPE)))
            #self.trafficLights.append(TrafficLightFactory.createTrafficLightDeepQLearningFPVCL(id))
            #self.trafficLights.append(TrafficLightFactory.createTrafficLightQLearningFPVCL(id))
            #self.trafficLights.append(TrafficLightFactory.createTrafficLightWebsterLike(id))
            #self.trafficLights.append(TrafficLight(id, TrafficLightControllerWebsterLike))

    def _run(self):
        """execute the TraCI control loop"""
        self.currentStep = 0
        # we start with phase 2 where EW has green
        # traci.trafficlight.setPhase("0", 2)
        #tls = TrafficLightStatic("0", "actuated_gap")
        minSteps = self.config.getInt(DEMAND_NUMBER_SIMULATION_STEPS)
        while traci.simulation.getMinExpectedNumber() > 0:
            self.connection.simulationStep()
            for tl in self.trafficLights:
                tl.step(self.currentStep)
                self.notify(EVENT_SIMULATION_STEP, traffic_light = tl)
            if (self.currentStep % Simulation.LOG_EVERY_STEPS == 0):
                print(f'Executing {self.currentStep} of min {minSteps}.')
            self.currentStep += 1

        for event_indicators in self.indicators.values():
            for kpi in event_indicators:
                kpi.save()
                #kpi.createPlot()
        traci.close()

        sys.stdout.flush()

        return self.indicators
        #plt.show()

    #def keepTrackOf(self, Statistics):
    #    self.indicators.append(Statistics(self.runID))

    def subscribe(self, eventID, Statistics):
        if (not(eventID in self.indicators)):
            self.indicators[eventID] = []
        self.indicators[eventID].append(Statistics(self.runID, self.experimentPrefix))

    def notify(self, eventID, **kwargs):
        for ind in (self.indicators.get(eventID, [])):
            ind.update(self.currentStep, **kwargs)

    def getIndicators(self, eventID = None):
        if (eventID is None):
            return self.indicators
        else:
            return self.indicators[eventID]

#from TrafficLightStatic import TrafficLightStatic
#from TrafficLightControllerFXM import TrafficLightControllerFXM
#from TrafficLightControllerWebsterLike import TrafficLightControllerWebsterLike
