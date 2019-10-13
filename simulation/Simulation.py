

from __future__ import absolute_import
from __future__ import print_function

import random
import sys

from sumolib import checkBinary  # noqa
import traci  # noqa

import matplotlib.pyplot as plt

from simulation.event_constants import *
from simulation.TrafficLightFactory import TrafficLightFactory

class Simulation(object):

    """docstring for Simulation."""
    def __init__(self, runID, options):
        super(Simulation, self).__init__()

        self.indicators = {}

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
        traci.start([sumoBinary, "-c", "data/cross.sumocfg",
                         "--tripinfo-output", "tripinfo_isolated.xml",
                         "--step-length", "1"])

        self._preRun()
        self._run()

    def _preRun(self):
        self.trafficLights = []
        for id in traci.trafficlight.getIDList():
            self.trafficLights.append(TrafficLightFactory.createTrafficLightQLearningFPVCL(id))
            #self.trafficLights.append(TrafficLightFactory.createTrafficLightWebsterLike(id))
            #self.trafficLights.append(TrafficLight(id, TrafficLightControllerWebsterLike))

    def _run(self):
        """execute the TraCI control loop"""
        self.currentStep = 0
        # we start with phase 2 where EW has green
        # traci.trafficlight.setPhase("0", 2)
        #tls = TrafficLightStatic("0", "actuated_gap")
        while traci.simulation.getMinExpectedNumber() > 0:
            traci.simulationStep()
            for tl in self.trafficLights:
                tl.step(self.currentStep)
                for kpi in self.indicators[EVENT_SIMULATION_STEP]:
                    kpi.update(self.currentStep, tl)
            self.currentStep += 1

        for event_indicators in self.indicators.values():
            for kpi in event_indicators:
                kpi.save()
                kpi.createPlot()
        traci.close()

        sys.stdout.flush()

        return self.indicators
        #plt.show()

    #def keepTrackOf(self, Statistics):
    #    self.indicators.append(Statistics(self.runID))

    def subscribe(self, eventID, Statistics):
        if (not(eventID in self.indicators)):
            self.indicators[eventID] = []
        self.indicators[eventID].append(Statistics(self.runID))

    def notify(self, eventID, callingObject):
        for ind in (self.indicators.get(eventID, [])):
            ind.update(self.currentStep, callingObject)

#from TrafficLightStatic import TrafficLightStatic
#from TrafficLightControllerFXM import TrafficLightControllerFXM
#from TrafficLightControllerWebsterLike import TrafficLightControllerWebsterLike
