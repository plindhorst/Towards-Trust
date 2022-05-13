import numpy as np

from actions1.AgentAction import MessageAskGender, MessageSuggestPickup
from actions1.HumanAction import MessageBoy, MessageYes, MessageNo, MessageSearch, PickUp, MessagePickUp, \
    MessageFound, MessageGirl, FoundVictim, EnterUnvisitedRoom
from actions1.util import is_in_room


class Benevolence:
    def __init__(self, actions):
        self._actions = actions

    # Returns computed benevolence
    def compute(self):

        print("\nBenevolence:")
        metrics = [self._communicated_baby_gender(), self._communicated_yes(), self._communicated_room_search(),
                   self._communicated_pickup()]

        score = np.mean(metrics)
        return score

    # Returns the times the human replied to agent when it asked help for identifying gender of baby
    def _communicated_baby_gender(self):
        count = 0
        total = 0

        for action in self._actions:
            if type(action) is MessageAskGender:
                total += 1
            if type(action) is MessageGirl or type(action) is MessageBoy:
                count += 1

        print("Communicated baby gender: ", count, "/", total)

        if count > total or total == 0:
            return 1

        return count / total

    # returns ratio of communicated yes to the total number of pick-up suggestions.
    def _communicated_yes(self):
        count = 0
        total = 0

        for action in self._actions:
            # total number of agent pick-up suggestions
            if type(action) is MessageSuggestPickup:
                total += 1
            # total number of yes responses from human
            if type(action) is MessageYes:
                count += 1

        print("Communicated yes:", count, "/", total)

        if count > total or total == 0:
            return 1

        return count / total

    # return ratio of communicated room search to total number of room search actions.
    def _communicated_room_search(self):
        count = 0
        total = 0

        for action in self._actions:
            # total number of rooms searched by human agent
            if type(action) is EnterUnvisitedRoom:
                total += 1
            # total number of rooms searches communicated by human agent.
            if type(action) is MessageSearch:
                count += 1

        print("Communicated room search: ", count, "/", total)

        if count > total or total == 0:
            return 1

        return count / total

    # return ratio of communicated pick-ups to total number of pick-up actions.
    def _communicated_pickup(self):
        count = 0
        total = 0

        # total number of pick-ups by human agent.
        for action in self._actions:
            if type(action) is PickUp:
                # we ensure that the pick-up occurs in the room where the patient is found.
                # this is done to discard pick-ups that might happen for rearrangement purposes.
                action_room = is_in_room(action.location)
                if action_room is not None:
                    total += 1

        # total number of communicated pick-ups by human agent.
        for action in self._actions:
            if type(action) is MessagePickUp:
                count += 1

        print("Communicated pick up: ", count, "/", total)

        if count > total or total == 0:
            return 1

        return count / total

    # Returns the ratio communicated victim found to actually found up victims
    def _communicated_victims_found(self):
        count = 0
        total = 0

        for action in self._actions:
            if type(action) is MessageFound:
                total += 1
            if type(action) is FoundVictim:
                count += 1

        if count > total or total == 0:
            return 1

        return count / total
