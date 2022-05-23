class AgentAction:
    def __init__(self, map_state):
        self.map_state = map_state

    def __str__(self):
        return str(self.__class__) + ": " + str(self.__dict__)


class MessageAskGender(AgentAction):
    def __init__(self, map_state, room_name):
        self.room_name = room_name
        super().__init__(map_state)


class MessageRequestPickup(AgentAction):
    def __init__(self, map_state, person):
        self.person = person
        super().__init__(map_state)


class MessageSuggestPickup(AgentAction):
    def __init__(self, map_state, person):
        self.person = person
        super().__init__(map_state)


class MessageDelivered(AgentAction):
    def __init__(self, map_state):
        super().__init__(map_state)
