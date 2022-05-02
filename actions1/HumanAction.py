class HumanAction:
    def __init__(self, tick):
        self.tick = tick


class MessageSearch(HumanAction):
    def __init__(self, tick, room_name):
        super().__init__(tick)
        self.room_name = room_name


class MessageFound(HumanAction):
    def __init__(self, tick, person):
        super().__init__(tick)
        self.person = person


class EnterRoom(HumanAction):
    def __init__(self, tick, room_name):
        super().__init__(tick)
        self.room_name = room_name

