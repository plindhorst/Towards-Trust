import glob
import json
import os
import pickle
import shutil

import numpy as np

from trustworthiness.Ability import Ability
from trustworthiness.Benevolence import Benevolence
from trustworthiness.Integrity import Integrity
from trustworthiness.util_plots import plot_metrics, plot_distr, plot_abi, plot_participant_stats
from world.actions.AgentAction import MessageAskGender, MessageSuggestPickup
from world.actions.HumanAction import MessageGirl, MessageYes, MessageBoy, MessageNo
from scipy.stats import shapiro, mannwhitneyu, ttest_ind


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


def _compute_abi_questionaire(answers):
    f = open('./trustworthiness/questionnaire.json')
    questions = json.load(f)

    abi = [0, 0, 0]
    counts = [0, 0, 0]

    answers_ = []

    for i, concept in enumerate(["Ability", "Benevolence", "Integrity"]):
        for question in questions:
            answered = False
            if question["type"] == concept:
                for answer in answers:
                    try:
                        abi[i] += int(answer[question["name"]])
                        answers_.append(int(answer[question["name"]]))
                        counts[i] += 1
                        answered = True
                        break
                    except KeyError:
                        continue
                if not answered:
                    answers_.append(0)
        abi[i] /= counts[i]

    abi = [round(x / 6, 2) for x in abi]

    return abi, answers_


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


def is_normal_distr(scores, alpha=0.05):
    statistic, p = shapiro(scores)

    normal = p > alpha

    return normal, p


class Trustworthiness:
    def __init__(self, group="control", graphs=False, alternative="two-sided", verbose_lvl=0):
        if graphs:
            shutil.rmtree('./results')
        abi_ctrl, abi_normal_ctrl, abi_questionnaire_ctrl, abi_questionnaire_normal_ctrl, tw_ctrl, tw_normal_ctrl, tw_questionnaire_ctrl, tw_questionnaire_normal_ctrl = get_group_trustworthiness(
            "control", graphs, verbose_lvl)
        abi_exp, abi_normal_exp, abi_questionnaire_exp, abi_questionnaire_normal_exp, tw_exp, tw_normal_exp, tw_questionnaire_exp, tw_questionnaire_normal_exp = get_group_trustworthiness(
            group, graphs, verbose_lvl)

        print("\nPerforming statistical inference. Hypothesis is '" + alternative + "'.")
        for i, concept in enumerate(["Ability", "Benevolence", "Integrity"]):
            significant, p_value, statistic, test = significance_test(abi_ctrl[i], abi_exp[i],
                                                                      (abi_normal_ctrl[i] and abi_normal_exp[i]),
                                                                      alternative)

            if significant:
                print(concept, "SIGNIFICANT (" + test + ", p = " + str(round(p_value, 3)) + ", test-statistic = " + str(
                    round(statistic, 3)) + ")")
            else:
                print(concept,
                      "NOT SIGNIFICANT (" + test + ", p = " + str(round(p_value, 3)) + ", test-statistic = " + str(
                          round(statistic, 3)) + ")")

            significant, p_value, statistic, test = significance_test(abi_questionnaire_ctrl[i],
                                                                      abi_questionnaire_exp[i], (
                                                                              abi_questionnaire_normal_ctrl[i] and
                                                                              abi_questionnaire_normal_exp[i]),
                                                                      alternative)

            if significant:
                print(concept, "questionnaire SIGNIFICANT (" + test + ", p = " + str(
                    round(p_value, 3)) + ", test-statistic = " + str(
                    round(statistic, 3)) + ")")
            else:
                print(concept, "questionnaire NOT SIGNIFICANT (" + test + ", p = " + str(
                    round(p_value, 3)) + ", test-statistic = " + str(
                    round(statistic, 3)) + ")")

        significant, p_value, statistic, test = significance_test(tw_ctrl, tw_exp, (tw_normal_ctrl and tw_normal_exp),
                                                                  alternative)

        if significant:
            print("Trustworthiness SIGNIFICANT (" + test + ", p = " + str(
                round(p_value, 3)) + ", test-statistic = " + str(
                round(statistic, 3)) + ")")
        else:
            print("Trustworthiness NOT SIGNIFICANT (" + test + ", p = " + str(
                round(p_value, 3)) + ", test-statistic = " + str(
                round(statistic, 3)) + ")")

        significant, p_value, statistic, test = significance_test(tw_questionnaire_ctrl, tw_questionnaire_exp,
                                                                  (
                                                                          tw_questionnaire_normal_ctrl and tw_questionnaire_normal_exp),
                                                                  alternative)

        if significant:
            print("Trustworthiness questionnaire SIGNIFICANT (" + test + ", p = " + str(
                round(p_value, 3)) + ", test-statistic = " + str(
                round(statistic, 3)) + ")")
        else:
            print("Trustworthiness questionnaire NOT SIGNIFICANT (" + test + ", p = " + str(
                round(p_value, 3)) + ", test-statistic = " + str(
                round(statistic, 3)) + ")")

        if graphs:
            plot_abi(abi_ctrl, abi_exp, tw_ctrl, tw_exp, type_="objective metrics")
            plot_abi(abi_questionnaire_ctrl, abi_questionnaire_exp, tw_questionnaire_ctrl, tw_questionnaire_exp,
                     type_="questionnaire")


