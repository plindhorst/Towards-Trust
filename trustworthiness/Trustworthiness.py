import os
import pickle

from trustworthiness.Ability import Ability
from trustworthiness.Benevolence import Benevolence
from trustworthiness.Integrity import Integrity


def _read_action_file(action_file):
    actions = []

    if not os.path.isfile(action_file):
        return

    with open(action_file, 'rb') as fr:
        try:
            while True:
                actions.append(pickle.load(fr))
        except EOFError:
            pass

    return actions


class Trustworthiness:
    def __init__(self, action_file):
        self._actions = _read_action_file(action_file)

        self._ability = Ability(self._actions)
        self._benevolence = Benevolence(self._actions)
        self._integrity = Integrity(self._actions)

    def actions_to_string(self):
        for action in self._actions:
            new_attrs = []

            for attr in action.__dict__:
                if attr != "map_state":
                    new_attrs.append({attr: action.__dict__[attr]})

            print(action.__class__.__name__, new_attrs)

    def compute(self):
        return self._ability.compute(), self._benevolence.compute(), self._integrity.compute()
