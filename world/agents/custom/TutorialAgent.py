import sys, random, enum, ast, time
from matrx import grid_world
from brains1.BW4TBrain import BW4TBrain
from actions1.customActions import *
from matrx import utils
from matrx.grid_world import GridWorld
from matrx.agents.agent_utils.state import State
from matrx.agents.agent_utils.navigator import Navigator
from matrx.agents.agent_utils.state_tracker import StateTracker
from matrx.actions.door_actions import OpenDoorAction
from matrx.actions.object_actions import GrabObject, DropObject
from matrx.messages.message import Message
from matrx.messages.message_manager import MessageManager

class Phase(enum.Enum):
    INTRO0=0,
    INTRO1=1,
    INTRO2=2,
    INTRO3=3,
    INTRO4=4,
    INTRO5=5,
    INTRO6=6,
    INTRO7=7,
    INTRO8=8,
    INTRO9=9,
    INTRO10=10,
    INTRO11=11,
    FIND_NEXT_GOAL=12,
    PICK_UNSEARCHED_ROOM=13,
    PLAN_PATH_TO_ROOM=14,
    FOLLOW_PATH_TO_ROOM=15,
    PLAN_ROOM_SEARCH_PATH=16,
    FOLLOW_ROOM_SEARCH_PATH=17,
    PLAN_PATH_TO_VICTIM=18,
    FOLLOW_PATH_TO_VICTIM=19,
    TAKE_VICTIM=20,
    PLAN_PATH_TO_DROPPOINT=21,
    FOLLOW_PATH_TO_DROPPOINT=22,
    DROP_VICTIM=23,
    WAIT_FOR_HUMAN=24,
    WAIT_AT_ZONE=25,
    FIX_ORDER_GRAB=26,
    FIX_ORDER_DROP=27

