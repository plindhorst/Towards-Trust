import os
import pickle
from datetime import datetime
from os.path import exists

from matrx.agents import AgentBrain

from world.actions.AgentAction import MessageAskGender, MessageRequestPickup, MessageSuggestPickup, MessageDelivered
from world.actions.HumanAction import MessageSearch, MessageFound, EnterRoom, MessagePickUp, DropOff, PickUp, MessageBoy, \
    MessageGirl, MessageNo, MessageYes, FoundVictim, EnterUnvisitedRoom
from world.actions.util import is_in_room, is_in_range, is_correct_drop_location


# This agent class records actions and messages of the human/agent
class Spy(AgentBrain):
    def __init__(self, agent_type):
        super().__init__()

        self._human_is_carrying = False
        self._carried_person = None
        self._human_in_room = False
        self._last_action = None
        self._found_victims = []
        self._visited_rooms = []
        self._file_created = False

        result_folder = os.getcwd().replace("\\", "/") + "/data/actions/"
        if not os.path.exists(result_folder):
            os.makedirs(result_folder)

        self.action_file = result_folder + agent_type + "_" + datetime.now().strftime("%Y%m%d-%H%M%S") + ".pkl"

    # This method gets called every tick
    def decide_on_action(self, state):

        self._read_human_messages()  # Remember communicated actions
        self._check_enter_room()  # Check if human enters a room
        self._check_pick_up()  # Check if human picks up a person
        self._check_drop_off()  # Check if human drops up a person
        self._check_found_victim()  # Check if human is next to a victim

        return None, {}

    # Save action to pickle file
    def _save_action_to_file(self, action):
        if not self._file_created and not exists(self.action_file):
            f = open(self.action_file, "w+")  # init action file
            f.close()
            self._file_created = True

        self._last_action = action
        with open(self.action_file, 'ab+') as out:
            pickle.dump(self._last_action, out, pickle.HIGHEST_PROTOCOL)

    # Returns the current map: locations of persons/agent/human
    def _map_state(self):
        agent = self.state.get_agents()[0]
        human = self.state.get_agents()[2]
        map_state = {"tick": self.state['World']['nr_ticks'], "persons": [], "human_location": human["location"],
                     "agent_location": agent["location"]}
        for person in self.state.get_with_property({"is_collectable": True}, combined=True):
            map_state["persons"].append(
                {"name": person["name"], "is_drop_zone": person["is_drop_zone"],
                 "is_goal_block": person["is_goal_block"],
                 "location": person["location"], "carried_by": person["carried_by"]})
        return map_state

    def _read_human_messages(self):
        for message in list(self.received_messages):

            # Messages/answers from the human
            if message.startswith("Search:"):
                room_name = message.replace("Search: ", "")
                self._save_action_to_file(MessageSearch(self._map_state(), room_name))
            elif message.startswith("Found:"):
                person = message.replace("Found: ", "")
                self._save_action_to_file(MessageFound(self._map_state(), person))
            elif message.startswith("Collect:"):
                if len(message.split()) == 6:
                    person = ' '.join(message.split()[1:4])
                else:
                    person = ' '.join(message.split()[1:5])
                room_name = message.replace("Collect: " + person + " in ", "")
                person += " in area " + room_name
                self._save_action_to_file(MessagePickUp(self._map_state(), person))
            elif message.startswith("Yes"):
                self._save_action_to_file(MessageYes(self._map_state()))
            elif message.startswith("No"):
                self._save_action_to_file(MessageNo(self._map_state()))
            elif message.startswith("Girl"):
                self._save_action_to_file(MessageGirl(self._map_state()))
            elif message.startswith("Boy"):
                self._save_action_to_file(MessageBoy(self._map_state()))
            # Messages from the agent
            elif message.startswith("URGENT: You should clarify the gender"):
                room_name = message.replace("URGENT: You should clarify the gender of the injured baby in area ",
                                            "").replace(
                    " because I am unable to distinguish them. Please come here and press button \"Boy\" or \"Girl\".",
                    "")
                self._save_action_to_file(MessageAskGender(self._map_state(), room_name))
            elif message.startswith("URGENT: You should pick up"):
                person = message.replace("URGENT: You should pick up ", "").replace(
                    " because I am not allowed to carry critically injured adults.", "")
                self._save_action_to_file(MessageRequestPickup(self._map_state(), person))
            elif message.startswith("You need to pick up"):
                person = message.replace("You need to pick up ", "").replace(
                    " because I am not allowed to carry critically injured adults.", "")
                self._save_action_to_file(MessageRequestPickup(self._map_state(), person))
            elif message.startswith("I suggest you pick up"):
                person = message.replace("I suggest you pick up ", "").replace(
                    " is far away and you can move faster. If you agree press the "
                    "\"Yes\" button, if you do not agree press \"No\".",
                    "")
                person = person[:person.index("because") - 1]
                self._save_action_to_file(MessageSuggestPickup(self._map_state(), person))
            elif message.endswith("because I am traversing the whole area."):
                person = message.replace(" because I am traversing the whole area.", "").replace("Found ", "")
                if person not in self._found_victims:
                    self._found_victims.append(person)
            elif message.startswith("Searching through whole"):
                room_name = message.replace("Searching through whole area ", "")
                room_name = room_name[:room_name.index("because") - 1]
                if room_name not in self._visited_rooms:
                    self._visited_rooms.append(room_name)
            elif message.startswith("Delivered "):
                self._save_action_to_file(MessageDelivered(self._map_state()))

            # Remove message from list
            self.received_messages.remove(message)

    def _check_enter_room(self):

        human = self.state.get_agents()[1]

        room_name = is_in_room(human["location"])

        if room_name is None:
            self._human_in_room = False
        elif not self._human_in_room:

            self._save_action_to_file(EnterRoom(self._map_state(), room_name))
            self._human_in_room = True

            if room_name not in self._visited_rooms:
                self._visited_rooms.append(room_name)
                self._save_action_to_file(EnterUnvisitedRoom(self._map_state(), room_name))

    def _check_pick_up(self):
        human = self.state.get_agents()[1]

        if not self._human_is_carrying and len(human["is_carrying"]) > 0:
            person = human["is_carrying"][0]["name"]
            location = human["location"]
            self._save_action_to_file(PickUp(self._map_state(), person, location))
            self._human_is_carrying = True
            self._carried_person = person

    def _check_drop_off(self):
        human = self.state.get_agents()[1]

        if self._human_is_carrying and len(human["is_carrying"]) == 0:
            person = self._carried_person
            location = human["location"]
            self._save_action_to_file(DropOff(self._map_state(), person, location))
            self._human_is_carrying = False
            self._carried_person = None

    def _check_found_victim(self):
        human = self.state.get_agents()[1]

        for person in self._map_state()["persons"]:
            if person not in self._found_victims and not is_correct_drop_location(
                    person["name"], person["location"]) and "injured" in person["name"] and is_in_range(
                person["location"], human["location"]):
                self._found_victims.append(person)

                location = human["location"]
                self._save_action_to_file(FoundVictim(self._map_state(), person, location))
