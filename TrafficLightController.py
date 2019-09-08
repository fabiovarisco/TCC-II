from abc import ABC, abstractmethod

class TrafficLightController(ABC):

    def __init__(self, trafficLight):
        #self.tlsID = tlsID
        super().__init__()
        self.trafficLight = trafficLight

    @abstractmethod
    def step(self, step):
        pass