class TutorialAgent(BW4TBrain):
    def __init__(self, condition, slowdown:int):
        super().__init__(condition, slowdown)
        self._phase=Phase.INTRO0
        self._roomVics = []
        self._searchedRooms = ['area C3', 'area C2']
        self._foundVictims = []
        self._collectedVictims = ['critically injured girl']
        self._foundVictimLocs = {}
        self._maxTicks = 100000
        self._sendMessages = []
        self._currentDoor=None
        self._condition = condition
        self._providedExplanations = []

    def initialize(self):
        self._state_tracker = StateTracker(agent_id=self.agent_id)
        self._navigator = Navigator(agent_id=self.agent_id,
                                    action_set=self.action_set, algorithm=Navigator.A_STAR_ALGORITHM)

    def filter_bw4t_observations(self, state):
        self._processMessages(state)
        return state

    def decide_on_bw4t_action(self, state:State):

        while True:
            if Phase.INTRO0==self._phase:
                self._sendMessage('Hello! My name is RescueBot. During this experiment we will collaborate and communicate with each other. \
                It is our goal to search and rescue the victims on the drop zone on our left as quickly as possible.  \
                We have to rescue the victims in order from left to right, so it is important to only drop a victim when the previous one already has been dropped. \
                You will receive and send messages in the chatbox. You can send your messages using the buttons. It is recommended to send messages \
                when you will search in an area, when you find one of the victims, and when you are going to pick up a victim.  \
                There are 8 victim and 3 injury types. The red color refers to critically injured victims, yellow to mildly injured victims, and green to healthy victims. \
                The 8 victims are a girl (critically injured girl/mildly injured girl/healthy girl), boy (critically injured boy/mildly injured boy/healthy boy), \
                woman (critically injured woman/mildly injured woman/healthy woman), man (critically injured man/mildly injured man/healthy man), \
                elderly woman (critically injured elderly woman/mildly injured elderly woman/healthy elderly woman), \
                elderly man (critically injured elderly man/mildly injured elderly man/healthy elderly man), dog (critically injured dog/mildly injured dog/healthy dog), \
                and a cat (critically injured cat/mildly injured cat/healthy cat). In the toolbar above you can find the keyboard controls, for moving you can simply use the arrow keys. Your sense range is limited to 1, so it is important to search the areas well.\
                We will now practice and familiarize you with everything mentioned above, until you are comfortable enough to start the real experiment. \
                If you read the text, press the "Ready!" button.', 'RescueBot')
                if self.received_messages and self.received_messages[-1]=='Ready!':
                    self._phase=Phase.INTRO1
                    self.received_messages=[]
                else:
                    return None,{}

            if Phase.INTRO1==self._phase:
                self._sendMessage('Lets try out the controls first. You can move with the arrow keys. If you move up twice, you will notice that you can now no longer see me in your field of view. \
                So you can only see as far as 1 grid cell. Therefore, it is important to search the areas well. If you moved up twice, press the "Ready!" button.','RescueBot')
                if self.received_messages and self.received_messages[-1]=='Ready!':
                    self._phase=Phase.INTRO2
                    self.received_messages=[]
                else:
                    return None,{}

            if Phase.INTRO2==self._phase:
                self._sendMessage('Lets move to area C3 now, and search it completely. In this area you should find 4 victims. One of them is our first goal victim on the drop zone: critically injured girl, the other three are healthy. \
                If you searched the whole area and found the 4 victims, press the "Ready!" button.', 'RescueBot')
                if self.received_messages and self.received_messages[-1]=='Ready!':
                    self._phase=Phase.INTRO3
                    self.received_messages=[]
                else:
                    return None,{}

            if Phase.INTRO3==self._phase:
                self._sendMessage('Lets pick up our first goal victim critically injured girl now. To pick up a victim, move yourself on the victim first. \
                Now, you can press "B" or "Q" on your keyboard to grab the victim. If you now move left, right, up, or down once, you can see the victim is no longer there. \
                You can only carry one victim at a time. \
                If you finished this step, press the "Ready!" button.', 'RescueBot')
                if self.received_messages and self.received_messages[-1]=='Ready!':
                    self._phase=Phase.INTRO4
                    self.received_messages=[]
                else:
                    return None,{}

            if Phase.INTRO4==self._phase:
                self._sendMessage('Lets drop our first goal victim critically injured girl at the drop zone now. The drop zone is located at the lower left of the environment, next to where you started. \
                You can move to the drop zone using the arrow keys. If you reach the drop zone, move on top of the image of the first goal victim you are currently carrying (critically injured girl). \
                This is the most left image on the drop zone, because it is the first victim to rescue. If you are located on top of this image, press "N" or "E" on your keyboard to drop the victim. \
                If you now move right once, you can see that you dropped critically injured girl in the right place. If you finished this step, press the "Ready!" button.', 'RescueBot')
                if self.received_messages and self.received_messages[-1]=='Ready!':
                    self._phase=Phase.INTRO5
                    self.received_messages=[]
                else:
                    return None,{}

            if Phase.INTRO5==self._phase:
                self._sendMessage('You just dropped the first victim, nice! Time for the next step and goal victim critically injured elderly woman. Lets move to and search through area C2 for this victim. But this time, let me know in the chat that you are going to search in area C2. \
                You can do this using the button "C2". By doing so, you will make sure that I will not also search for critically injured elderly woman in this area. This way, we can collaborate more efficiently! \
                If you pressed the button "C2" and moved to the entrance of the area, press the "Ready!" button.', 'RescueBot')
                if self.received_messages and self.received_messages[-1]=='Ready!':
                    self._phase=Phase.INTRO6
                    self.received_messages=[]
                else:
                    return None,{}

            if Phase.INTRO6==self._phase:
                self._sendMessage('You should now be present in area C2. If you search this area you should find critically injured elderly woman and mildly injured cat. \
                When you find one of our goal victims in an area, it is important to communicate this with me in the chat. You can do so using the buttons below "I have found:". \
                For example, in this area you should press the button "critically injured elderly woman in C2" and "mildly injured cat in C2". You can select the correct room using the dropdown menu. \
                Communicating this information with me can improve efficiency, so it is highly recommended! If you searched the whole area, found the 2 victims, and communicated this using the "found" buttons, press the "Ready!" button.', 'RescueBot')
                if self.received_messages and self.received_messages[-1]=='Ready!':
                    self._foundVictimLocs['mildly injured cat'] = {'room':'area C2'}
                    self._phase=Phase.INTRO7
                    self.received_messages=[]
                else:
                    return None,{}

            if Phase.INTRO7==self._phase:
                self._sendMessage('Lets pick up the next goal victim to drop off at the drop zone: critically injured elderly woman in area C2. But this time, let me know you will pick up this victim using the corresponding button. \
                Similar to when you found this victim, select the button "critically injured elderly woman in C2" below "I will pick up:" in the chat window. \
                This way, I will know that I no longer have to search this goal victim, and can start searching for the next goal victim to rescue: critically injured man. \
                After sending the message to me, pick up/grab critically injured elderly woman, move to the drop zone, and drop critically injured elderly woman in the right place. \
                If you did so, press the "Ready!" button.', 'RescueBot')
                if self.received_messages and self.received_messages[-1]=='Ready!':
                    self._phase=Phase.INTRO8
                    self.received_messages=[]
                else:
                    return None,{}

            if Phase.INTRO8==self._phase:
                self._sendMessage('You just rescued the second goal victim critically injured elderly woman, great work! You should now have a good understanding of the controls and messaging system. \
                The next step is a small trial of how the real experiment will be. So now I will also be moving to and searching through areas, picking up and dropping off victims, and communicating this relevant info with you during the mission. \
                We still have to rescue the following victims in this order: critically injured man, critically injured dog, mildly injured boy, mildly injured elderly man, mildly injured woman, mildly injured cat. \
                Once we delivered the last victim mildly injured cat, the game will end automatically. If you are ready to start searching for critically injured man, press the "Ready!" button.' , 'RescueBot')
                if self.received_messages and self.received_messages[-1]=='Ready!':
                    self._currentTick = state['World']['nr_ticks']
                    self._phase=Phase.FIND_NEXT_GOAL
                    self.received_messages=[]
                else:
                    return None,{}

            if Phase.FIND_NEXT_GOAL==self._phase:
                zones = self._getDropZones(state)
                locs = [zone['location'] for zone in zones]
                self._firstVictim = str(zones[0]['img_name'])[8:-4]
                self._lastVictim = str(zones[-1]['img_name'])[8:-4]
                remainingZones = []
                for info in zones:
                    if str(info['img_name'])[8:-4] not in self._collectedVictims:
                        remainingZones.append(info)
                if remainingZones:
                    self._goalVic = str(remainingZones[0]['img_name'])[8:-4]
                    self._goalLoc = remainingZones[0]['location']
                    self._remainingZones = remainingZones
                else:
                    return None,{}

                if self._goalVic not in self._foundVictims:
                    self._phase=Phase.PICK_UNSEARCHED_ROOM
                    return Idle.__name__,{'duration_in_ticks':25}

                if self._goalVic in self._foundVictims and 'location' in self._foundVictimLocs[self._goalVic].keys():
                    if self._condition!="silent" and self._foundVictimLocs[self._goalVic]['room'] in ['area A1', 'area A2', 'area A3', 'area A4'] and state[self.agent_id]['location'] in locs and self._collectedVictims:
                        if self._condition == "explainable":
                            self._sendMessage('I suggest you pick up ' + self._goalVic + ' in ' + self._foundVictimLocs[self._goalVic]['room'] + ' because ' + self._foundVictimLocs[self._goalVic]['room'] + ' is far away and you can move faster. If you agree press the "Yes" button, if you do not agree press "No".', 'RescueBot')
                        if self._condition == "transparent":
                            self._sendMessage('I suggest you pick up ' + self._goalVic + ' in ' + self._foundVictimLocs[self._goalVic]['room'] + '. If you agree press the "Yes" button, if you do not agree press "No".', 'RescueBot')
                        if self._condition == "adaptive":
                            msg1 = 'I suggest you pick up ' + self._goalVic + ' in ' + self._foundVictimLocs[self._goalVic]['room'] + ' because ' + self._foundVictimLocs[self._goalVic]['room'] + ' is far away and you can move faster. If you agree press the "Yes" button, if you do not agree press "No".'
                            msg2 = 'I suggest you pick up ' + self._goalVic + ' in ' + self._foundVictimLocs[self._goalVic]['room'] + '. If you agree press the "Yes" button, if you do not agree press "No".'
                            explanation = 'because it is located far away and you can move faster'
                            self._dynamicMessage(msg1,msg2,explanation,'RescueBot')

                        if self.received_messages and self.received_messages[-1]=='Yes' or self._goalVic in self._collectedVictims:
                            self._collectedVictims.append(self._goalVic)
                            self._phase=Phase.FIND_NEXT_GOAL
                        if self.received_messages and self.received_messages[-1]=='No' or state['World']['nr_ticks'] > self._tick + 579:
                            self._phase=Phase.PLAN_PATH_TO_VICTIM
                        return Idle.__name__,{'duration_in_ticks':50}
                    else:
                        self._phase=Phase.PLAN_PATH_TO_VICTIM
                        return Idle.__name__,{'duration_in_ticks':50}

                if self._goalVic in self._foundVictims and 'location' not in self._foundVictimLocs[self._goalVic].keys():
                    if self._condition!="silent" and self._foundVictimLocs[self._goalVic]['room'] in ['area A1', 'area A2', 'area A3', 'area A4'] and state[self.agent_id]['location'] in locs and self._collectedVictims:
                        if self._condition=="explainable":
                            self._sendMessage('I suggest you pick up ' + self._goalVic + ' in ' + self._foundVictimLocs[self._goalVic]['room'] + ' because ' + self._foundVictimLocs[self._goalVic]['room'] + ' is far away and you can move faster. If you agree press the "Yes" button, if you do not agree press "No".', 'RescueBot')
                        if self._condition=="transparent":
                            self._sendMessage('I suggest you pick up ' + self._goalVic + ' in ' + self._foundVictimLocs[self._goalVic]['room'] + '. If you agree press the "Yes" button, if you do not agree press "No".', 'RescueBot')
                        if self._condition=="adaptive":
                            msg1 = 'I suggest you pick up ' + self._goalVic + ' in ' + self._foundVictimLocs[self._goalVic]['room'] + ' because ' + self._foundVictimLocs[self._goalVic]['room'] + ' is far away and you can move faster. If you agree press the "Yes" button, if you do not agree press "No".'
                            msg2 = 'I suggest you pick up ' + self._goalVic + ' in ' + self._foundVictimLocs[self._goalVic]['room'] + '. If you agree press the "Yes" button, if you do not agree press "No".'
                            explanation = 'because it is located far away and you can move faster'
                            self._dynamicMessage(msg1,msg2,explanation,'RescueBot')

                        if self.received_messages and self.received_messages[-1]=='Yes' or self._goalVic in self._collectedVictims:
                            self._collectedVictims.append(self._goalVic)
                            self._phase=Phase.FIND_NEXT_GOAL
                        if self.received_messages and self.received_messages[-1]=='No' or state['World']['nr_ticks'] > self._tick + 579:
                            self._phase=Phase.PLAN_PATH_TO_ROOM
                        return Idle.__name__,{'duration_in_ticks':50}
                    else:
                        self._phase=Phase.PLAN_PATH_TO_ROOM
                        return Idle.__name__,{'duration_in_ticks':50}

            if Phase.PICK_UNSEARCHED_ROOM==self._phase:
                agent_location = state[self.agent_id]['location']
                unsearchedRooms=[room['room_name'] for room in state.values()
                                 if 'class_inheritance' in room
                                 and 'Door' in room['class_inheritance']
                                 and room['room_name'] not in self._searchedRooms]
                if self._remainingZones and len(unsearchedRooms) == 0:
                    self._searchedRooms = []
                    self._sendMessages = []
                    self.received_messages = []
                    self._searchedRooms.append(self._door['room_name'])
                    if self._condition=="explainable":
                        self._sendMessage('Going to re-search areas to find ' + self._goalVic +' because we searched all areas but did not find ' + self._goalVic,'RescueBot')
                    if self._condition=="transparent":
                        self._sendMessage('Going to re-search areas','RescueBot')
                    if self._condition=="adaptive":
                        msg1 = 'Going to re-search areas to find ' + self._goalVic +' because we searched all areas but did not find ' + self._goalVic
                        msg2 = 'Going to re-search areas'
                        explanation = 'because we searched all areas'
                        self._dynamicMessage(msg1,msg2,explanation,'RescueBot')
                    self._phase = Phase.FIND_NEXT_GOAL
                else:
                    if self._currentDoor==None:
                        self._door = state.get_room_doors(self._getClosestRoom(state,unsearchedRooms,agent_location))[0]
                    if self._currentDoor!=None:
                        self._door = state.get_room_doors(self._getClosestRoom(state,unsearchedRooms,self._currentDoor))[0]
                    self._phase = Phase.PLAN_PATH_TO_ROOM

            if Phase.PLAN_PATH_TO_ROOM==self._phase:
                self._navigator.reset_full()
                if self._goalVic in self._foundVictims and 'location' not in self._foundVictimLocs[self._goalVic].keys():
                    self._door = state.get_room_doors(self._foundVictimLocs[self._goalVic]['room'])[0]
                    doorLoc = self._door['location']
                else:
                    doorLoc = self._door['location']
                self._navigator.add_waypoints([doorLoc])
                self._phase=Phase.FOLLOW_PATH_TO_ROOM

            if Phase.FOLLOW_PATH_TO_ROOM==self._phase:
                if self._goalVic in self._collectedVictims:
                    self._currentDoor=None
                    self._phase=Phase.FIND_NEXT_GOAL
                if self._goalVic in self._foundVictims and self._door['room_name']!=self._foundVictimLocs[self._goalVic]['room']:
                    self._currentDoor=None
                    self._phase=Phase.FIND_NEXT_GOAL
                if self._door['room_name'] in self._searchedRooms and self._goalVic not in self._foundVictims:
                    self._currentDoor=None
                    self._phase=Phase.FIND_NEXT_GOAL
                else:
                    self._state_tracker.update(state)
                    if self._condition!="silent" and self._condition!="transparent" and self._goalVic in self._foundVictims and str(self._door['room_name']) == self._foundVictimLocs[self._goalVic]['room']:
                        self._sendMessage('Moving to ' + str(self._door['room_name']) + ' to pick up ' + self._goalVic+'.', 'RescueBot')
                    if self._condition!="silent" and self._goalVic not in self._foundVictims:
                        if self._condition=="explainable":
                            self._sendMessage('Moving to ' + str(self._door['room_name']) + ' to search for ' + self._goalVic + ' and because it is the closest unsearched area.', 'RescueBot')
                        if self._condition=="adaptive":
                            msg1 = 'Moving to ' + str(self._door['room_name']) + ' to search for ' + self._goalVic + ' and because it is the closest unsearched area.'
                            msg2 = 'Moving to ' + str(self._door['room_name']) + ' to search for ' + self._goalVic+'.'
                            explanation = 'because it is the closest unsearched area'
                            self._dynamicMessage(msg1,msg2,explanation,'RescueBot')
                    if self._condition=="transparent":
                        self._sendMessage('Moving to ' + str(self._door['room_name'])+'.', 'RescueBot')
                    self._currentDoor=self._door['location']
                    action = self._navigator.get_move_action(self._state_tracker)
                    if action!=None:
                        return action,{}
                    self._phase=Phase.PLAN_ROOM_SEARCH_PATH
                    return Idle.__name__,{'duration_in_ticks':50}

            if Phase.PLAN_ROOM_SEARCH_PATH==self._phase:
                roomTiles = [info['location'] for info in state.values()
                             if 'class_inheritance' in info
                             and 'AreaTile' in info['class_inheritance']
                             and 'room_name' in info
                             and info['room_name'] == self._door['room_name']
                             ]
                self._roomtiles=roomTiles
                self._navigator.reset_full()
                self._navigator.add_waypoints(self._efficientSearch(roomTiles))
                if self._condition=="explainable":
                    self._sendMessage('Searching through whole ' + str(self._door['room_name']) + ' because my sense range is limited and to find ' + self._goalVic+'.', 'RescueBot')
                if self._condition=="transparent":
                    self._sendMessage('Searching through whole ' + str(self._door['room_name']) + '.', 'RescueBot')
                if self._condition=="adaptive":
                    msg1 = 'Searching through whole ' + str(self._door['room_name']) + ' because my sense range is limited and to find ' + self._goalVic+'.'
                    msg2 = 'Searching through whole ' + str(self._door['room_name'])+'.'
                    explanation = 'because my sense range is limited'
                    self._dynamicMessage(msg1,msg2,explanation,'RescueBot')
                #self._currentDoor = self._door['location']
                self._roomVics=[]
                self._phase=Phase.FOLLOW_ROOM_SEARCH_PATH
                return Idle.__name__,{'duration_in_ticks':50}

            if Phase.FOLLOW_ROOM_SEARCH_PATH==self._phase:
                self._state_tracker.update(state)
                action = self._navigator.get_move_action(self._state_tracker)
                if action!=None:

                    for info in state.values():
                        if 'class_inheritance' in info and 'CollectableBlock' in info['class_inheritance']:
                            vic = str(info['img_name'][8:-4])
                            if vic not in self._roomVics:
                                self._roomVics.append(vic)

                            if vic in self._foundVictims and 'location' not in self._foundVictimLocs[vic].keys():
                                self._foundVictimLocs[vic] = {'location':info['location'],'room':self._door['room_name'],'obj_id':info['obj_id']}
                                if vic == self._goalVic:
                                    if self._condition=="explainable":
                                        self._sendMessage('Found '+ vic + ' in ' + self._door['room_name'] + ' because you told me '+vic+ ' was located here.', 'RescueBot')
                                    if self._condition=="transparent":
                                        self._sendMessage('Found '+ vic + ' in ' + self._door['room_name']+'.', 'RescueBot')
                                    if self._condition=="adaptive":
                                        msg1 = 'Found '+ vic + ' in ' + self._door['room_name'] + ' because you told me '+vic+ ' was located here.'
                                        msg2 = 'Found '+ vic + ' in ' + self._door['room_name']+'.'
                                        explanation = 'because you told me it was located here'
                                        self._dynamicMessage(msg1,msg2,explanation,'RescueBot')
                                    self._searchedRooms.append(self._door['room_name'])
                                    self._phase=Phase.FIND_NEXT_GOAL

                            if 'healthy' not in vic and vic not in self._foundVictims:
                                if self._condition=="explainable":
                                    self._sendMessage('Found '+ vic + ' in ' + self._door['room_name'] + ' because I am traversing the whole area.', 'RescueBot')
                                if self._condition=="transparent":
                                    self._sendMessage('Found '+ vic + ' in ' + self._door['room_name']+'.', 'RescueBot')
                                if self._condition=="adaptive":
                                    msg1 = 'Found '+ vic + ' in ' + self._door['room_name'] + ' because I am traversing the whole area.'
                                    msg2 = 'Found '+ vic + ' in ' + self._door['room_name']+'.'
                                    explanation = 'because I am traversing the whole area'
                                    self._dynamicMessage(msg1,msg2,explanation,'RescueBot')
                                self._foundVictims.append(vic)
                                self._foundVictimLocs[vic] = {'location':info['location'],'room':self._door['room_name'],'obj_id':info['obj_id']}
                    return action,{}
                #if self._goalVic not in self._foundVictims:
                #    self._sendMessage(self._goalVic + ' not present in ' + str(self._door['room_name']) + ' because I searched the whole area without finding ' + self._goalVic, 'RescueBot')
                if self._goalVic in self._foundVictims and self._goalVic not in self._roomVics and self._foundVictimLocs[self._goalVic]['room']==self._door['room_name']:
                    if self._condition=="explainable":
                        self._sendMessage(self._goalVic + ' not present in ' + str(self._door['room_name']) + ' because I searched the whole area without finding ' + self._goalVic+'.', 'RescueBot')
                    if self._condition=="transparent":
                        self._sendMessage(self._goalVic + ' not present in ' + str(self._door['room_name'])+'.', 'RescueBot')
                    if self._condition=="adaptive":
                        msg1 = self._goalVic + ' not present in ' + str(self._door['room_name']) + ' because I searched the whole area without finding ' + self._goalVic+'.'
                        msg2 = self._goalVic + ' not present in ' + str(self._door['room_name'])+'.'
                        explanation = 'because I searched the whole area'
                        self._dynamicMessage(msg1,msg2,explanation,'RescueBot')
                    self._foundVictimLocs.pop(self._goalVic, None)
                    self._foundVictims.remove(self._goalVic)
                    self._roomVics = []
                    self.received_messages = []
                self._searchedRooms.append(self._door['room_name'])
                self._phase=Phase.FIND_NEXT_GOAL
                return Idle.__name__,{'duration_in_ticks':50}

            if Phase.PLAN_PATH_TO_VICTIM==self._phase:
                if self._condition=="explainable":
                    self._sendMessage('Picking up ' + self._goalVic + ' in ' + self._foundVictimLocs[self._goalVic]['room'] + ' because ' + self._goalVic + ' should be transported to the drop zone.', 'RescueBot')
                if self._condition=="transparent":
                    self._sendMessage('Picking up ' + self._goalVic + ' in ' + self._foundVictimLocs[self._goalVic]['room']+'.', 'RescueBot')
                if self._condition=="adaptive":
                    msg1 = 'Picking up ' + self._goalVic + ' in ' + self._foundVictimLocs[self._goalVic]['room'] + ' because ' + self._goalVic + ' should be transported to the drop zone.'
                    msg2 = 'Picking up ' + self._goalVic + ' in ' + self._foundVictimLocs[self._goalVic]['room']+'.'
                    explanation = 'because it should be transported to the drop zone'
                    self._dynamicMessage(msg1,msg2,explanation,'RescueBot')
                self._navigator.reset_full()
                self._navigator.add_waypoints([self._foundVictimLocs[self._goalVic]['location']])
                self._phase=Phase.FOLLOW_PATH_TO_VICTIM
                return Idle.__name__,{'duration_in_ticks':50}

            if Phase.FOLLOW_PATH_TO_VICTIM==self._phase:
                if self._goalVic in self._collectedVictims:
                    self._phase=Phase.FIND_NEXT_GOAL
                else:
                    self._state_tracker.update(state)
                    action=self._navigator.get_move_action(self._state_tracker)
                    if action!=None:
                        return action,{}
                    self._phase=Phase.TAKE_VICTIM

            if Phase.TAKE_VICTIM==self._phase:
                self._phase=Phase.PLAN_PATH_TO_DROPPOINT
                self._collectedVictims.append(self._goalVic)
                return GrabObject.__name__,{'object_id':self._foundVictimLocs[self._goalVic]['obj_id']}

            if Phase.PLAN_PATH_TO_DROPPOINT==self._phase:
                self._navigator.reset_full()
                self._navigator.add_waypoints([self._goalLoc])
                self._phase=Phase.FOLLOW_PATH_TO_DROPPOINT

            if Phase.FOLLOW_PATH_TO_DROPPOINT==self._phase:
                if self._condition=="explainable":
                    self._sendMessage('Transporting '+ self._goalVic + ' to the drop zone because ' + self._goalVic + ' should be delivered there for further treatment.', 'RescueBot')
                if self._condition=="transparent":
                    self._sendMessage('Transporting '+ self._goalVic + ' to the drop zone.', 'RescueBot')
                if self._condition=="adaptive":
                    msg1 = 'Transporting '+ self._goalVic + ' to the drop zone because ' + self._goalVic + ' should be delivered there for further treatment.'
                    msg2 = 'Transporting '+ self._goalVic + ' to the drop zone.'
                    explanation = 'because it should be delivered there for further treatment'
                    self._dynamicMessage(msg1,msg2,explanation,'RescueBot')
                self._state_tracker.update(state)
                action=self._navigator.get_move_action(self._state_tracker)
                if action!=None:
                    return action,{}
                self._phase=Phase.DROP_VICTIM
                #return Idle.__name__,{'duration_in_ticks':50}

            if Phase.DROP_VICTIM == self._phase:
                zones = self._getDropZones(state)
                for i in range(len(zones)):
                    if zones[i]['img_name'][8:-4]==self._goalVic:
                        if self._goalVic!=self._firstVictim:
                            self._previousVic = zones[i-1]['img_name']
                        if self._goalVic!=self._lastVictim:
                            self._nextVic = zones[i+1]['img_name']

                if self._goalVic==self._firstVictim or state[{'img_name':self._previousVic,'is_collectable':True}] and self._goalVic==self._lastVictim or state[{'img_name':self._previousVic, 'is_collectable':True}] and not state[{'img_name':self._nextVic, 'is_collectable':True}]:
                    if self._condition=="explainable":
                        self._sendMessage('Delivered '+ self._goalVic + ' at the drop zone because ' + self._goalVic + ' was the current victim to rescue.', 'RescueBot')
                    if self._condition=="transparent":
                        self._sendMessage('Delivered '+ self._goalVic + ' at the drop zone.', 'RescueBot')
                    if self._condition=="adaptive":
                        msg1 = 'Delivered '+ self._goalVic + ' at the drop zone because ' + self._goalVic + ' was the current victim to rescue.'
                        msg2 = 'Delivered '+ self._goalVic + ' at the drop zone.'
                        explanation = 'because it was the current victim to rescue'
                        self._dynamicMessage(msg1,msg2,explanation,'RescueBot')
                    self._phase=Phase.FIND_NEXT_GOAL
                    self._currentDoor = None
                    self._tick = state['World']['nr_ticks']
                    return DropObject.__name__,{}
                #if state[{'img_name':self._nextVic, 'is_collectable':True}] and state[{'img_name':self._previousVic, 'is_collectable':True}]:
                #    self._sendMessage('Delivered '+ self._goalVic + ' at the drop zone because ' + self._goalVic + ' was the current victim to rescue.', 'RescueBot')
                #    self._phase=Phase.FIX_ORDER_GRAB
                #    return DropObject.__name__,{}
                else:
                    if self._condition=="explainable":
                        self._sendMessage('Waiting for human operator at drop zone because previous victim should be collected first.', 'RescueBot')
                    if self._condition=="transparent":
                        self._sendMessage('Waiting for human operator at drop zone.', 'RescueBot')
                    if self._condition=="adaptive":
                        msg1 = 'Waiting for human operator at drop zone because previous victim should be collected first.'
                        msg2 = 'Waiting for human operator at drop zone.'
                        explanation = 'because previous victim should be collected first'
                        self._dynamicMessage(msg1,msg2,explanation,'RescueBot')
                    return None,{}

                    #if Phase.FIX_ORDER_GRAB == self._phase:
            #    self._navigator.reset_full()
            #    self._navigator.add_waypoints([state[{'img_name':self._nextVic, 'is_collectable':True}]['location']])
            #    self._state_tracker.update(state)
            #    action=self._navigator.get_move_action(self._state_tracker)
            #    if action!=None:
            #        return action,{}
            #    self._phase=Phase.FIX_ORDER_DROP
            #    return GrabObject.__name__,{'object_id':state[{'img_name':self._nextVic, 'is_collectable':True}]['obj_id']}

            #if Phase.FIX_ORDER_DROP==self._phase:
            #    self._phase=Phase.FIND_NEXT_GOAL
            #    self._tick = state['World']['nr_ticks']
            #    return DropObject.__name__,{}


    def _getDropZones(self,state:State):
        '''
        @return list of drop zones (their full dict), in order (the first one is the
        the place that requires the first drop)
        '''
        places=state[{'is_goal_block':True}]
        places.sort(key=lambda info:info['location'][1], reverse=True)
        zones = []
        for place in places:
            if place['drop_zone_nr']==0:
                zones.append(place)
        return zones

    def _processMessages(self, state):
        '''
        process incoming messages.
        Reported blocks are added to self._blocks
        '''
        #areas = ['area A1','area A2','area A3','area A4','area B1','area B2','area C1','area C2','area C3']
        for msg in self.received_messages:
            if msg.startswith("Search:"):
                area = 'area '+ msg.split()[-1]
                if area not in self._searchedRooms:
                    self._searchedRooms.append(area)
            if msg.startswith("Found:"):
                if len(msg.split()) == 6:
                    foundVic = ' '.join(msg.split()[1:4])
                else:
                    foundVic = ' '.join(msg.split()[1:5])
                loc = 'area '+ msg.split()[-1]
                if loc not in self._searchedRooms:
                    self._searchedRooms.append(loc)
                if foundVic not in self._foundVictims:
                    self._foundVictims.append(foundVic)
                    self._foundVictimLocs[foundVic] = {'room':loc}
                if foundVic in self._foundVictims and self._foundVictimLocs[foundVic]['room'] != loc:
                    self._foundVictimLocs[foundVic] = {'room':loc}
            if msg.startswith('Collect:'):
                if len(msg.split()) == 6:
                    collectVic = ' '.join(msg.split()[1:4])
                else:
                    collectVic = ' '.join(msg.split()[1:5])
                loc = 'area ' + msg.split()[-1]
                if loc not in self._searchedRooms:
                    self._searchedRooms.append(loc)
                if collectVic not in self._foundVictims:
                    self._foundVictims.append(collectVic)
                    self._foundVictimLocs[collectVic] = {'room':loc}
                if collectVic in self._foundVictims and self._foundVictimLocs[collectVic]['room'] != loc:
                    self._foundVictimLocs[collectVic] = {'room':loc}
                if collectVic not in self._collectedVictims:
                    self._collectedVictims.append(collectVic)
            #if msg.startswith('Mission'):
            #    self._sendMessage('Unsearched areas: '  + ', '.join([i.split()[1] for i in areas if i not in self._searchedRooms]) + '. Collected victims: ' + ', '.join(self._collectedVictims) +
            #    '. Found victims: ' +  ', '.join([i + ' in ' + self._foundVictimLocs[i]['room'] for i in self._foundVictimLocs]) ,'RescueBot')
            #    self.received_messages=[]

    def _sendMessage(self, mssg, sender):
        msg = Message(content=mssg, from_id=sender)
        if msg.content not in self.received_messages:
            self.send_message(msg)
            self._sendMessages.append(msg.content)

        if self.received_messages and self._sendMessages:
            self._last_mssg = self._sendMessages[-1]
            if self._last_mssg.startswith('Searching') or self._last_mssg.startswith('Moving'):
                self.received_messages=[]
                self.received_messages.append(self._last_mssg)

    def _getClosestRoom(self, state, objs, currentDoor):
        agent_location = state[self.agent_id]['location']
        locs = {}
        for obj in objs:
            locs[obj]=state.get_room_doors(obj)[0]['location']
        dists = {}
        for room,loc in locs.items():
            if currentDoor!=None:
                dists[room]=utils.get_distance(currentDoor,loc)
            if currentDoor==None:
                dists[room]=utils.get_distance(agent_location,loc)

        return min(dists,key=dists.get)

    def _efficientSearch(self, tiles):
        x=[]
        y=[]
        for i in tiles:
            if i[0] not in x:
                x.append(i[0])
            if i[1] not in y:
                y.append(i[1])
        locs = []
        for i in range(len(x)):
            if i%2==0:
                locs.append((x[i],min(y)))
            else:
                locs.append((x[i],max(y)))
        return locs

    def _dynamicMessage(self, mssg1, mssg2, explanation, sender):
        if explanation not in self._providedExplanations:
            self._sendMessage(mssg1,sender)
            self._providedExplanations.append(explanation)
        if 'Searching' in mssg1:
            #history = ['Searching' in mssg for mssg in self._sendMessages]
            if explanation in self._providedExplanations and mssg1 not in self._sendMessages[-5:]:
                self._sendMessage(mssg2,sender)
        if 'Found' in mssg1:
            history = [mssg2[:-1] in mssg for mssg in self._sendMessages]
            if explanation in self._providedExplanations and True not in history:
                self._sendMessage(mssg2,sender)
        if 'Searching' not in mssg1 and 'Found' not in mssg1:
            if explanation in self._providedExplanations and self._sendMessages[-1]!=mssg1:
                self._sendMessage(mssg2,sender)
