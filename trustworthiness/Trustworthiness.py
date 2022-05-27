import glob
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


def _actions_to_string(actions):
    for action in actions:
        new_attrs = []

        for attr in action.__dict__:
            if attr != "map_state":
                new_attrs.append({attr: action.__dict__[attr]})

        print(action.__class__.__name__, new_attrs)


def _compute(ability, benevolence, integrity):
    return round(ability.compute(), 2), round(benevolence.compute(), 2), round(integrity.compute(), 2)


class Trustworthiness:
    def __init__(self):
        list_of_files = glob.glob('./data/actions/*.pkl')

        if len(list_of_files) > 0:
            for action_file in list_of_files:
                print("### ", action_file.split("\\")[-1])

                actions = _read_action_file(action_file)

                # _actions_to_string(actions)

                ability = Ability(actions)
                benevolence = Benevolence(actions)
                integrity = Integrity(actions)

                ability_score, benevolence_score, integrity_score = _compute(ability, benevolence, integrity)

                print("\n--- ABI score: ", ability_score, benevolence_score, integrity_score, "\n")
