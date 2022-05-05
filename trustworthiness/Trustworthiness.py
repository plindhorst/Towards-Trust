import os
import pickle

from actions1.HumanAction import MessageSearch, EnterRoom

ACTION_FILE = "./actions.pkl"


class Trustworthiness:
    def __init__(self):
        self._human_actions = []

        self._read_action_file()

    def _read_action_file(self):
        self._human_actions = []

        if not os.path.isfile(ACTION_FILE):
            return

        with open(ACTION_FILE, 'rb') as fr:
            try:
                while True:
                    self._human_actions.append(pickle.load(fr))
            except EOFError:
                pass

    # Returns the amount of rooms the human does not visit after communicating that he will visit them
    def check_searched_rooms(self):
        count = 0
        lies = 0
        # TODO: ignore visited rooms
        for i, action in enumerate(self._human_actions):
            if type(action) is MessageSearch:
                count += 1
                entered_room = False
                for j, other_action in enumerate(self._human_actions):
                    if i < j:  # Make sure to check only next actions
                        if type(other_action) is EnterRoom:
                            print(action.room_name, "->", other_action.room_name)
                            if action.room_name != other_action.room_name:
                                lies += 1
                            entered_room = True
                            break

                if not entered_room:
                    lies += 1

        print(count - lies, "/", count, " correct room searches")
