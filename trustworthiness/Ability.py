import numpy as np

from actions1.util import NUMBER_OF_VICTIMS, is_correct_drop_location
from actions1.HumanAction import FoundVictim, PickUp

class Ability:
    def __init__(self, actions):
        self._actions = actions

    # Returns computed ability
    def compute(self):
        print("\nAbility:")
        metrics = [self._game_completion(), self._victim_found_ratios(),
                   self._victim_picked_ratios()]
        score = np.mean(metrics)
        return score

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
            if type(action) is PickUp :
                picked_up_victim_count = picked_up_victim_count + 1
        picked_up_ratio = picked_up_victim_count / NUMBER_OF_VICTIMS
        print("Ratio of victims picked up: ", picked_up_victim_count, "/", NUMBER_OF_VICTIMS, " = ", picked_up_ratio)

        return picked_up_victim_count / NUMBER_OF_VICTIMS