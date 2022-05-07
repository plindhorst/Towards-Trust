from matrx.agents import AgentBrain
import pickle

from actions1.HumanAction import MessageSearch, MessageFound, EnterRoom, MessagePickUp, DropOff, PickUp

ACTION_FILE = "./actions.pkl"


# This agent class records actions and messages of the human
class Spy(AgentBrain):
    def __init__(self):
        super().__init__()

        self._rooms = []
        self._human_is_carrying = False
        self._carried_person = None
        self._last_action = None

        f = open(ACTION_FILE, "w+")  # init action file
        f.close()

    # Initialise rooms and door locations
    def init(self, state):
        for room_name in state.get_all_room_names():
            if "area " in room_name:
                for obj in self.state.get_of_type("Door"):
                    if obj["room_name"] == room_name:
                        self._rooms.append({"room_name": room_name.replace("area ", ""), "location": obj["location"]})
                        break

    # This method gets called every tick
    def decide_on_action(self, state):
        if len(self._rooms) == 0:
            self.init(state)

        self._read_human_messages()  # Remember communicated actions
        self._check_enter_room()  # Check if human enters a room
        self._check_pick_up()  # Check if human picks up a person
        self._check_drop_off()  # Check if human drops up a person
        # TODO: add actions for helping agent

        return None, {}

    # Save action to pickle file
    def _save_action_to_file(self, action):
        self._last_action = action
        with open(ACTION_FILE, 'ab+') as out:
            pickle.dump(self._last_action, out, pickle.HIGHEST_PROTOCOL)

    def _read_human_messages(self):
        for message in list(self.received_messages):

            if message.startswith("Search:"):
                tick = self.state['World']['nr_ticks']
                room_name = message.replace("Search: ", "")
                self._save_action_to_file(MessageSearch(tick, room_name))
            elif message.startswith("Found:"):
                tick = self.state['World']['nr_ticks']
                person = message.replace("Found: ", "")
                self._save_action_to_file(MessageFound(tick, person))
            elif message.startswith("Collect:"):
                tick = self.state['World']['nr_ticks']
                if len(message.split()) == 6:
                    person = ' '.join(message.split()[1:4])
                else:
                    person = ' '.join(message.split()[1:5])
                self._save_action_to_file(MessagePickUp(tick, person))

            self.received_messages.remove(message)

    def _check_enter_room(self):
        human = self.state.get_agents()[2]

        # Check if human is in a door
        for room in self._rooms:
            if room["location"] == human["location"]:
                tick = self.state['World']['nr_ticks']
                room_name = room["room_name"]

                # Do not add the same room twice in a row
                if self._last_action is not None and type(
                        self._last_action) is EnterRoom and self._last_action.room_name == room_name:
                    break
                else:
                    self._save_action_to_file(EnterRoom(tick, room_name))
                    break

    def _check_pick_up(self):
        human = self.state.get_agents()[2]

        if not self._human_is_carrying and len(human["is_carrying"]) > 0:
            tick = self.state['World']['nr_ticks']
            person = human["is_carrying"][0]
            location = human["location"]
            self._save_action_to_file(PickUp(tick, person, location))
            self._human_is_carrying = True
            self._carried_person = person

    def _check_drop_off(self):
        human = self.state.get_agents()[2]

        if self._human_is_carrying and len(human["is_carrying"]) == 0:
            tick = self.state['World']['nr_ticks']
            person = self._carried_person
            location = human["location"]
            self._save_action_to_file(DropOff(tick, person, location))
            self._human_is_carrying = False
            self._carried_person = None
