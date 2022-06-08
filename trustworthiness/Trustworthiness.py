import glob
import json
import os
import pickle

from trustworthiness.Ability import Ability
from trustworthiness.Benevolence import Benevolence
from trustworthiness.Integrity import Integrity
from trustworthiness.util_plots import plot_metrics
from world.actions.AgentAction import MessageAskGender, MessageSuggestPickup
from world.actions.HumanAction import MessageGirl, MessageYes, MessageBoy, MessageNo

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


def _average_ticks_to_respond(list_of_files):
    all_ticks_to_respond = []

    for action_file in list_of_files:
        actions = _read_action_file(action_file)
        count = 0
        ticks = 0
        start = 0
        question = None

        for action in actions:
            tick = action.map_state['tick']

            if type(action) in [MessageAskGender, MessageSuggestPickup]:
                question = action
                start = tick

            if (type(question) is MessageAskGender and type(action) in [MessageGirl, MessageBoy] \
                    or type(question) is MessageSuggestPickup and type(action) in [MessageYes, MessageNo]):
                ticks += tick - start
                count += 1
                question = None

        if count == 0:
            all_ticks_to_respond.append(-1)
        else:
            all_ticks_to_respond.append(ticks / count)

    return all_ticks_to_respond


class Trustworthiness:
    def __init__(self, group="control", graphs=False):
        list_of_files = glob.glob('./data/actions/' + group + '_*.pkl')

        if len(list_of_files) > 0:
            last_ticks = _last_ticks(list_of_files)
            ticks_to_respond = _average_ticks_to_respond(list_of_files)

            # modify list for non-responsive values: -1.
            maximum = max(ticks_to_respond)
            for index, item in enumerate(ticks_to_respond):
                if item == -1:
                    ticks_to_respond[index] = maximum * 2

            metrics = []
            for action_file in list_of_files:
                this_tick = _last_ticks([action_file])
                this_tick_to_respond = _average_ticks_to_respond([action_file])
                action_file = action_file.replace("\\", "/")
                file_name = action_file.split("/")[-1].replace(".pkl", "")

                print("### ", file_name)

                actions = _read_action_file(action_file)

                # _actions_to_string(actions)

                ability = Ability(actions, last_ticks, this_tick, verbose=VERBOSE)
                benevolence = Benevolence(actions, ticks_to_respond, this_tick_to_respond, verbose=VERBOSE)
                integrity = Integrity(actions, verbose=VERBOSE)

                ability_score, ability_metrics = ability.compute()
                benevolence_score, benevolence_metrics = benevolence.compute()
                integrity_score, integrity_metrics = integrity.compute()

                metrics.append([ability_metrics, benevolence_metrics, integrity_metrics])

                answers = _read_questionnaire_answers(file_name + ".json")
                abi_questionnaire = _compute_questionaire(answers)

                print("\n--- ABI score (metrics): ", [ability_score, benevolence_score, integrity_score])
                print("--- ABI score (questionnaire): ", abi_questionnaire, "\n")

            plot_metrics(metrics)
