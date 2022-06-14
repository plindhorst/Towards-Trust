import argparse
import pathlib
import sys

import requests

from trustworthiness.Trustworthiness import Trustworthiness
from world.agents.ControlAgent import ControlAgent
from world.agents.custom.AdviceAgent import AdviceAgent
from world.agents.custom.ConflictingAgent import ConflictingAgent
from world.agents.custom.DirectingAgent import DirectingAgent
from world.agents.custom.FriendlyAgent import FriendlyAgent
from world.agents.custom.FriendlyAgentDutch import FriendlyAgentDutch
from world.agents.custom.HelpingAgent import HelpingAgent
from world.agents.custom.TutorialAgent import TutorialAgent
from world.agents.custom.TutorialAgentDutch import TutorialAgentDutch
from world.visualizer import visualization_server
from world.worldBuilder import create_builder

TICK_DURATION = 0.07
MINUTES = 10
MAX_TICKS = int(MINUTES * 60 / TICK_DURATION)
AGENT_SLOWDOWN = 7

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-agent", action='store',
                        help="Agent type, choose from: control, control-dutch, helper, conflicting, advice, directing,\
                         friendly, friendly-dutch, tutorial, tutorial-dutch", type=str)
    parser.add_argument("-tw", action='store',
                        help="Compare trustworthiness of control and experiment groups. "
                             "Enter the name of the experimental group, choose from: "
                             "helper, conflicting, advice, directing, friendly",
                        default="conflicting", type=str)
    parser.add_argument("-alt", action='store',
                        help="Defines the alternative hypothesis. The following options are available (default is ‘two-sided’):"
                             "‘two-sided’: the means of the distributions underlying the samples are unequal."
                             "‘less’: the mean of the distribution underlying the first sample is less than the mean of the distribution underlying the second sample."
                             "‘greater’: the mean of the distribution underlying the first sample is greater than the mean of the distribution underlying the second sample.",
                        default="two-sided", type=str)
    parser.add_argument("-verbose_lvl", action='store',
                        help="Choose how much information to print. Verbose levels are: 0, 1, 2",
                        default="0", type=str)
    args = parser.parse_args()

    if args.tw:
        group = args.tw
        if group not in ["helper", "conflicting", "advice", "directing", "friendly"]:
            print("Invalid experimental group name. Choose from: helper, conflicting, advice, directing, friendly")
            sys.exit(0)

        alt = "two-sided"
        if args.alt:
            alt = args.alt
            if alt not in ["two-sided", "less", "greater"]:
                print("Invalid alternative hypothesis. Choose from: two-sided, greater, less")
                sys.exit(0)

        verbose_lvl = 0
        if args.verbose_lvl:
            verbose_lvl = int(args.verbose_lvl)
            if verbose_lvl not in [0, 1, 2]:
                print("Invalid verbose level. Choose from: 0, 1, 2")
                sys.exit(0)

        trustworthiness = Trustworthiness(group=group, graphs=True, alternative=alt, verbose_lvl=verbose_lvl)
        sys.exit(0)

    agent = None

    agent_type = args.agent
    if agent_type == "control":
        print("Playing with control agent")
        agent = ControlAgent(AGENT_SLOWDOWN)
    elif agent_type == "control-dutch":
        print("Playing with control-dutch agent")
    elif agent_type == "helper":
        print("Playing with helper agent")
        agent = HelpingAgent(AGENT_SLOWDOWN, "explainable")
    elif agent_type == "conflicting":
        print("Playing with conflicting agent")
        agent = ConflictingAgent(AGENT_SLOWDOWN)
    elif agent_type == "advice":
        print("Playing with advice seeking agent")
        agent = AdviceAgent(AGENT_SLOWDOWN)
    elif agent_type == "directing":
        print("Playing with directing agent")
        agent = DirectingAgent(AGENT_SLOWDOWN)
    elif agent_type == "friendly":
        print("Playing with friendly agent")
        agent = FriendlyAgent(AGENT_SLOWDOWN)
    elif agent_type == "friendly-dutch":
        print("Playing with friendly-dutch agent")
        agent = FriendlyAgentDutch(AGENT_SLOWDOWN)
    elif agent_type == "tutorial":
        agent = TutorialAgent(AGENT_SLOWDOWN)
    elif agent_type == "tutorial-dutch":
        agent = TutorialAgentDutch(AGENT_SLOWDOWN)

    else:
        print("Please choose one of the following agents: control, control-dutch, helper, conflicting, advice, \
        directing, friendly, friendly-dutch, tutorial, tutorial-dutch")
        sys.exit(0)

    while True:
        builder = create_builder(agent_type=agent_type, agent=agent, max_nr_ticks=MAX_TICKS,
                                 tick_duration=TICK_DURATION)

        # Start overarching MATRX scripts and threads
        media_folder = str(pathlib.Path().resolve()) + "/world/visualizer/static/"
        builder.startup(media_folder=media_folder)
        print("Starting custom visualizer")
        vis_thread = visualization_server.run_matrx_visualizer(agent_type, verbose=False, media_folder=media_folder)
        world = builder.get_world()
        print("Started world...")

        # builder.api_info["matrx_paused"] = False
        world.run(builder.api_info)
        requests.get("http://localhost:" + str(visualization_server.port) + "/set_done")
        print("DONE!")
        requests.get("http://localhost:" + str(visualization_server.port) + "/shutdown_visualizer")
        vis_thread.join()
        builder.stop()
