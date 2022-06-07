import glob
import json
import os
import pickle
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import pingouin as pg
from scipy.stats import skew

from trustworthiness.Ability import Ability
from trustworthiness.Benevolence import Benevolence
from trustworthiness.Integrity import Integrity
from world.actions.AgentAction import MessageAskGender, MessageSuggestPickup
from world.actions.HumanAction import MessageGirl, MessageYes, MessageBoy, MessageNo
from scipy import stats

VERBOSE = False
CONTROL_AGENT = 'control'
EXPERIMENTAL_AGENT = 'friendly'




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
    f = open('../data/questionnaire/' + file_name)
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
    f = open('./questionnaire.json')
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

def _PrintCronbachsAlpha():
    list_of_files = glob.glob('../data/questionnaire/*.json')
    jsonControlLists = [_read_questionnaire_answers(k[22:]) for k in list_of_files if (CONTROL_AGENT in k)]
    jsonExperimentalLists = [_read_questionnaire_answers(k[22:]) for k in list_of_files if (EXPERIMENTAL_AGENT in k)]

    transformedObjectsListControl = []
    transformedObjectsListExperimental = []

    for jsonControlList in jsonControlLists:
        fullObject = {}
        for d in jsonControlList:
            fullObject.update(d)
        transformedObjectsListControl.append(fullObject)

    for jsonExperimentalList in jsonExperimentalLists:
        fullObject = {}
        for d in jsonExperimentalList:
            fullObject.update(d)
        transformedObjectsListExperimental.append(fullObject)

    pandaFrameControl = pd.DataFrame.from_records(transformedObjectsListControl)
    pandaFrameControl = pandaFrameControl.apply(pd.to_numeric, args=('coerce',))
    pandaFrameExperimental = pd.DataFrame.from_records(transformedObjectsListExperimental)
    pandaFrameExperimental = pandaFrameExperimental.apply(pd.to_numeric, args=('coerce',))

    abilityControl = pandaFrameControl.iloc[:, 5:10]
    benevolenceControl = pandaFrameControl.iloc[:, 10:15]
    integrityControl = pandaFrameControl.iloc[:, 15:20]

    abilityExperimental = pandaFrameExperimental.iloc[:, 5:10]
    benevolenceExperimental = pandaFrameExperimental.iloc[:, 10:15]
    integrityExperimental = pandaFrameExperimental.iloc[:, 15:20]

    #Calculate cronbach_alpha
    print("Cronbach's alpha, control group, ability: ")
    print(pg.cronbach_alpha(data=abilityControl)[0])

    print("Cronbach's alpha, experimental group, ability: ")
    print(pg.cronbach_alpha(data=abilityExperimental)[0])

    print("Cronbach's alpha, control group, benevolence: ")
    print(pg.cronbach_alpha(data=benevolenceControl)[0])

    print("Cronbach's alpha, experimental group, benevolence: ")
    print(pg.cronbach_alpha(data=benevolenceExperimental)[0])

    print("Cronbach's alpha, control group, integrity: ")
    print(pg.cronbach_alpha(data=integrityControl)[0])

    print("Cronbach's alpha, experimental group, integrity: ")
    print(pg.cronbach_alpha(data=integrityExperimental)[0])

def _compute(ability, benevolence, integrity):
    return round(ability.compute(), 2), round(benevolence.compute(), 2), round(integrity.compute(), 2)


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
    def __init__(self):
        list_of_files = glob.glob('../data/actions/*.pkl')
        list_of_files = [k for k in list_of_files if (CONTROL_AGENT in k) or (EXPERIMENTAL_AGENT in k)]

        if len(list_of_files) > 0:
            control_ability_tw_s = []
            control_benevolence_tw_s = []
            control_integrity_tw_s = []
            control_tw_s = []

            control_ability_tw_o = []
            control_benevolence_tw_o = []
            control_integrity_tw_o = []
            control_tw_o = []

            experimental_ability_tw_o = []
            experimental_benevolence_tw_o = []
            experimental_integrity_tw_o = []
            experimental_tw_o = []

            experimental_ability_tw_s = []
            experimental_benevolence_tw_s = []
            experimental_integrity_tw_s = []
            experimental_tw_s = []


            last_ticks = _last_ticks(list_of_files)
            ticks_to_respond = _average_ticks_to_respond(list_of_files)

            # modify list for non-responsive values: -1.
            maximum = max(ticks_to_respond)
            for index, item in enumerate(ticks_to_respond):
                if item == -1:
                    ticks_to_respond[index] = maximum * 2

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

                ability_score, benevolence_score, integrity_score = _compute(ability, benevolence, integrity)
                answers = _read_questionnaire_answers(file_name + ".json")
                abi_questionnaire = _compute_questionaire(answers)

                trustworthiness_objective = np.mean([ability_score, benevolence_score, integrity_score])
                trustworthiness_subjective = np.mean(abi_questionnaire)

                if CONTROL_AGENT in file_name:

                    control_ability_tw_o.append(ability_score)
                    control_benevolence_tw_o.append(benevolence_score)
                    control_integrity_tw_o.append(integrity_score)
                    control_tw_o.append(trustworthiness_objective)

                    control_ability_tw_s.append(abi_questionnaire[0])
                    control_benevolence_tw_s.append(abi_questionnaire[1])
                    control_integrity_tw_s.append(abi_questionnaire[2])
                    control_tw_s.append(trustworthiness_subjective)

                elif EXPERIMENTAL_AGENT in file_name:
                    experimental_ability_tw_o.append(ability_score)
                    experimental_benevolence_tw_o.append(benevolence_score)
                    experimental_integrity_tw_o.append(integrity_score)
                    experimental_tw_o.append(trustworthiness_objective)

                    control_ability_tw_s.append(abi_questionnaire[0])
                    control_benevolence_tw_s.append(abi_questionnaire[1])
                    control_integrity_tw_s.append(abi_questionnaire[2])
                    experimental_tw_s.append(trustworthiness_subjective)

            print("CONTROL----------")
            print(control_tw_o)
            print(control_tw_s)
            shapiro_test_o = stats.shapiro(control_tw_o)
            shapiro_test_s = stats.shapiro(control_tw_s)
            print(shapiro_test_o)
            print(shapiro_test_s)

            print("EXPERIMENTAL----------")
            print(experimental_tw_o)
            print(experimental_tw_s)
            shapiro_test_o = stats.shapiro(experimental_tw_o)
            shapiro_test_s = stats.shapiro(experimental_tw_s)
            print(shapiro_test_o)
            print(shapiro_test_s)

            t_test_o = stats.ttest_ind(control_tw_o, experimental_tw_o)
            t_test_s = stats.ttest_ind(control_tw_s, experimental_tw_s)
            print("OBJECTIVE T-TEST: ")
            print(t_test_o)
            print("SUBJECTIVE T-TEST: ")
            print(t_test_s)
            plt.hist(control_tw_o, bins=7)
            plt.hist(experimental_tw_o, bins=7)
            plt.show()

            # print("\n--- ABI score (metrics): ", [ability_score, benevolence_score, integrity_score])
            # print("--- ABI score (questionnaire): ", abi_questionnaire, "\n")

Trustworthiness()