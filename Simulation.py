

from __future__ import absolute_import
from __future__ import print_function

import random
import sys

from sumolib import checkBinary  # noqa
import traci  # noqa


class Simulation(object):

    currentStep = 0

    """docstring for Simulation."""
    def __init__(self, runID, options):
        super(Simulation, self).__init__()

        self. indicators = []

        self.runID = runID
        self.options = options

    def init(self):

        if self.options.nogui:
            sumoBinary = checkBinary('sumo')
        else:
            sumoBinary = checkBinary('sumo-gui')

        # first, generate the route file for this simulation
        self._generate_routefile()

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
        step = 0
        # we start with phase 2 where EW has green
        # traci.trafficlight.setPhase("0", 2)
        #tls = TrafficLightStatic("0", "actuated_gap")
        while traci.simulation.getMinExpectedNumber() > 0:
            traci.simulationStep()
            Simulation.currentStep = step
            for tl in self.trafficLights:
                tl.step(step)
                for kpi in self.indicators:
                    kpi.gather(step, tl)
            step += 1
        for kpi in self.indicators:
            kpi.save()
        traci.close()

        sys.stdout.flush()

    def keepTrackOf(self, Statistics):
        self.indicators.append(Statistics(self.runID))

    @staticmethod
    def getCurrentStep():
        return Simulation.currentStep

    def _generate_routefile(self):
        random.seed(42)  # make tests reproducible
        N = 3600  # number of time steps
        # demand per second from different directions
        pWE = 1. / 8
        pEW = 1. / 12
        pNS = 1. / 14
        pSN = 1. / 16
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

from TrafficLightStatic import TrafficLightStatic
from TrafficLight import TrafficLight, TrafficLightFactory
from TrafficLightControllerFXM import TrafficLightControllerFXM
from TrafficLightControllerWebsterLike import TrafficLightControllerWebsterLike
