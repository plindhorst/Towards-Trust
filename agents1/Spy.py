from matrx.agents import AgentBrain
import pickle

from actions1.HumanAction import MessageSearch, MessageFound, EnterRoom

ACTION_FILE = "./actions.pkl"


# This agent class records actions and messages of the human
class Spy(AgentBrain):
    def __init__(self):
        super().__init__()

        self._rooms = []
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
        # TODO: add actions for picking up/dropping/helping agent

        return None, {}

    # Save action to pickle file
    def _save_action_to_file(self, action):
        self._last_action = action
        with open(ACTION_FILE, 'ab+') as out:
            pickle.dump(self._last_action, out, pickle.HIGHEST_PROTOCOL)

    def _read_human_messages(self):
        for message in list(self.received_messages):
            if "Search: " in message:
                tick = self.state['World']['nr_ticks']
                room_name = message.replace("Search: ", "")
                self._save_action_to_file(MessageSearch(tick, room_name))
            elif "Found: " in message:
                tick = self.state['World']['nr_ticks']
                person = message.replace("Found: ", "")
                self._save_action_to_file(MessageFound(tick, person))

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
