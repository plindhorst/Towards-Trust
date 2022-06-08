import os

import numpy as np
from matplotlib import pyplot as plt


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
