import numpy as np

from actions1.util import NUMBER_OF_VICTIMS, is_correct_drop_location


class Ability:
    def __init__(self, actions):
        self._actions = actions

    # Returns computed ability
    def compute(self):
        print("\nAbility:")
        metrics = [self._game_completion()]

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
