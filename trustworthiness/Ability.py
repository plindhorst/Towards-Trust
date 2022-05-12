from actions1.HumanAction import *
from actions1.AgentAction import *
from actions1.util import is_correct_drop_location

NUMBER_OF_PATIENTS = 8

class Ability:
    def __init__(self, actions):
        self._actions = actions

    # Returns computed ability
    def compute(self):
        score = 0
        return score


    def _victims_saved(self):
        count = 0
        for i, action in enumerate(self._actions):
            if type(action) is DropOff:
                if is_correct_drop_location(action.person, action.location):
                    count += 1

        return count/NUMBER_OF_PATIENTS
        # return count - if we want to normalize through aggregation.


    # def _victims_saved_alternative(self):
    #     count = 0
    #     for i, action in enumerate(self._actions):
    #         if type(action) is DropOff:
    #             if action.person["is_goal_block"] and action.location["is_drop_zone"]:
    #                 count += 1
    #
    #     return count/NUMBER_OF_PATIENTS
    #     # return count - if we want to normalize through aggregation.