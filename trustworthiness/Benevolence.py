from actions1.HumanAction import *
from actions1.AgentAction import *


class Benevolence:
    def __init__(self, actions):
        self._actions = actions

    # Returns computed benevolence
    def compute(self):
        score = 0
        return score

    def _communicated_baby_gender(self):
        count = 0
        total = 0
        for i, action in self._actions:
            if type(action) is MessageAskGender:
                total += 1

        for j, action in self._actions:
            if type(action) is MessageBoy | type(action) is MessageGirl:
                count += 1

        if count > total:
            return 1

        return count / total

    def _communicated_yes_no(self):
        count = 0
        total = 0
        for i, action in self._actions:
            if type(action) is MessageRequestPickup:
                total += 1

        for j, action in self._actions:
            if type(action) is MessageYes | type(action) is MessageNo:
                count += 1

        if count > total:
            return 1

        return count / total

    def _communicated_room_search(self):
        count = 0
        total = 0
        for i, action in self._actions:
            if type(action) is EnterRoom:
                total += 1

        for j, action in self._actions:
            if type(action) is MessageSearch:
                count += 1

        if count > total:
            return 1

        return count / total
