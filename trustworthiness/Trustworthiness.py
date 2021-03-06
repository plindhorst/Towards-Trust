import glob
import json
import os
import pickle
import statistics

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import pingouin as pg
from scipy.stats import skew
import seaborn as sns

from trustworthiness.Ability import Ability
from trustworthiness.Benevolence import Benevolence
from trustworthiness.Integrity import Integrity
from world.actions.AgentAction import MessageAskGender, MessageSuggestPickup
from world.actions.HumanAction import MessageGirl, MessageYes, MessageBoy, MessageNo, MessageHelp
from scipy import stats

VERBOSE = False
CONTROL_AGENT = 'control'
EXPERIMENTAL_AGENT = 'advice'


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

    # Calculate cronbach_alpha
    print("\nCronbach's alpha, control group, ability: ")
    print("\t" + str(pg.cronbach_alpha(data=abilityControl)[0]))

    print("\nCronbach's alpha, experimental group, ability: ")
    print("\t" + str(pg.cronbach_alpha(data=abilityExperimental)[0]))

    print("\nCronbach's alpha, control group, benevolence: ")
    print("\t" + str(pg.cronbach_alpha(data=benevolenceControl)[0]))

    print("\nCronbach's alpha, experimental group, benevolence: ")
    print("\t" + str(pg.cronbach_alpha(data=benevolenceExperimental)[0]))

    print("\nCronbach's alpha, control group, integrity: ")
    print("\t" + str(pg.cronbach_alpha(data=integrityControl)[0]))

    print("\nCronbach's alpha, experimental group, integrity: ")
    print("\t" + str(pg.cronbach_alpha(data=integrityExperimental)[0]))


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


def _printShapiroResult(result):
    if result < 0.05:
        print("\t" + str(result) + " NOT NORMALLY DISTRIBUTED")
    else:
        print("\t" + str(result) + " NORMALLY DISTRIBUTED")


def _printSignificanceTest(shapiroResultControl, shapiroResultExperimental, controlData, experimentalData):
    if shapiroResultControl >= 0.05 and shapiroResultExperimental >= 0.05:
        print("T-Test: ")
        ttestValue = stats.ttest_ind(controlData, experimentalData)
        if (ttestValue.pvalue < 0.05):
            print("\t" + str(ttestValue) + " SIGNIFICANT")
        else:
            print("\t" + str(ttestValue) + " NOT SIGNIFICANT")
    else:
        print("mann-Whitney test: ")
        mannWhitneyUValue = stats.mannwhitneyu(controlData, experimentalData)
        if (mannWhitneyUValue.pvalue < 0.05):
            print("\t" + str(mannWhitneyUValue) + " SIGNIFICANT")
        else:
            print("\t" + str(mannWhitneyUValue) + " NOT SIGNIFICANT")


