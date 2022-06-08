import numpy as np

from world.actions.AgentAction import MessageAskGender, MessageSuggestPickup
from world.actions.HumanAction import MessageBoy, MessageYes, MessageSearch, PickUp, MessagePickUp, \
    MessageFound, MessageGirl, FoundVictim, EnterUnvisitedRoom
from world.actions.util import is_in_room


class Benevolence:
    def __init__(self, actions, ticks, this_tick, verbose_lvl=0):
        self._actions = actions
        self._ticks = ticks
        self._this_tick = this_tick
        self.verbose_lvl = verbose_lvl

    # Returns computed benevolence
    def compute(self):

        if self.verbose_lvl == 2:
            print("\nBenevolence:")
        metrics = [self._communicated_baby_gender(), self._communicated_yes(), self._communicated_room_search(),
                   self._communicated_pickup(), self._advice_followed(), self._communicated_victims_found(),
                   self._average_ticks_to_respond()]
        score = np.mean(metrics)
        return score, metrics

    # Returns the times the human replied to agent when it asked help for identifying gender of baby
    def _communicated_baby_gender(self):
        count = 0
        total = 0

        for action in self._actions:
            if type(action) is MessageAskGender:
                total += 1
            if type(action) is MessageGirl or type(action) is MessageBoy:
                count += 1

        if self.verbose_lvl == 2:
            print("Communicated baby gender: ", count, "/", total)

        if count > total:
            return 1
        elif total == 0:
            return 0.5
        else:
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

        if self.verbose_lvl == 2:
            print("Communicated yes:", count, "/", total)

        if count > total:
            return 1
        elif total == 0:
            return 0.5
        else:
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

        if self.verbose_lvl == 2:
            print("Communicated room search: ", count, "/", total)

        if count > total:
            return 1
        elif total == 0:
            return 0.5
        else:
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

        if self.verbose_lvl == 2:
            print("Communicated pick up: ", count, "/", total)

        if count > total:
            return 1
        elif total == 0:
            return 0.5
        else:
            return count / total

    # Returns the ratio communicated victim found to actually found up victims
    def _communicated_victims_found(self):
        count = 0
        total = 0

        for action in self._actions:
            if type(action) is MessageFound:
                count += 1
            if type(action) is FoundVictim:
                total += 1

        if self.verbose_lvl == 2:
            print("Communicated victims found: ", count, "/", total)

        if count > total:
            return 1
        elif total == 0:
            return 0.5
        else:
            return count / total

    # Return the ration of advices followed
    def _advice_followed(self):
        count = 0
        total = 0
        victim = None

        for action in self._actions:
            if type(action) is MessageSuggestPickup:
                victim = action.person
                count += 1

            # The advice is only considered to have been followed if the human does not pick any other victim after
            # receiving the suggestion
            if type(action) is PickUp and victim is not None:
                if victim == action.person:
                    total += 1
                victim = None

        if self.verbose_lvl == 2:
            print("The ratio of advice followed by the human is : ", total, "/", count)

        if count > total:
            return 1
        elif total == 0:
            return 0.5
        else:
            return count / total

    # Returns the average number of ticks to respond to the agent
    def _average_ticks_to_respond(self):
        maximum = max(self._ticks)
        minimum = min(self._ticks)
        this = self._this_tick[0]
        if this == -1:
            this = maximum
        normalized = abs((this - maximum) / (minimum - maximum))

        if self.verbose_lvl == 2:
            print("Normalized response ticks: ", normalized, ", Number of Ticks: ", this)

        return normalized
