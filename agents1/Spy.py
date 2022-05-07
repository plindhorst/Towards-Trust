from matrx.agents import AgentBrain
import pickle

from actions1.AgentAction import MessageAskGender, MessageRequestPickup, MessageSuggestPickup
from actions1.HumanAction import MessageSearch, MessageFound, EnterRoom, MessagePickUp, DropOff, PickUp, MessageBoy, \
    MessageGirl, MessageNo, MessageYes
from actions1.util import is_in_room

ACTION_FILE = "./actions.pkl"


# This agent class records actions and messages of the human/agent
class Spy(AgentBrain):
    def __init__(self):
        super().__init__()

        self._human_is_carrying = False
        self._carried_person = None
        self._human_in_room = False
        self._last_action = None

        f = open(ACTION_FILE, "w+")  # init action file
        f.close()

    # This method gets called every tick
    def decide_on_action(self, state):

        self._read_human_messages()  # Remember communicated actions
        self._check_enter_room()  # Check if human enters a room
        self._check_pick_up()  # Check if human picks up a person
        self._check_drop_off()  # Check if human drops up a person

        return None, {}

    # Save action to pickle file
    def _save_action_to_file(self, action):
        self._last_action = action
        with open(ACTION_FILE, 'ab+') as out:
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

            # Remove message from list
            self.received_messages.remove(message)

    def _check_enter_room(self):

        human = self.state.get_agents()[2]

        room_name = is_in_room(human["location"])

        if room_name is None:
            self._human_in_room = False
        elif not self._human_in_room:

            self._save_action_to_file(EnterRoom(self._map_state(), room_name))
            self._human_in_room = True

    def _check_pick_up(self):
        human = self.state.get_agents()[2]

        if not self._human_is_carrying and len(human["is_carrying"]) > 0:
            person = human["is_carrying"][0]["name"]
            location = human["location"]
            self._save_action_to_file(PickUp(self._map_state(), person, location))
            self._human_is_carrying = True
            self._carried_person = person

    def _check_drop_off(self):
        human = self.state.get_agents()[2]

        if self._human_is_carrying and len(human["is_carrying"]) == 0:
            person = self._carried_person
            location = human["location"]
            self._save_action_to_file(DropOff(self._map_state(), person, location))
            self._human_is_carrying = False
            self._carried_person = None
