import os

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as stats

COLORS = ['r', 'b', '#FFFF00', 'g']


def plot_distr(group, scores):
    result_folder = os.getcwd().replace("\\", "/") + "/results/distributions/"
    if not os.path.exists(result_folder):
        os.makedirs(result_folder)

    for i, concept in enumerate(["Ability", "Benevolence", "Integrity", "Trustworthiness"]):
        concept_score = []
        if concept == "Trustworthiness":
            for score in scores:
                concept_score.append(np.mean(score))
        else:
            for score in scores:
                concept_score.append(score[i])

        fig = plt.gcf()
        plt.rc("font", **{"size": 22})
        plt.subplot(1, 3, 1)
        plt.hist(concept_score, bins=10, facecolor=COLORS[i], edgecolor='black', linewidth=0.5)
        plt.xticks([0, 1])
        plt.xlabel("Value bins")
        plt.ylabel("Frequency")
        plt.title("Histogram for " + concept)
        plt.subplot(1, 3, 2)
        plt.boxplot(concept_score, notch=False, patch_artist=True,
                    boxprops=dict(facecolor=COLORS[i], color=COLORS[i]),
                    capprops=dict(color=COLORS[i]),
                    whiskerprops=dict(color=COLORS[i]),
                    flierprops=dict(color=COLORS[i], markeredgecolor=COLORS[i]),
                    medianprops=dict(color=COLORS[i]),
                    )
        plt.xlabel("")
        plt.ylabel("Values")
        plt.yticks([0, 1])
        plt.title("Boxplot of " + concept)
        ax1 = plt.subplot(1, 3, 3)
        stats.probplot(concept_score, dist="norm", plot=plt)
        ax1.get_lines()[0].set_markerfacecolor(COLORS[i])
        ax1.get_lines()[0].set_markeredgecolor('black')
        ax1.get_lines()[1].set_color('black')
        ax1.get_lines()[0].set_markersize(12.0)
        plt.yticks([0, 1])
        plt.title("Normal Q-Q Plot")
        fig.tight_layout()
        fig.set_size_inches(20, 10)
        fig.suptitle("Probability Distribution of " + concept + " for " + group.replace("_", " ").title())
        plt.savefig(result_folder + group + "_" + concept + "_distr.png", bbox_inches="tight")
        plt.close(fig)


def plot_metrics(metrics):
    metric_names = [
        ["game_completion", "victim_found_ratios", "victim_picked_ratios", "rooms_visited", "normalized_tick"],
        ["communicated_baby_gender", "communicated_yes", "communicated_room_search", "communicated_pickup",
         "advice_followed", "communicated_victims_found", "average_ticks_to_respond"],
        ["truth_identify_gender", "truth_suggested_pickup_yes", "truth_identify_person",
         "truth_communicated_searched_rooms", "truth_pickup"]]

    result_folder = os.getcwd().replace("\\", "/") + "/results/metrics/"
    if not os.path.exists(result_folder):
        os.makedirs(result_folder)

    for i, concept in enumerate(metric_names):
        for j, metric_name in enumerate(concept):
            aggr = []
            for metric in metrics:
                aggr.append(metric[i][j])

            fig = plt.gcf()
            plt.rc("font", **{"size": 22})

            plt.hist(aggr, bins=10, facecolor=COLORS[i], edgecolor='black', linewidth=0.5)
            plt.xlabel("Value")
            plt.ylabel("Count")
            plt.title(metric_name)
            fig.set_size_inches(20, 10)

            plt.savefig(result_folder + metric_name + ".png", bbox_inches="tight")
            plt.close(fig)


def plot_abi(abi_ctrl, abi_exp, tw_ctrl, tw_exp, type_):
    fig = plt.gcf()
    plt.rc("font", **{"size": 27})

    bar_width = 1

    abi_ctrl.append(tw_ctrl)
    abi_exp.append(tw_exp)
    for i, concept in enumerate(["Ability", "Benevolence", "Integrity", "Trustworthiness"]):
        mean_ctrl = np.mean(abi_ctrl[i])
        mean_exp = np.mean(abi_exp[i])

        plt.bar((i + 1) * " ", mean_ctrl, color=COLORS[i], width=bar_width, edgecolor='black')
        plt.bar((i + 2) * 3 * " ", mean_exp, color=COLORS[i], width=bar_width, edgecolor='black', hatch="x")

        if i < 3:
            plt.bar((i + 2) * 3 * "   ", 1.20, alpha=0, width=0.5)

    result_folder = os.getcwd().replace("\\", "/") + "/results/"
    if not os.path.exists(result_folder):
        os.makedirs(result_folder)

    fig.tight_layout()
    plt.title("ABI Scores for " + type_.title())
    plt.ylabel("Score")

    first_legend = plt.legend(
        [mpatches.Patch(facecolor=COLORS[0], edgecolor='black'), mpatches.Patch(facecolor=COLORS[1], edgecolor='black'),
         mpatches.Patch(facecolor=COLORS[2], edgecolor='black'),
         mpatches.Patch(facecolor=COLORS[3], edgecolor='black')],
        ['Ability', 'Benevolence', 'Integrity', "Trustworthiness"],
        loc='upper right', edgecolor='black',
        frameon=False)
    ax = plt.gca().add_artist(first_legend)
    plt.legend([mpatches.Patch(facecolor='#FFFFFF', edgecolor='black'),
                mpatches.Patch(facecolor='#FFFFFF', hatch='x', edgecolor='black')],
               ['Control', 'Experimental'],
               loc='upper left', frameon=False)
    plt.yticks([0, 1])
    fig.set_size_inches(25, 12)
    plt.savefig(result_folder + "ABI_" + type_.replace(" metrics", "") + ".png", bbox_inches="tight")
    plt.close(fig)


def plot_participant_stats(group, participants_stats):
    result_folder = os.getcwd().replace("\\", "/") + "/results/"
    if not os.path.exists(result_folder):
        os.makedirs(result_folder)

    plot_coords = [(0, 0), (1, 0), (0, 1), (1, 1)]
    titles = ["Age", "Gender", "Birthplace", "Game Experience"]
    name_stats = ["age", "Gender", "Birthplace", "GameExperience"]
    values_stats = [["18-24", "25-34", "35-44", "45-54", "55-64", "65+"],
                    ["Male", "Female", "Other", "Prefer not to say"],
                    ["Africa", "Asia", "Australia", "Europe", "North/Central America", "South America", "Other"],
                    ["Low", "Average", "High"]]

    fig = plt.figure(figsize=(25, 25))
    plt.rc("font", **{"size": 28})
    for i, name_stat in enumerate(name_stats):
        counts = []
        for j in range(len(values_stats[i])):
            counts.append(0)

        for participants_stat in participants_stats:
            try:
                counts[int(participants_stat[i][name_stat])] += 1
            except KeyError:
                continue

        pop_idx = []
        for j, count in enumerate(counts):
            if count == 0:
                pop_idx.append(j)

        for j, idx in enumerate(pop_idx):
            counts.pop(idx - j)
            values_stats[i].pop(idx - j)

        ax1 = plt.subplot2grid((2, 2), plot_coords[i])
        plt.title(titles[i].title())

        plt.pie(counts, labels=values_stats[i], autopct='%1.1f%%')

    fig.suptitle("Population Statistics for " + group.replace("_", " ").title() + " Group")
    fig.tight_layout()
    plt.savefig(result_folder + "population_stats_" + group + ".png", bbox_inches="tight")
    plt.close(fig)
