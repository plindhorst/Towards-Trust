import argparse
import os, requests
import csv
import glob
import pathlib
import sys
from datetime import datetime

from SaR_gui import visualization_server
from trustworthiness.Trustworthiness import Trustworthiness
from worlds1.worldBuilder import create_builder
from agents1 import HighInterdependenceAgent

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-xai", action='store', help="Explainability of agent", type=str)
    parser.add_argument("-tw", action='store_true', help="Measure trustworthiness of human", default=False)
    args = parser.parse_args()

    if args.tw:
        trustworthiness = Trustworthiness("./actions.pkl")

        trustworthiness.actions_to_string()
        ability, benevolence, integrity = trustworthiness.compute()
        print("\nABI: ", round(ability, 2), ",", round(benevolence, 2), ",", round(integrity, 2))
        sys.exit(0)

    choice1 = args.xai
    if args.xai is None or args.xai == "":
        print("\nEnter one of the robot communication styles 'silent', 'transparent', 'adaptive', or 'explainable':")
        choice1 = input()

    # Hardcode interdependence to high
    interdependence = "low"

    while True:
        builder = create_builder(exp_version=interdependence, condition=choice1)

        # Start overarching MATRX scripts and threads
        media_folder = pathlib.Path().resolve()
        builder.startup(media_folder=media_folder)
        print("Starting custom visualizer")
        vis_thread = visualization_server.run_matrx_visualizer(verbose=False, media_folder=media_folder)
        world = builder.get_world()
        print("Started world...")

        # builder.api_info["matrx_paused"] = False
        world.run(builder.api_info)
        requests.get("http://localhost:" + str(visualization_server.port) + "/set_done")
        print("DONE!")
        requests.get("http://localhost:" + str(visualization_server.port) + "/shutdown_visualizer")
        vis_thread.join()
        builder.stop()
