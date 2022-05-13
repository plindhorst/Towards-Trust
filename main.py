import argparse
import os, requests
import csv
import glob
import pathlib
import sys

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
        trustworthiness = Trustworthiness()

        # trustworthiness.actions_to_string()
        print("\ntw: ", trustworthiness.compute())
        sys.exit(0)

    choice1 = args.xai
    if args.xai is None or args.xai == "":
        print("\nEnter one of the robot communication styles 'silent', 'transparent', 'adaptive', or 'explainable':")
        choice1 = input()

    # Hardcode interdependence to high
    choice2 = "high"

    # Create our world builder
    builder = create_builder(exp_version=choice2, condition=choice1)

    # Start overarching MATRX scripts and threads, such as the api and/or visualizer if requested. Here we also link our
    # own media resource folder with MATRX.
    media_folder = pathlib.Path().resolve()
    # media_folder = os.path.dirname(os.path.join(os.path.realpath("/home/ruben/Documents/MATRX/MATRX"), "media"))
    builder.startup(media_folder=media_folder)
    print("Starting custom visualizer")
    vis_thread = visualization_server.run_matrx_visualizer(verbose=False, media_folder=media_folder)
    world = builder.get_world()
    print("Started world...")
    builder.api_info["matrx_paused"] = False
    world.run(builder.api_info)
    print("DONE!")
    print("Shutting down custom visualizer")
    r = requests.get("http://localhost:" + str(visualization_server.port) + "/shutdown_visualizer")
    vis_thread.join()

    if choice2 == "low" or choice2 == "high":
        fld = os.getcwd()
        recent_dir = max(glob.glob(os.path.join(fld, '*/')), key=os.path.getmtime)
        recent_dir = max(glob.glob(os.path.join(recent_dir, '*/')), key=os.path.getmtime)
        action_file = glob.glob(os.path.join(recent_dir, 'world_1/action*'))[0]
        message_file = glob.glob(os.path.join(recent_dir, 'world_1/message*'))[0]
        action_header = []
        action_contents = []
        message_header = []
        message_contents = []
        unique_agent_moves = []
        unique_human_moves = []
        dropped_human = []
        dropped_agent = []
        drop_zones = ['(1, 23)', '(2, 23)', '(3, 23)', '(4, 23)', '(5, 23)', '(6, 23)', '(7, 23)', '(8, 23)']

        with open(action_file) as csvfile:
            reader = csv.reader(csvfile, delimiter=';', quotechar="'")
            for row in reader:
                if action_header == []:
                    action_header = row
                    continue
                if row[1:3] not in unique_agent_moves:
                    unique_agent_moves.append(row[1:3])
                if row[3:5] not in unique_human_moves:
                    unique_human_moves.append(row[3:5])
                if row[1] == 'DropObject' and row[1:3] not in dropped_agent and row[2] in drop_zones:
                    dropped_agent.append(row[1:3])
                if row[3] == 'DropObject' and row[3:5] not in dropped_human and row[4] in drop_zones:
                    dropped_human.append(row[3:5])
                res = {action_header[i]: row[i] for i in range(len(action_header))}
                action_contents.append(res)

        with open(message_file) as csvfile:
            reader = csv.reader(csvfile, delimiter=';', quotechar="'")
            for row in reader:
                if message_header == []:
                    message_header = row
                    continue
                res = {message_header[i]: row[i] for i in range(len(message_header))}
                message_contents.append(res)

        no_messages_human = message_contents[-1]['total_number_messages_human']
        no_messages_agent = message_contents[-1]['total_number_messages_agent']
        mssg_len_human = message_contents[-1]['average_message_length_human']
        mssg_len_agent = message_contents[-1]['average_message_length_agent']
        no_ticks = action_contents[-1]['tick_nr']

        # Altered by Justin: Now the number of ticks will be the amount after 'ready' has been pressed.
        no_ticks = str(int(
            action_contents[-1]['tick_nr']) - HighInterdependenceAgent.HighInterdependenceAgent.numberOfTicksWhenReady)

        success = action_contents[-1]['done']
        print("Saving output...")
        with open(os.path.join(recent_dir, 'world_1/output.csv'), mode='w') as csv_file:
            csv_writer = csv.writer(csv_file, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            csv_writer.writerow(
                ['completed', 'no_ticks', 'moves_agent', 'moves_human', 'no_messages_agent', 'no_messages_human',
                 'message_length_agent', 'message_length_human', 'victims_dropped_agent', 'victims_dropped_human'])
            csv_writer.writerow([success, no_ticks, len(unique_agent_moves), len(unique_human_moves), no_messages_agent,
                                 no_messages_human, mssg_len_agent, mssg_len_human, len(dropped_agent),
                                 len(dropped_human)])

    builder.stop()
