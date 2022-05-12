from actions1.HumanAction import *


class Benevolence:
    def __init__(self, actions):
        self._actions = actions

    # Returns computed benevolence
    def compute(self):
        score = 0
        return score

    # Returns the times communicated victim found
    def _truth_pickup(self):
        count = 0

        for i, action in enumerate(self._actions):
            if type(action) is MessageFound:
                count += 1

        return count

    # Returns the times communicated victim picked up
    def _truth_pickup(self):
        count = 0

        for i, action in enumerate(self._actions):
            if type(action) is MessagePickUp:
                count += 1

        return count
