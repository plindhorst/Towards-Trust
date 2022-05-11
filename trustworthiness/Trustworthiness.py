import os
import pickle

from trustworthiness.Ability import Ability
from trustworthiness.Benevolence import Benevolence
from trustworthiness.Integrity import Integrity

ACTION_FILE = "./actions.pkl"


def _read_action_file():
    actions = []

    if not os.path.isfile(ACTION_FILE):
        return

    with open(ACTION_FILE, 'rb') as fr:
        try:
            while True:
                actions.append(pickle.load(fr))
        except EOFError:
            pass

    return actions


class Trustworthiness:
    def __init__(self):
        self._actions = _read_action_file()

        self._ability = Ability(self._actions)
        self._benevolence = Benevolence(self._actions)
        self._integrity = Integrity(self._actions)

    def actions_to_string(self):
        for action in self._actions:
            print(action)

    def compute(self):
        return self._ability.compute(), self._benevolence.compute(), self._integrity.compute()