from abc import ABC, abstractmethod

class Statistics(ABC):

    """docstring for Statistics."""
    def __init__(self, runID, filePrefix = "stats"):
        super(Statistics, self).__init__()
        self.runID = runID
        self.filePrefix = filePrefix
        self.statistics = []

    @abstractmethod
    def gather(self, step, trafficLight):
        pass

    def save(self):
        with open(f"output/{self.runID}_{self.filePrefix}.csv", "w") as statsFile:
            for s in self.statistics:
                print(",".join(str(sI) for sI in s), file=statsFile)
