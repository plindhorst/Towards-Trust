import numpy as np

from world.actions.util import NUMBER_OF_VICTIMS, is_correct_drop_location, ROOMS
from world.actions.HumanAction import FoundVictim, PickUp, EnterRoom


class Ability:
    def __init__(self, actions):
        self._actions = actions

    # Returns computed ability
    def compute(self):
        print("\nAbility:")

        metrics = [self._game_completion(), self._victim_found_ratios(),
                   self._victim_picked_ratios(), self._rooms_visited()]
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

    # returns the ratio of vicims found
    def _victim_found_ratios(self):
        found_victim_count = 0
        for action in self._actions:
            if type(action) is FoundVictim and found_victim_count != NUMBER_OF_VICTIMS:
                found_victim_count = found_victim_count + 1
        found_ratio = found_victim_count / NUMBER_OF_VICTIMS
        print("Ratio of victims found: ", found_victim_count, "/", NUMBER_OF_VICTIMS, " = ", found_ratio)

        return found_victim_count / NUMBER_OF_VICTIMS

    # returns the ratio of victim picked up by the human
    def _victim_picked_ratios(self):
        picked_up_victim_count = 0
        for action in self._actions:
            if type(action) is PickUp:
                picked_up_victim_count = picked_up_victim_count + 1
        picked_up_ratio = picked_up_victim_count / NUMBER_OF_VICTIMS
        print("Ratio of victims picked up: ", picked_up_victim_count, "/", NUMBER_OF_VICTIMS, " = ", picked_up_ratio)

        return picked_up_victim_count / NUMBER_OF_VICTIMS

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
