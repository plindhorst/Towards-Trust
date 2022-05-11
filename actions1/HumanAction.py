class HumanAction:
    def __init__(self, map_state):
        self.map_state = map_state

    def __str__(self):
        return str(self.__class__) + ": " + str(self.__dict__)


class MessageSearch(HumanAction):
    def __init__(self, map_state, room_name):
        self.room_name = room_name
        super().__init__(map_state)


class MessageFound(HumanAction):
    def __init__(self, map_state, person):
        self.room_name = person.split(" ")[-1]
        self.person = person.replace(self.room_name, "area " + self.room_name)
        super().__init__(map_state)


class MessagePickUp(HumanAction):
    def __init__(self, map_state, person):
        self.person = person
        super().__init__(map_state)


class MessageYes(HumanAction):
    def __init__(self, map_state):
        super().__init__(map_state)


class MessageNo(HumanAction):
    def __init__(self, map_state):
        super().__init__(map_state)


class MessageGirl(HumanAction):
    def __init__(self, map_state):
        super().__init__(map_state)


class MessageBoy(HumanAction):
    def __init__(self, map_state):
        super().__init__(map_state)


class EnterRoom(HumanAction):
    def __init__(self, map_state, room_name):
        self.room_name = room_name
        super().__init__(map_state)


class PickUp(HumanAction):
    def __init__(self, map_state, person, location):
        self.person = person
        self.location = location
        super().__init__(map_state)


class DropOff(HumanAction):
    def __init__(self, map_state, person, location):
        self.person = person
        self.location = location
        super().__init__(map_state)