def significance_test(control_data, experimental_data, normal, alternative="greater", alpha=0.05):
    if normal:
        p_value = ttest_ind(control_data, experimental_data, alternative=alternative).pvalue
        statistic = ttest_ind(control_data, experimental_data, alternative=alternative).statistic
        test = "T-Test"
    else:
        p_value = mannwhitneyu(control_data, experimental_data, alternative=alternative).pvalue
        statistic = mannwhitneyu(control_data, experimental_data, alternative=alternative).statistic
        test = "Mann-Whitney U Test"

    significant = p_value < alpha
    return significant, p_value, statistic, test


def cronbach_alpha(scores):
    scores = np.asarray(scores, dtype=object)
    itemvars = scores.var(axis=1, ddof=1)
    tscores = scores.sum(axis=0)
    nitems = len(scores)

    return nitems / (nitems - 1.) * (1 - itemvars.sum() / tscores.var(ddof=1))


def get_group_trustworthiness(group, graphs, verbose_lvl):
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
        scores = []
        questionnaire_scores = []
        questionnaire_answers = []
        participant_stats = []
        for action_file in list_of_files:

            metrics_, scores_, abi_questionnaire, answers, participant_stat = get_trustworthiness_from_file(action_file, last_ticks,
                                                                                          ticks_to_respond,
                                                                                          verbose_lvl)
            metrics.append(metrics_)
            scores.append(scores_)
            questionnaire_scores.append(abi_questionnaire)
            questionnaire_answers.append(answers)
            participant_stats.append(participant_stat)

            if verbose_lvl >= 2:
                print("\n--- ABI score (metrics): ", scores_)
                print("--- ABI score (questionnaire): ", abi_questionnaire, "\n")

        if verbose_lvl >= 1:
            print()
            print(group, "Cronbach's Alpha =", round(cronbach_alpha(questionnaire_answers), 3))

        abi_scores = [[], [], []]
        abi_questionnaire_scores = [[], [], []]
        abi_normal = []
        abi_questionnaire_normal = []
        for i, concept in enumerate(["Ability", "Benevolence", "Integrity"]):

            concept_score = []
            concept_questionaire_score = []
            for score in scores:
                abi_scores[i].append(score[i])
                concept_score.append(score[i])

            for score in questionnaire_scores:
                abi_questionnaire_scores[i].append(score[i])
                concept_questionaire_score.append(score[i])

            normal, p = is_normal_distr(concept_score)
            abi_normal.append(normal)

            if verbose_lvl >= 1:
                if normal:
                    print(group, "(" + concept + ")", "is normally distributed, with p =", round(p, 3), ", mean =",
                          round(np.mean(np.array(concept_score)), 3), ", STD =",
                          round(np.std(np.array(concept_score)), 3))
                else:
                    print(group, "(" + concept + ")", "is not normally distributed, with p =", round(p, 3), ", mean =",
                          round(np.mean(np.array(concept_score)), 3), ", STD =",
                          round(np.std(np.array(concept_score)), 3))

            normal, p = is_normal_distr(concept_questionaire_score)
            abi_questionnaire_normal.append(normal)

            if verbose_lvl >= 1:
                if normal:
                    print(group, "(" + concept + ") questionnaire", "is normally distributed, with p =", round(p, 3),
                          ", mean =", round(np.mean(np.array(concept_questionaire_score)), 3), ", STD =",
                          round(np.std(np.array(concept_questionaire_score)), 3))
                else:
                    print(group, "(" + concept + ") questionnaire", "is not normally distributed, with p =",
                          round(p, 3), ", mean =", round(np.mean(np.array(concept_questionaire_score)), 3), ", STD =",
                          round(np.std(np.array(concept_questionaire_score)), 3))

        tw_scores = []
        for score in scores:
            tw_scores.append(np.mean(score))

        tw_normal, p = is_normal_distr(tw_scores)

        if verbose_lvl >= 1:
            if tw_normal:
                print(group, "(Trustworthiness)", "is normally distributed, with p =", round(p, 3), ", mean =",
                      round(np.mean(np.array(tw_scores)), 3), ", STD =", round(np.std(np.array(tw_scores)), 3))
            else:
                print(group, "(Trustworthiness)", "is not normally distributed, with p =", round(p, 3), ", mean =",
                      round(np.mean(np.array(tw_scores)), 3), ", STD =", round(np.std(np.array(tw_scores)), 3))

        tw_questionnaire_scores = []
        for score in questionnaire_scores:
            tw_questionnaire_scores.append(np.mean(score))

        tw_questionnaire_normal, p = is_normal_distr(tw_questionnaire_scores)

        if verbose_lvl >= 1:
            if tw_questionnaire_normal:
                print(group, "(Trustworthiness) questionnaire", "is normally distributed, with p =", round(p, 3),
                      ", mean =", round(np.mean(np.array(tw_questionnaire_scores)), 3), ", STD =",
                      round(np.std(np.array(tw_questionnaire_scores)), 3))
            else:
                print(group, "(Trustworthiness) questionnaire", "is not normally distributed, with p =", round(p, 3),
                      ", mean =", round(np.mean(np.array(tw_questionnaire_scores)), 3), ", STD =",
                      round(np.std(np.array(tw_questionnaire_scores)), 3))

        if graphs:
            plot_metrics(metrics)
            plot_distr(group, scores)
            plot_distr(group + "_questionnaire", questionnaire_scores)
            plot_participant_stats(group, participant_stats)

        return abi_scores, abi_normal, abi_questionnaire_scores, abi_questionnaire_normal, tw_scores, tw_normal, tw_questionnaire_scores, tw_questionnaire_normal


