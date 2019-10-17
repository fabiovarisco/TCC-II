from abc import ABC, abstractmethod

class Statistics(ABC):

    """docstring for Statistics."""
    def __init__(self, runID, filePrefix = "stats"):
        super(Statistics, self).__init__()
        self.runID = runID
        self.filePrefix = filePrefix
        self.statistics = []

    @abstractmethod
    def update(self, step, callingObject):
        pass

    @abstractmethod
    def createPlot(self):
        pass

    def save(self):
        with open(f"output/{self.runID}_{self.filePrefix}.csv", "w") as statsFile:
            print(",".join(cN for cN in self.columns), file=statsFile)
            for s in self.statistics:
                print(",".join(str(sI) for sI in s), file=statsFile)


class ObserverStatistics(Statistics):

    """docstring for Statistics."""
    def __init__(self, runID, filePrefix = "stats"):
        super(ObserverStatistics, self).__init__(runID, filePrefix)
