import os
import sys

import traci  # noqa

from TrafficLightController import TrafficLightController

class TrafficLightStatic(TrafficLightController):

    """docstring for TrafficLightStatic."""
    def __init__(self, tlsID):
        super().__init__(tlsID)
        
    def setProgram(self, programId):
        self.programID = programID
        traci.trafficlight.setProgram(self.id, programID)

    def step(self):
        pass