def get_trustworthiness_from_file(action_file, last_ticks, ticks_to_respond, verbose_lvl):
    this_tick = _last_ticks([action_file])
    this_tick_to_respond = _average_ticks_to_respond([action_file])
    action_file = action_file.replace("\\", "/")
    file_name = action_file.split("/")[-1].replace(".pkl", "")

    if verbose_lvl >= 2:
        print("### ", file_name)

    actions = _read_action_file(action_file)

    ability = Ability(actions, last_ticks, this_tick, verbose_lvl=verbose_lvl)
    benevolence = Benevolence(actions, ticks_to_respond, this_tick_to_respond, verbose_lvl=verbose_lvl)
    integrity = Integrity(actions, verbose_lvl=verbose_lvl)

    ability_score, ability_metrics = ability.compute()
    benevolence_score, benevolence_metrics = benevolence.compute()
    integrity_score, integrity_metrics = integrity.compute()

    metrics = [ability_metrics, benevolence_metrics, integrity_metrics]
    scores = [ability_score, benevolence_score, integrity_score]

    answers = _read_questionnaire_answers(file_name + ".json")
    participant_stat = []
    for i in range(5):
        participant_stat.append(answers[i])
    abi_questionnaire, answers = _compute_abi_questionaire(answers)

    return metrics, scores, abi_questionnaire, answers, participant_stat
