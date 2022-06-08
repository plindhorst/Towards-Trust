import numpy as np

from world.actions.util import NUMBER_OF_VICTIMS, is_correct_drop_location, ROOMS
from world.actions.HumanAction import FoundVictim, PickUp, EnterRoom


class Ability:
    def __init__(self, actions, ticks, this_tick, verbose_lvl=0):
        self._actions = actions
        self._last_ticks = ticks
        self._this_tick = this_tick
        self.verbose_lvl = verbose_lvl

    # Returns computed ability
    def compute(self):

        if self.verbose_lvl == 2:
            print("\nAbility:")

        metrics = [self._game_completion(), self._victim_found_ratios(),
                   self._victim_picked_ratios(), self._rooms_visited(), self._normalized_tick()]
        score = np.mean(metrics)
        return score, metrics

    def _normalized_tick(self):
        maximum = max(self._last_ticks)
        minimum = min(self._last_ticks)
        this = self._this_tick[0]
        normalized = abs((this - maximum) / (minimum - maximum))

        if self.verbose_lvl == 2:
            print("Normalized Ticks: ", normalized, ", Number of Ticks: ", this)

        return normalized

    # Returns the ratio of correctly dropped off victims by the total amount of victims needed to be dropped-off
    def _game_completion(self):
        count = 0
        last_map_state = self._actions[-1].map_state
        for person in last_map_state["persons"]:
            if is_correct_drop_location(person["name"], person["location"]):
                count += 1

        count += len(self._actions[0].map_state["persons"]) - len(
            self._actions[-1].map_state["persons"])  # add persons that are carried

        if self.verbose_lvl == 2:
            print("Game completion: ", count, "/", NUMBER_OF_VICTIMS)

        if count > NUMBER_OF_VICTIMS:
            return 1

        return count / NUMBER_OF_VICTIMS

    # returns the ratio of victims found
    def _victim_found_ratios(self):
        found_victim_count = 0
        for action in self._actions:
            if type(action) is FoundVictim and found_victim_count != NUMBER_OF_VICTIMS:
                found_victim_count = found_victim_count + 1

        if self.verbose_lvl == 2:
            print("Ratio of victims found: ", found_victim_count, "/", NUMBER_OF_VICTIMS)

        if found_victim_count > NUMBER_OF_VICTIMS:
            return 1
        return found_victim_count / NUMBER_OF_VICTIMS

    # returns the ratio of victim picked up by the human
    def _victim_picked_ratios(self):
        picked_up_victim_count = 0
        for action in self._actions:
            if type(action) is PickUp:
                picked_up_victim_count = picked_up_victim_count + 1

        if self.verbose_lvl == 2:
            print("Ratio of victims picked up: ", picked_up_victim_count, "/", NUMBER_OF_VICTIMS)

        if picked_up_victim_count > NUMBER_OF_VICTIMS:
            return 1

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

        if self.verbose_lvl == 2:
            print("Rooms visited: ", count, "/", number_of_rooms)

        if count > number_of_rooms:
            return 1

        return count / number_of_rooms
