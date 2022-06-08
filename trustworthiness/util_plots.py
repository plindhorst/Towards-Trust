import os

import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as stats


def plot_distr(group, scores):
    result_folder = os.getcwd().replace("\\", "/") + "/results/"
    if not os.path.exists(result_folder):
        os.makedirs(result_folder)

    colors = ['r', 'b', 'y', 'g']
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
        plt.hist(concept_score, bins=10, facecolor=colors[i], edgecolor='black', linewidth=0.5)
        plt.xticks([0, 1])
        plt.xlabel("Value bins")
        plt.ylabel("Frequency")
        plt.title("Histogram for " + concept)
        plt.subplot(1, 3, 2)
        plt.boxplot(concept_score, notch=False, patch_artist=True,
                    boxprops=dict(facecolor=colors[i], color=colors[i]),
                    capprops=dict(color=colors[i]),
                    whiskerprops=dict(color=colors[i]),
                    flierprops=dict(color=colors[i], markeredgecolor=colors[i]),
                    medianprops=dict(color=colors[i]),
                    )
        plt.xlabel("")
        plt.ylabel("Values")
        plt.yticks([0, 1])
        plt.title("Boxplot of " + concept)
        ax1 = plt.subplot(1, 3, 3)
        stats.probplot(concept_score, dist="norm", plot=plt)
        ax1.get_lines()[0].set_markerfacecolor(colors[i])
        ax1.get_lines()[0].set_markeredgecolor('black')
        ax1.get_lines()[1].set_color('black')
        ax1.get_lines()[0].set_markersize(12.0)
        plt.yticks([0, 1])
        plt.title("Normal Q-Q Plot")
        fig.tight_layout()
        fig.set_size_inches(20, 10)
        plt.savefig(result_folder + group + "_" + concept + "_distr.png", bbox_inches="tight")
        plt.close(fig)


def plot_metrics(metrics):
    metric_names = [
        ["game_completion", "victim_found_ratios", "victim_picked_ratios", "rooms_visited", "normalized_tick"],
        ["communicated_baby_gender", "communicated_yes", "communicated_room_search", "communicated_pickup",
         "advice_followed", "communicated_victims_found", "average_ticks_to_respond"],
        ["truth_identify_gender", "truth_suggested_pickup_yes", "truth_identify_person",
         "truth_communicated_searched_rooms", "truth_pickup"]]
    colors = ['r', 'b', 'y']

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

            plt.hist(aggr, bins=10, facecolor=colors[i], edgecolor='black', linewidth=0.5)
            plt.xlabel("Value")
            plt.ylabel("Count")
            plt.title(metric_name)
            fig.set_size_inches(20, 10)

            plt.savefig(result_folder + metric_name + ".png", bbox_inches="tight")
            plt.close(fig)
