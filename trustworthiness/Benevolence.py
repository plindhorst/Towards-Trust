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
        metrics = [self._communicated_baby_gender(), self._communicated_yes_no(), self._communicated_room_search(),
                   self._communicated_pickup(), self._advice_followed(), self._average_ticks_to_respond()]

        self._average_ticks_to_respond()
        score = np.mean(metrics)
        return score

    # Returns the times the human replied to agent when it asked help for identifying gender of baby
    def _communicated_baby_gender(self):
        count = 0
        total = 0

        for action in self._actions:
            if type(action) is MessageAskGender:
                total += 1
            if type(action) is (MessageGirl or MessageBoy):
                count += 1

        print("Communicated baby gender: ", count, "/", total)

        if count > total or total == 0:
            return 1

        return count / total

    # returns ratio of communicated yes/no to the total number of pick-up suggestions.
    def _communicated_yes_no(self):
        count = 0
        total = 0

        for action in self._actions:
            # total number of agent pick-up suggestions
            if type(action) is MessageSuggestPickup:
                total += 1
            # total number of yes/no responses from human
            if type(action) is MessageYes or type(action) is MessageNo:
                count += 1

        print("Communicated yes/no:", count, "/", total)

        if count > total or total == 0:
            return 1

        return count or total

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

        return count or total

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

    # Return the ration of advices followed
    def _advice_followed(self):
        num_advice = 0
        num_advice_followed = 0
        victim = None

        for action in self._actions:
            if type(action) is MessageSuggestPickup:
                victim = action.person
                num_advice = num_advice + 1

            # The advice is only considered to have been followed if the human does not pick any other victim after
            # receiving the suggestion
            if type(action) is PickUp and victim is not None:
                if victim == action.person:
                    num_advice_followed = num_advice_followed + 1
                victim = None
        print("The ratio of advice followed by the human is : ", num_advice_followed, "/", num_advice)

        if num_advice == 0:
            return -1

        return num_advice_followed / num_advice

    # Returns the avergae number of ticks to respond to the agent
    def _average_ticks_to_respond(self):
        count = 0;
        ticks = 0;
        for action in self._actions:
            start = -1;
            end = -1;
            question = None
            if type(action) in [MessageAskGender, MessageSuggestPickup]:
                question = action
                start = action.map_state['tick']
            if (question is MessageAskGender and type(action) in [MessageGirl, MessageBoy] \
                    or question is MessageSuggestPickup and type(action) in [MessageYes, MessageNo]) and end > start:
                end = action.map_state['tick']
                ticks += end - start
                count += 1
                start = -1
                end = -1
        print("The average number of ticks to respond is :", ticks, "/", count)

        if count == 0:
            return -1

        return ticks/count
