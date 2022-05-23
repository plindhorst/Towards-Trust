from world.agents.ControlAgent import ControlAgent


class AdviceAgent(ControlAgent):

    def __init__(self, slowdown: int):
        super().__init__(slowdown)