class Trustworthiness:
    def __init__(self):
        list_of_files = glob.glob('../data/actions/*.pkl')
        list_of_files = [k for k in list_of_files if (CONTROL_AGENT in k) or (EXPERIMENTAL_AGENT in k)]

        if len(list_of_files) > 0:
            help_counters = []
            help_trustworthiness = []
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


            for action_file in list_of_files:
                this_tick = _last_ticks([action_file])
                this_tick_to_respond = _average_ticks_to_respond([action_file])
                action_file = action_file.replace("\\", "/")
                file_name = action_file.split("/")[-1].replace(".pkl", "")

                print("### ", file_name)

                list_of_tick_files = [k for k in list_of_files if (EXPERIMENTAL_AGENT in k)]
                if CONTROL_AGENT in file_name:
                    list_of_tick_files = [k for k in list_of_files if (CONTROL_AGENT in k)]

                last_ticks = _last_ticks(list_of_tick_files)
                ticks_to_respond = _average_ticks_to_respond(list_of_tick_files)

                # modify list for non-responsive values: -1.
                maximum = max(ticks_to_respond)
                for index, item in enumerate(ticks_to_respond):
                    if item == -1:
                        ticks_to_respond[index] = maximum


                actions = _read_action_file(action_file)

                # _actions_to_string(actions)

                ability = Ability(actions, last_ticks, this_tick, verbose=VERBOSE)
                benevolence = Benevolence(actions, ticks_to_respond, this_tick_to_respond, verbose=VERBOSE)
                integrity = Integrity(actions, verbose=VERBOSE)

                ability_score, benevolence_score, integrity_score = _compute(ability, benevolence, integrity)
                answers = _read_questionnaire_answers(file_name + ".json")
                abi_questionnaire = _compute_questionaire(answers)

                trustworthiness_objective = np.mean([ability_score, benevolence_score, integrity_score])
                print(trustworthiness_objective)
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
                    help_count = 0

                    for act in actions:

                        if type(act) is MessageHelp:
                            # print(act)
                            # print(action_file)
                            help_count += 1

                    if help_count > 0:
                        help_counters.append(help_count)
                        help_trustworthiness.append(trustworthiness_objective)
                    # print(help_counters)
                    experimental_ability_tw_o.append(ability_score)
                    experimental_benevolence_tw_o.append(benevolence_score)
                    experimental_integrity_tw_o.append(integrity_score)
                    experimental_tw_o.append(trustworthiness_objective)

                    experimental_ability_tw_s.append(abi_questionnaire[0])
                    experimental_benevolence_tw_s.append(abi_questionnaire[1])
                    experimental_integrity_tw_s.append(abi_questionnaire[2])
                    experimental_tw_s.append(trustworthiness_subjective)
            coef_corr = np.corrcoef(help_counters, help_trustworthiness)
            print("\n\nPEARSON CORRELATION: ", coef_corr, "\n\n")

            print("### STATISTICS OF DISTRIBUTION EXPERIMENTAL GROUP:")
            variance_exp = statistics.mean(experimental_tw_o)
            variance_a_exp = statistics.mean(experimental_ability_tw_o)
            variance_b_exp = statistics.mean(experimental_benevolence_tw_o)
            variance_i_exp = statistics.mean(experimental_integrity_tw_o)
            print("MEAN TW EXPERIMENTAL: ", round(variance_exp, 3))
            print("MEAN ABILITY EXPERIMENTAL: ",  round(variance_a_exp, 3))
            print("MEAN BENEVOLENCE EXPERIMENTAL: ",  round(variance_b_exp, 3))
            print("MEAN INTEGRITY EXPERIMENTAL: ",  round(variance_i_exp, 3))
            variance_exp = statistics.variance(experimental_tw_o)
            variance_a_exp = statistics.variance(experimental_ability_tw_o)
            variance_b_exp = statistics.variance(experimental_benevolence_tw_o)
            variance_i_exp = statistics.variance(experimental_integrity_tw_o)
            print("VARIANCE TW EXPERIMENTAL: ",  round(variance_exp, 3))
            print("VARIANCE ABILITY EXPERIMENTAL: ",  round(variance_a_exp, 3))
            print("VARIANCE BENEVOLENCE EXPERIMENTAL: ",  round(variance_b_exp, 3))
            print("VARIANCE INTEGRITY EXPERIMENTAL: ",  round(variance_i_exp, 3))
            variance_exp = statistics.stdev(experimental_tw_o)
            variance_a_exp = statistics.stdev(experimental_ability_tw_o)
            variance_b_exp = statistics.stdev(experimental_benevolence_tw_o)
            variance_i_exp = statistics.stdev(experimental_integrity_tw_o)
            print("STD TW EXPERIMENTAL: ",  round(variance_exp, 3))
            print("STD ABILITY EXPERIMENTAL: ",  round(variance_a_exp, 3))
            print("STD BENEVOLENCE EXPERIMENTAL: ",  round(variance_b_exp, 3))
            print("STD INTEGRITY EXPERIMENTAL: ",  round(variance_i_exp, 3))
            variance_exp = skew(experimental_tw_o)
            variance_a_exp = skew(experimental_ability_tw_o)
            variance_b_exp = skew(experimental_benevolence_tw_o)
            variance_i_exp = skew(experimental_integrity_tw_o)
            print("SKEW TW EXPERIMENTAL: ", round(variance_exp, 3))
            print("SKEW ABILITY EXPERIMENTAL: ",round(variance_a_exp, 3))
            print("SKEW BENEVOLENCE EXPERIMENTAL: ", round(variance_b_exp, 3))
            print("SKEW INTEGRITY EXPERIMENTAL: ", round(variance_i_exp, 3))


            print("### STATISTICS OF DISTRIBUTION CONTROL GROUP:")
            variance_exp = statistics.mean(control_tw_o)
            variance_a_exp = statistics.mean(control_ability_tw_o)
            variance_b_exp = statistics.mean(control_benevolence_tw_o)
            variance_i_exp = statistics.mean(control_integrity_tw_o)
            print("MEAN TW CONTROL: ", round(variance_exp, 3))
            print("MEAN ABILITY  CONTROL: ",round(variance_a_exp, 3))
            print("MEAN BENEVOLENCE  CONTROL: ", round(variance_b_exp, 3))
            print("MEAN INTEGRITY  CONTROL: ", round(variance_i_exp, 3))
            variance_exp = statistics.variance(control_tw_o)
            variance_a_exp = statistics.variance(control_ability_tw_o)
            variance_b_exp = statistics.variance(control_benevolence_tw_o)
            variance_i_exp = statistics.variance(control_integrity_tw_o)
            print("VARIANCE TW  CONTROL: ", round(variance_exp, 3))
            print("VARIANCE ABILITY  CONTROL: ",round(variance_a_exp, 3))
            print("VARIANCE BENEVOLENCE  CONTROL: ", round(variance_b_exp, 3))
            print("VARIANCE INTEGRITY  CONTROL: ", round(variance_i_exp, 3))
            variance_exp = statistics.stdev(control_tw_o)
            variance_a_exp = statistics.stdev(control_ability_tw_o)
            variance_b_exp = statistics.stdev(control_benevolence_tw_o)
            variance_i_exp = statistics.stdev(control_integrity_tw_o)
            print("STD TW  CONTROL: ", round(variance_exp, 3))
            print("STD ABILITY  CONTROL: ",round(variance_a_exp, 3))
            print("STD BENEVOLENCE  CONTROL: ", round(variance_b_exp, 3))
            print("STD INTEGRITY  CONTROL: ", round(variance_i_exp, 3))
            variance_exp = skew(control_tw_o)
            variance_a_exp = skew(control_ability_tw_o)
            variance_b_exp = skew(control_benevolence_tw_o)
            variance_i_exp = skew(control_integrity_tw_o)
            print("SKEW TW  CONTROL: ", round(variance_exp, 3))
            print("SKEW ABILITY  CONTROL: ",round(variance_a_exp, 3))
            print("SKEW BENEVOLENCE  CONTROL: ", round(variance_b_exp, 3))
            print("SKEW INTEGRITY  CONTROL: ", round(variance_i_exp, 3))


            print("\n SUBJECTIVE \n")

            print("### STATISTICS OF DISTRIBUTION EXPERIMENTAL GROUP:")
            variance_exp = statistics.mean(experimental_tw_s)
            variance_a_exp = statistics.mean(experimental_ability_tw_s)
            variance_b_exp = statistics.mean(experimental_benevolence_tw_s)
            variance_i_exp = statistics.mean(experimental_integrity_tw_s)
            print("MEAN TW EXPERIMENTAL: ", round(variance_exp, 3))
            print("MEAN ABILITY EXPERIMENTAL: ", round(variance_a_exp, 3))
            print("MEAN BENEVOLENCE EXPERIMENTAL: ", round(variance_b_exp, 3))
            print("MEAN INTEGRITY EXPERIMENTAL: ", round(variance_i_exp, 3))
            variance_exp = statistics.variance(experimental_tw_s)
            variance_a_exp = statistics.variance(experimental_ability_tw_s)
            variance_b_exp = statistics.variance(experimental_benevolence_tw_s)
            variance_i_exp = statistics.variance(experimental_integrity_tw_s)
            print("VARIANCE TW EXPERIMENTAL: ", round(variance_exp, 3))
            print("VARIANCE ABILITY EXPERIMENTAL: ", round(variance_a_exp, 3))
            print("VARIANCE BENEVOLENCE EXPERIMENTAL: ", round(variance_b_exp, 3))
            print("VARIANCE INTEGRITY EXPERIMENTAL: ", round(variance_i_exp, 3))
            variance_exp = statistics.stdev(experimental_tw_s)
            variance_a_exp = statistics.stdev(experimental_ability_tw_s)
            variance_b_exp = statistics.stdev(experimental_benevolence_tw_s)
            variance_i_exp = statistics.stdev(experimental_integrity_tw_s)
            print("STD TW EXPERIMENTAL: ", round(variance_exp, 3))
            print("STD ABILITY EXPERIMENTAL: ", round(variance_a_exp, 3))
            print("STD BENEVOLENCE EXPERIMENTAL: ", round(variance_b_exp, 3))
            print("STD INTEGRITY EXPERIMENTAL: ", round(variance_i_exp, 3))
            variance_exp = skew(experimental_tw_s)
            variance_a_exp = skew(experimental_ability_tw_s)
            variance_b_exp = skew(experimental_benevolence_tw_s)
            variance_i_exp = skew(experimental_integrity_tw_s)
            print("SKEW TW EXPERIMENTAL: ", round(variance_exp, 3))
            print("SKEW ABILITY EXPERIMENTAL: ", round(variance_a_exp, 3))
            print("SKEW BENEVOLENCE EXPERIMENTAL: ", round(variance_b_exp, 3))
            print("SKEW INTEGRITY EXPERIMENTAL: ", round(variance_i_exp, 3))

            print("### STATISTICS OF DISTRIBUTION CONTROL GROUP:")
            variance_exp = statistics.mean(control_tw_s)
            variance_a_exp = statistics.mean(control_ability_tw_s)
            variance_b_exp = statistics.mean(control_benevolence_tw_s)
            variance_i_exp = statistics.mean(control_integrity_tw_s)
            print("MEAN TW CONTROL: ", round(variance_exp, 3))
            print("MEAN ABILITY  CONTROL: ", round(variance_a_exp, 3))
            print("MEAN BENEVOLENCE  CONTROL: ", round(variance_b_exp, 3))
            print("MEAN INTEGRITY  CONTROL: ", round(variance_i_exp, 3))
            variance_exp = statistics.variance(control_tw_s)
            variance_a_exp = statistics.variance(control_ability_tw_s)
            variance_b_exp = statistics.variance(control_benevolence_tw_s)
            variance_i_exp = statistics.variance(control_integrity_tw_s)
            print("VARIANCE TW  CONTROL: ", round(variance_exp, 3))
            print("VARIANCE ABILITY  CONTROL: ", round(variance_a_exp, 3))
            print("VARIANCE BENEVOLENCE  CONTROL: ", round(variance_b_exp, 3))
            print("VARIANCE INTEGRITY  CONTROL: ", round(variance_i_exp, 3))
            variance_exp = statistics.stdev(control_tw_s)
            variance_a_exp = statistics.stdev(control_ability_tw_s)
            variance_b_exp = statistics.stdev(control_benevolence_tw_s)
            variance_i_exp = statistics.stdev(control_integrity_tw_s)
            print("STD TW  CONTROL: ", round(variance_exp, 3))
            print("STD ABILITY  CONTROL: ", round(variance_a_exp, 3))
            print("STD BENEVOLENCE  CONTROL: ", round(variance_b_exp, 3))
            print("STD INTEGRITY  CONTROL: ", round(variance_i_exp, 3))
            variance_exp = skew(control_tw_s)
            variance_a_exp = skew(control_ability_tw_s)
            variance_b_exp = skew(control_benevolence_tw_s)
            variance_i_exp = skew(control_integrity_tw_s)
            print("SKEW TW  CONTROL: ", round(variance_exp, 3))
            print("SKEW ABILITY  CONTROL: ", round(variance_a_exp, 3))
            print("SKEW BENEVOLENCE  CONTROL: ", round(variance_b_exp, 3))
            print("SKEW INTEGRITY  CONTROL: ", round(variance_i_exp, 3))

            shapiro_control_ability_o = stats.shapiro(control_ability_tw_o).pvalue
            shapiro_control_benevolence_o = stats.shapiro(control_benevolence_tw_o).pvalue
            shapiro_control_integrity_o = stats.shapiro(control_integrity_tw_o).pvalue
            shapiro_control_o = stats.shapiro(control_tw_o).pvalue

            shapiro_control_ability_s = stats.shapiro(control_ability_tw_s).pvalue
            shapiro_control_benevolence_s = stats.shapiro(control_benevolence_tw_s).pvalue
            shapiro_control_integrity_s = stats.shapiro(control_integrity_tw_s).pvalue
            shapiro_control_s = stats.shapiro(control_tw_s).pvalue

            shapiro_experimental_ability_o = stats.shapiro(experimental_ability_tw_o).pvalue
            shapiro_experimental_benevolence_o = stats.shapiro(experimental_benevolence_tw_o).pvalue
            shapiro_experimental_integrity_o = stats.shapiro(experimental_integrity_tw_o).pvalue
            shapiro_experimental_o = stats.shapiro(experimental_tw_o).pvalue

            shapiro_experimental_ability_s = stats.shapiro(experimental_ability_tw_s).pvalue
            shapiro_experimental_benevolence_s = stats.shapiro(experimental_benevolence_tw_s).pvalue
            shapiro_experimental_integrity_s = stats.shapiro(experimental_integrity_tw_s).pvalue
            shapiro_experimental_s = stats.shapiro(experimental_tw_s).pvalue

            print("\n cronbachs alpha:")
            _PrintCronbachsAlpha()

            print("\n Shapiro-Wilk test:")
            print("\n control group - objective - ability:")
            _printShapiroResult(shapiro_control_ability_o)
            print("\n control group - objective - benevolence:")
            _printShapiroResult(shapiro_control_benevolence_o)
            print("\n control group - objective - integrity:")
            _printShapiroResult(shapiro_control_integrity_o)
            print("\n control group - objective - trustworthiness")
            _printShapiroResult(shapiro_control_o)

            print("\n control group - subjective - ability:")
            _printShapiroResult(shapiro_control_ability_s)
            print("\n control group - subjective - benevolence:")
            _printShapiroResult(shapiro_control_benevolence_s)
            print("\n control group - subjective - integrity:")
            _printShapiroResult(shapiro_control_integrity_s)
            print("\n control group - subjective - trustworthiness")
            _printShapiroResult(shapiro_control_s)

            print("\n experimental group - objective - ability:")
            _printShapiroResult(shapiro_experimental_ability_o)
            print("\n experimental group - objective - benevolence:")
            _printShapiroResult(shapiro_experimental_benevolence_o)
            print("\n experimental group - objective - integrity:")
            _printShapiroResult(shapiro_experimental_integrity_o)
            print("\n experimental group - objective - trustworthiness:")
            _printShapiroResult(shapiro_experimental_o)

            print("\n experimental group - subjective - ability:")
            _printShapiroResult(shapiro_experimental_ability_s)
            print("\n experimental group - subjective - benevolence:")
            _printShapiroResult(shapiro_experimental_benevolence_s)
            print("\n experimental group - subjective - integrity:")
            _printShapiroResult(shapiro_experimental_integrity_s)
            print("\n experimental group - subjective - trustworthiness:")
            _printShapiroResult(shapiro_experimental_s)

            print("\nsignificance test: ")
            print("\n\tobjective - ability - ", end="")
            _printSignificanceTest(shapiro_control_ability_o, shapiro_experimental_ability_o, control_ability_tw_o,
                                   experimental_ability_tw_o)

            print("\n\tobjective - benevolence - ", end="")
            _printSignificanceTest(shapiro_control_benevolence_o, shapiro_experimental_benevolence_o,
                                   control_benevolence_tw_o, experimental_benevolence_tw_o)

            print("\n\tobjective - integrity - ", end="")
            _printSignificanceTest(shapiro_control_integrity_o, shapiro_experimental_integrity_o,
                                   control_integrity_tw_o, experimental_integrity_tw_o)

            print("\n\tobjective - trustworthiness - ", end="")
            _printSignificanceTest(shapiro_control_o, shapiro_experimental_o, control_tw_o, experimental_tw_o)

            print("\n\tsubjective - ability - ", end="")
            _printSignificanceTest(shapiro_control_ability_s, shapiro_experimental_ability_s, control_ability_tw_s,
                                   experimental_ability_tw_s)

            print("\n\tsubjective - benevolence - ", end="")
            _printSignificanceTest(shapiro_control_benevolence_s, shapiro_experimental_benevolence_s,
                                   control_benevolence_tw_s, experimental_benevolence_tw_s)

            print("\n\tsubjective - integrity - ", end="")
            _printSignificanceTest(shapiro_control_integrity_s, shapiro_experimental_integrity_s,
                                   control_integrity_tw_s, experimental_integrity_tw_s)

            print("\n\tsubjective - trustworthiness - ", end="")
            _printSignificanceTest(shapiro_control_s, shapiro_experimental_s, control_tw_s, experimental_tw_s)

            # plt.scatter(help_counters, help_trustworthiness, alpha=0.5)
            # plt.plot(help_counters,help_trustworthiness)
            # m, b = np.polyfit(help_counters, help_trustworthiness,)
            # plt.plot(help_counters, m * help_counters + b)
            # plt.show()


            # Trusworthiness Histogram control vs. experiment, objective.
            plt.hist([control_tw_o, experimental_tw_o], bins=7, label=['control group', 'experimental group'],
                     color=['#0072BD','#77AC30'])
            plt.title("Trustworthiness Histogram (Objective)")
            plt.legend()
            plt.xlabel('Trustworthiness Score')
            plt.ylabel('Frequency')
            plt.show()


            # Ability Histogram control vs. experiment, objective.
            plt.hist([control_ability_tw_o, experimental_ability_tw_o], bins=7,
                     label=['control group', 'experimental group'], color=['#0072BD','#77AC30'])
            plt.title("Ability Histogram (Objective)")
            plt.legend()
            plt.xlabel('Ability Score')
            plt.ylabel('Frequency')
            plt.show()

            # Benevolence Histogram control vs. experiment, objective.
            plt.hist([control_benevolence_tw_o, experimental_benevolence_tw_o], bins=7,
                     label=['control group', 'experimental group'], color=['#0072BD','#77AC30'])
            plt.title("Benevolence Histogram (Objective)")
            plt.legend()
            plt.xlabel('Benevolence Score')
            plt.ylabel('Frequency')
            plt.show()

            # Integrity Histogram control vs. experiment, objective.
            plt.hist([control_integrity_tw_o, experimental_integrity_tw_o], bins=7,
                     label=['control group', 'experimental group'], color=['#0072BD','#77AC30'])
            plt.title("Integrity Histogram (Objective)")
            plt.legend()
            plt.xlabel('Integrity Score')
            plt.ylabel('Frequency')
            plt.show()

            # Trusworthiness Histogram control vs. experiment, subjective.
            plt.hist([control_tw_s, experimental_tw_s], bins=7,
                     label=['control group', 'experimental group'], color=['#0072BD','#77AC30'])
            plt.title("Trustworthiness Histogram (Subjective)")
            plt.legend()
            plt.xlabel('Subjectively measured trustworthiness')
            plt.ylabel('Frequency')
            plt.show()

            # Ability Histogram control vs. experiment, subjective.
            plt.hist([control_ability_tw_s, experimental_ability_tw_s], bins=7,
                     label=['control group', 'experimental group'], color=['#0072BD','#77AC30'])
            plt.title("Ability Histogram (Subjective)")
            plt.legend()
            plt.xlabel('Ability Score')
            plt.ylabel('Frequency')
            plt.show()

            # Benevolence Histogram control vs. experiment, subjective.
            plt.hist([control_benevolence_tw_s, experimental_benevolence_tw_s], bins=7,
                     label=['control group', 'experimental group'], color=['#0072BD','#77AC30'])
            plt.title("Benevolence Histogram (Subjective)")
            plt.legend()
            plt.xlabel('Benevolence Score')
            plt.ylabel('Frequency')
            plt.show()

            # Integrity Histogram control vs. experiment, subjective.
            plt.hist([control_integrity_tw_s, experimental_integrity_tw_s], bins=7,
                     label=['control group', 'experimental group'], color=['#0072BD','#77AC30'])
            plt.title("Integrity Histogram (Subjective)")
            plt.legend()
            plt.xlabel('Integrity Score')
            plt.ylabel('Frequency')
            plt.show()

            # print("\n--- ABI score (metrics): ", [ability_score, benevolence_score, integrity_score])
            # print("--- ABI score (questionnaire): ", abi_questionnaire, "\n")

        control_group = [k for k in list_of_files if (CONTROL_AGENT in k)]
        experimental_group = [k for k in list_of_files if (EXPERIMENTAL_AGENT in k)]

        control_group_values = []
        control_group_ability = []
        control_group_benevolence = []
        control_group_integrity = []

        experimental_group_values = []
        experimental_group_ability = []
        experimental_group_benevolence = []
        experimental_group_integrity = []

        if len(control_group) > 0:
            for action_file in control_group:
                this_tick = _last_ticks([action_file])
                this_tick_to_respond = _average_ticks_to_respond([action_file])

                actions = _read_action_file(action_file)

                ability = Ability(actions, last_ticks, this_tick, verbose=VERBOSE)
                benevolence = Benevolence(actions, ticks_to_respond, this_tick_to_respond, verbose=VERBOSE)
                integrity = Integrity(actions, verbose=VERBOSE)

                ability_score, benevolence_score, integrity_score = _compute(ability, benevolence, integrity)
                trustworthiness = (ability_score + benevolence_score + integrity_score) / 3
                control_group_values.append(trustworthiness)
                control_group_ability.append(ability_score)
                control_group_benevolence.append(benevolence_score)
                control_group_integrity.append(integrity_score)

        if len(experimental_group) > 0:
            for action_file in experimental_group:
                this_tick = _last_ticks([action_file])
                this_tick_to_respond = _average_ticks_to_respond([action_file])

                actions = _read_action_file(action_file)

                ability = Ability(actions, last_ticks, this_tick, verbose=VERBOSE)
                benevolence = Benevolence(actions, ticks_to_respond, this_tick_to_respond, verbose=VERBOSE)
                integrity = Integrity(actions, verbose=VERBOSE)

                ability_score, benevolence_score, integrity_score = _compute(ability, benevolence, integrity)
                trustworthiness = (ability_score + benevolence_score + integrity_score) / 3
                experimental_group_values.append(trustworthiness)
                experimental_group_ability.append(ability_score)
                experimental_group_benevolence.append(benevolence_score)
                experimental_group_integrity.append(integrity_score)

        X = ['Ability', 'Benevolence', 'Integrity', 'Trustworthiness']

        print("control -- The mean is : ")
        print(np.mean(control_group_benevolence))
        print("The sd is ")
        print(np.std(control_group_benevolence))
        print("experimental -- The mean is : ")
        print(np.mean(experimental_group_benevolence))
        print("The sd is ")
        print(np.std(experimental_group_benevolence))


        control_bar_values = [np.mean(control_group_ability), np.mean(control_group_benevolence),
                              np.mean(control_group_integrity), np.mean(control_group_values)]
        experimental_bar_values = [np.mean(experimental_group_ability), np.mean(experimental_group_benevolence),
                                   np.mean(experimental_group_integrity), np.mean(experimental_group_values)]

        X_axis = np.arange(len(X))

        plt.bar(X_axis - 0.2, control_bar_values, 0.4, label='Control Group')
        plt.bar(X_axis + 0.2, experimental_bar_values, 0.4, label='Experimental Group')

        plt.xticks(X_axis, X)
        plt.title("ABI Objective Measures Comparison")
        plt.legend()
        plt.show()

        ## Plot Questionnaire Graph
        list_of_questionnaires = glob.glob('../data/questionnaire/*.json')
        control_a = []
        control_b = []
        control_i = []
        experimental_a = []
        experimental_b = []
        experimental_i = []
        count = 0
        if len(list_of_questionnaires) > 0:

            for questionnaireFile in list_of_questionnaires:
                f = open(questionnaireFile)
                data = json.load(f)
                abi_questionnaire = _compute_questionaire(data)
                if CONTROL_AGENT in questionnaireFile:
                    control_a.append(abi_questionnaire[0])
                    control_b.append(abi_questionnaire[1])
                    control_i.append(abi_questionnaire[2])
                if EXPERIMENTAL_AGENT in questionnaireFile:
                    count += 1
                    experimental_a.append(abi_questionnaire[0])
                    experimental_b.append(abi_questionnaire[1])
                    experimental_i.append(abi_questionnaire[2])

            if count == 0:
                print("ERROR: You forgot to include your experimental data in the questionnaire folder. Exiting.")
                return

            print("The medians : ")
            print(np.median(np.array(control_i)))
            print(np.median(np.array(experimental_i)))

            control_avg_ability = np.average(np.array(control_a))
            control_avg_benevolence = np.average(np.array(control_b))
            control_avg_integrity = np.average(np.array(control_i))
            control_abi = np.array([control_avg_ability, control_avg_benevolence,
                                    control_avg_integrity])  # contains the average score for ability, benevolence and integrity
            # of the control group
            control_trustworthiness = np.average(control_abi)

            experimental_avg_ability = np.average(np.array(experimental_a))
            experimental_avg_benevolence = np.average(np.array(experimental_b))
            experimental_avg_integrity = np.average(np.array(experimental_i))
            experimental_abi = np.array([experimental_avg_ability, experimental_avg_benevolence,
                                         experimental_avg_integrity])  # contains the average score for ability, benevolence
            # and integrity of the experimental group
            experimental_trustworthiness = np.average(experimental_abi)

            df = pd.DataFrame({'control group': [control_avg_ability, control_avg_benevolence, control_avg_integrity,
                                                 control_trustworthiness],
                               'experimental group': [experimental_avg_ability, experimental_avg_benevolence,
                                                      experimental_avg_integrity, experimental_trustworthiness]},
                              index=["Ability", "Benevolence", "Integrity", "Trustworthiness"])
            df.plot(kind='bar')
            plt.title("ABI Questionnaire Score Comparison")
            plt.legend()
            plt.show()


            print("Got here")


Trustworthiness()
