import numpy as np

from actions1.AgentAction import MessageAskGender, MessageSuggestPickup
from actions1.HumanAction import MessageGirl, MessageBoy, MessageYes, PickUp, MessageFound, MessageSearch, EnterRoom, \
    MessagePickUp
from actions1.util import get_persons_in_room


class Integrity:
    def __init__(self, actions):
        self._actions = actions

    # Returns computed integrity
    def compute(self):
        metrics = [self._truth_identify_gender(), self._truth_suggested_pickup_yes(), self._truth_identify_person(),
                   self._truth_communicated_searched_rooms(), self._truth_pickup()]
        score = np.mean(metrics)
        return score

    # Returns ratio of truthfully identified baby genders
    def _truth_identify_gender(self):
        count = 0
        truth = 0

        for i, action in enumerate(self._actions):
            if type(action) is MessageAskGender:
                count += 1
                for j, other_action in enumerate(self._actions):
                    if i < j:  # Make sure to check only next actions
                        if type(other_action) is MessageGirl:  # Human identified a girl
                            # Check if a girl is in that room
                            for person in get_persons_in_room(action.room_name, action.map_state):
                                if person["name"].startswith("critically injured girl in area "):
                                    truth += 1
                                    break
                        elif type(other_action) is MessageBoy:
                            # Check if a boy is in that room
                            for person in get_persons_in_room(action.room_name, action.map_state):
                                if person["name"].startswith("critically injured boy in area "):
                                    truth += 1
                                    break
        if count == 0:
            return 1
        else:
            return truth / count

    # Returns ratio of truthfully pick ups after agent suggestion
    def _truth_suggested_pickup_yes(self):
        count = 0
        truth = 0

        for i, action in enumerate(self._actions):
            if type(action) is MessageSuggestPickup:
                for j, other_action in enumerate(self._actions):
                    if i < j:  # Make sure to check only next actions
                        if type(other_action) is MessageYes:
                            count += 1
                            for k, other_action_2 in enumerate(self._actions):
                                if i < j < k:  # Make sure to check only next actions
                                    if type(other_action_2) is PickUp:
                                        # check that next pickup is same person as communicated
                                        if action.person == other_action_2.person:
                                            truth += 1

        if count == 0:
            return 1
        else:
            return truth / count

    # Returns ratio of truthfully identified persons found by human
    def _truth_identify_person(self):
        count = 0
        truth = 0

        for i, action in enumerate(self._actions):
            if type(action) is MessageFound:
                count += 1
                for person in get_persons_in_room(action.room_name, action.map_state):
                    # check if identified person is in that room
                    if person["name"] == action.person:
                        truth += 1
                        break
        if count == 0:
            return 1
        else:
            return truth / count

    # Returns ratio of rooms the human does visit after communicating that he will visit them
    def _truth_communicated_searched_rooms(self):
        count = 0
        truth = 0
        for i, action in enumerate(self._actions):
            if type(action) is MessageSearch:
                count += 1
                for j, other_action in enumerate(self._actions):
                    if i < j:  # Make sure to check only next actions
                        if type(other_action) is EnterRoom:
                            # check if next room search is same room as communicated
                            if action.room_name == other_action.room_name:
                                truth += 1
                            break

        if count == 0:
            return 1
        else:
            return truth / count

    # Returns ratio of truthfully pick-ups after communicating with agent
    def _truth_pickup(self):
        count = 0
        truth = 0

        for i, action in enumerate(self._actions):
            if type(action) is MessagePickUp:
                count += 1
                for j, other_action in enumerate(self._actions):
                    if i < j:  # Make sure to check only next actions
                        if type(other_action) is PickUp:
                            # check if next pickup is same person as communicated
                            if action.person == other_action.person:
                                truth += 1

        if count == 0:
            return 1
        else:
            return truth / count
