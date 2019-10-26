from stats.Statistics import ObserverStatistics

class StatisticsQLearningRewards(ObserverStatistics):

    """docstring for StatisticsQLearningRewards."""
    def __init__(self, runID, filePrefix = "qlearning_rewards"):
        super(StatisticsQLearningRewards, self).__init__(runID, ['step', 'tl_id', 'previous_state', 'current_state', 'action', 'reward'], filePrefix)

    def update(self, step, **kwargs):
        self.statistics.append([step, kwargs['tl_id'], kwargs['previous_state'], kwargs['current_state'], kwargs['action'], kwargs['reward']])

    def createPlot(self):
        pass