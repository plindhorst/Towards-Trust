import numpy as np

from actions1.HumanAction import EnterRoom
from actions1.util import NUMBER_OF_VICTIMS, is_correct_drop_location, ROOMS


class Ability:
    def __init__(self, actions):
        self._actions = actions

    # Returns computed ability
    def compute(self):
        print("\nAbility:")
        metrics = [self._game_completion(), self._rooms_visited()]

        score = np.mean(metrics)
        return score

    # Returns the ratio of correctly dropped off victims by the total amount of victims needed to be dropped-off
    def _game_completion(self):
        count = 0
        last_map_state = self._actions[-1].map_state
        for person in last_map_state["persons"]:
            if is_correct_drop_location(person["name"], person["location"]):
                count += 1

        print("Game completion: ", count, "/", NUMBER_OF_VICTIMS)

        return count / NUMBER_OF_VICTIMS

    # Returns the ratio of number of rooms visited by human by the total amount of rooms
    def _rooms_visited(self):
        number_of_rooms = len(ROOMS)
        count = 0
        visited_rooms = []
        for action in self._actions:
            if type(action) is EnterRoom:
                if action.room_name not in visited_rooms:
                    visited_rooms.append(action.room_name)
                    count += 1

        print("Rooms visited: ", count, "/", number_of_rooms)

        return count / NUMBER_OF_VICTIMS
