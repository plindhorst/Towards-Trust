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


def _last_ticks(files):
    last_ticks = []

    for action_file in files:
        last_tick = 0
        if not os.path.isfile(action_file):
            return


        with open(action_file, 'rb') as fr:
            try:
                while True:
                    data = pickle.load(fr)
                    last_tick = data.__dict__["map_state"]['tick']

            except EOFError:
                pass

        last_ticks.append(last_tick)

    return last_ticks


def _actions_to_string(actions):
    for action in actions:
        new_attrs = []

        for attr in action.__dict__:
            if attr != "map_state":
                new_attrs.append({attr: action.__dict__[attr]})

        print(action.__class__.__name__, new_attrs)


def _compute(ability, benevolence, integrity):
    return round(ability.compute(), 2), round(benevolence.compute(), 2), round(integrity.compute(), 2)


# def _


class Trustworthiness:
    def __init__(self):
        list_of_files = glob.glob('./data/actions/*.pkl')

        if len(list_of_files) > 0:
            last_ticks = _last_ticks(list_of_files)
            for action_file in list_of_files:
                print("### ", action_file.split("\\")[-1])
                this_tick = _last_ticks([action_file])
                actions = _read_action_file(action_file)

                # _actions_to_string(actions)

                ability = Ability(actions, last_ticks, this_tick)
                benevolence = Benevolence(actions)
                integrity = Integrity(actions)

                ability_score, benevolence_score, integrity_score = _compute(ability, benevolence, integrity)

                print("\n--- ABI score: ", ability_score, benevolence_score, integrity_score, "\n")
