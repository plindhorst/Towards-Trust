import glob
import json
import os
import pickle

from trustworthiness.Ability import Ability
from trustworthiness.Benevolence import Benevolence
from trustworthiness.Integrity import Integrity

VERBOSE = False


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


def _read_questionnaire_answers(file_name):
    f = open('./data/questionnaire/' + file_name)
    data = json.load(f)
    return data


def _actions_to_string(actions):
    for action in actions:
        new_attrs = []

        for attr in action.__dict__:
            if attr != "map_state":
                new_attrs.append({attr: action.__dict__[attr]})

        print(action.__class__.__name__, new_attrs)


def _compute_questionaire(answers):
    f = open('./trustworthiness/questionnaire.json')
    questions = json.load(f)

    abi = [0, 0, 0]
    counts = [0, 0, 0]

    for i, concept in enumerate(["Ability", "Benevolence", "Integrity"]):
        for question in questions:
            if question["type"] == concept:
                for answer in answers:
                    try:
                        abi[i] += int(answer[question["name"]])
                        counts[i] += 1
                        break
                    except KeyError:
                        continue
        abi[i] /= counts[i]

    abi = [round(x / 6, 2) for x in abi]

    return abi


def _compute(ability, benevolence, integrity):
    return round(ability.compute(), 2), round(benevolence.compute(), 2), round(integrity.compute(), 2)


class Trustworthiness:
    def __init__(self):
        list_of_files = glob.glob('./data/actions/*.pkl')

        if len(list_of_files) > 0:
            for action_file in list_of_files:
                action_file = action_file.replace("\\", "/")
                file_name = action_file.split("/")[-1].replace(".pkl", "")

                print("### ", file_name)

                actions = _read_action_file(action_file)

                # _actions_to_string(actions)

                ability = Ability(actions, verbose=VERBOSE)
                benevolence = Benevolence(actions, verbose=VERBOSE)
                integrity = Integrity(actions, verbose=VERBOSE)

                ability_score, benevolence_score, integrity_score = _compute(ability, benevolence, integrity)

                answers = _read_questionnaire_answers(file_name + ".json")
                abi_questionnaire = _compute_questionaire(answers)

                print("\n--- ABI score (metrics): ", [ability_score, benevolence_score, integrity_score])
                print("--- ABI score (questionnaire): ", abi_questionnaire, "\n")
