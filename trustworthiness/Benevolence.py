import numpy as np
from actions1.HumanAction import *
from actions1.AgentAction import *
from actions1.util import is_in_room, get_persons_in_room

class Benevolence:
    def __init__(self, actions):
        self._actions = actions

    # Returns computed benevolence
    def compute(self):
        metrics = [self._communicated_pickup(), self._communicated_yes_no(), self._communicated_baby_gender(),
                   self._communicated_room_search()]
        score = np.mean(metrics)
        return score

    # returns ratio of communicated baby gender identification to the total number of identification actions.
    def _communicated_baby_gender(self):
        count = 0
        total = 0

        # total number of agent gender identification requests.
        for i, action in self._actions:
            if type(action) is MessageAskGender:
                total += 1

        # total number of human gender identification responses.
        for j, action in self._actions:
            if type(action) is MessageBoy | type(action) is MessageGirl:
                count += 1

        if count > total | total == 0:
            return 1

        return count / total

    # returns ratio of communicated yes/no to the total number of pick-up requests.
    def _communicated_yes_no(self):
        count = 0
        total = 0

        # total number of agent pick-up requests
        for i, action in self._actions:
            if type(action) is MessageRequestPickup:
                total += 1

        # total number of yes/no responses from human
        for j, action in self._actions:
            if type(action) is MessageYes | type(action) is MessageNo:
                count += 1

        if count > total | total == 0:
            return 1

        return count / total

    # return ratio of communicated room search to total number of room search actions.
    def _communicated_room_search(self):
        count = 0
        total = 0

        # total number of rooms searched by human agent.
        for i, action in self._actions:
            if type(action) is EnterRoom:
                total += 1

        # number of room searches that are communicated by human agent.
        for j, action in self._actions:
            if type(action) is MessageSearch:
                count += 1

        if count > total | total == 0:
            return 1

        return count / total

    # return ratio of communicated pick-ups to total number of pick-up actions.
    def _communicated_pickup(self):
        count = 0
        total = 0

        # total number of pick-ups by human agent.
        for i, action in self._actions:
            if type(action) is PickUp:
                # we ensure that the pick-up occurs in the room where the patient is found.
                # this is done to discard pick-ups that might happen for rearrangement purposes.
                action_room = is_in_room(action.location)
                if action_room is not None:
                    total += 1

        # total number of communicated pick-ups by human agent.
        for j, action in self._actions:
            if type(action) is MessagePickUp:
                count += 1

        if count > total | total == 0:
            return 1

        return count / total



