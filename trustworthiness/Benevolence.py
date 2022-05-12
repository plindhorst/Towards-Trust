from actions1.HumanAction import *
from actions1.AgentAction import MessageAskGender, MessageSuggestPickup


class Benevolence:
    def __init__(self, actions):
        self._actions = actions

    # Returns computed benevolence
    def compute(self):
        score = 0
        return score

    # Returns the times communicated victim found
    def _victim_found_no(self):
        count = 0

        for i, action in enumerate(self._actions):
            if type(action) is MessageFound:
                count += 1

        return count

    # Returns the times communicated victim picked up
    def _victim_picked_up_no(self):
        count = 0

        for i, action in enumerate(self._actions):
            if type(action) is MessagePickUp:
                count += 1

        return count

    # Returns the times the human replied to agent when it asked help for identifying gender of baby
    def _identify_gender(self):
        count = 0

        for i, action in enumerate(self._actions):
            if type(action) is MessageAskGender:
                for j, other_action in enumerate(self._actions):
                    if i < j:  # Make sure to check only next actions
                        if type(other_action) is (MessageGirl or MessageBoy):
                            count += 1

        return count

    # Returns the times the human replied to agent advices human to pick up a certain victim
    def suggested_pickup_yes_no(self):
        count = 0

        for i, action in enumerate(self._actions):
            if type(action) is MessageSuggestPickup:
                for j, other_action in enumerate(self._actions):
                    if i < j:  # Make sure to check only next actions
                        if type(other_action) is MessageYes:
                            count += 1

        return count


