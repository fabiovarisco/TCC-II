import os
import sys

import traci  # noqa

from TrafficLightController import TrafficLightController

class TrafficLightStatic(TrafficLightController):

    """docstring for TrafficLightStatic."""
    def __init__(self, tlsID, programID):
        super().__init__(tlsID)
        self.programID = programID
        traci.trafficlight.setProgram(tlsID, programID)

    def step():
        pass
