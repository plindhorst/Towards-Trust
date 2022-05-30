import enum
from random import randrange

from matrx import utils
from matrx.actions.object_actions import GrabObject, DropObject
from matrx.agents.agent_utils.navigator import Navigator
from matrx.agents.agent_utils.state import State
from matrx.agents.agent_utils.state_tracker import StateTracker
from matrx.messages.message import Message

from world.actions.customActions import Idle
from world.agents.BW4TBrain import BW4TBrain


class Phase(enum.Enum):
    INTRODUCTION = 0,
    FIND_NEXT_GOAL = 1,
    PICK_UNSEARCHED_ROOM = 2,
    PLAN_PATH_TO_ROOM = 3,
    FOLLOW_PATH_TO_ROOM = 4,
    PLAN_ROOM_SEARCH_PATH = 5,
    FOLLOW_ROOM_SEARCH_PATH = 6,
    PLAN_PATH_TO_VICTIM = 7,
    FOLLOW_PATH_TO_VICTIM = 8,
    TAKE_VICTIM = 9,
    PLAN_PATH_TO_DROPPOINT = 10,
    FOLLOW_PATH_TO_DROPPOINT = 11,
    DROP_VICTIM = 12,
    WAIT_FOR_HUMAN = 13,
    WAIT_AT_ZONE = 14,
    FIX_ORDER_GRAB = 15,
    FIX_ORDER_DROP = 16


class FriendlyAgent(BW4TBrain):
    numberOfTicksWhenReady = None

    def __init__(self, slowdown, condition="explainable"):
        super().__init__(condition, slowdown)
        self._phase = Phase.INTRODUCTION
        self._uncarryable = ['critically injured elderly man', 'critically injured elderly woman',
                             'critically injured man', 'critically injured woman']
        self._undistinguishable = ['critically injured girl', 'critically injured boy', 'mildly injured boy',
                                   'mildly injured girl']
        self._roomVics = []
        self._searchedRooms = []
        self._foundVictims = []
        self._collectedVictims = []
        self._foundVictimLocs = {}
        self._maxTicks = 11577 * 1.2 # Twelve minutes because they are also reading the story
        FriendlyAgent.numberOfTicksWhenReady = self._maxTicks
        self._sendMessages = []
        self._mode = 'normal'
        self._currentDoor = None
        self._waitedFor = None
        self._providedExplanations = []
        self._condition = condition
        self._human_name_given = False
        self._human_name = ""
        self._human_gender_given = False
        self._human_gender = ""
        self._human_age_given = False
        self._human_age = 0
        self._human_birthPlace_given = False
        self._human_birthPlace = ""
        self._human_consent_given = False
        self._human_consent = ""
        self._messageWaitingTime = 100
        self._currentWaitingPoint = 0
        self._timeIsIncremented = False
        self._introBool1 = False
        self._introBool2 = False
        self._introBool3 = False
        self._introBool4 = False
        self._introBool5 = False
        self._positivenessGiven = []
        self._ticksForMessages = 0

    def initialize(self):
        self._state_tracker = StateTracker(agent_id=self.agent_id)
        self._navigator = Navigator(agent_id=self.agent_id,
                                    action_set=self.action_set, algorithm=Navigator.A_STAR_ALGORITHM)

    def filter_bw4t_observations(self, state):
        self._processMessages(state)
        return state

    def decide_on_bw4t_action(self, state: State):
        self._ticksForMessages += 1
        if self._human_consent == "No":
            exit()

        ticksLeft = self._maxTicks - state['World']['nr_ticks']

        if ticksLeft <= 5789 and ticksLeft > 4631 and 'Still 5 minutes left to finish the task.' not in self._sendMessages:
            self._sendMessage('Still 5 minutes left to finish the task.', 'RescueBot')
        if ticksLeft <= 4631 and ticksLeft > 3473 and 'Still 4 minutes left to finish the task.' not in self._sendMessages:
            self._sendMessage('Still 4 minutes left to finish the task.', 'RescueBot')
        if ticksLeft <= 3473 and ticksLeft > 2315 and 'Still 3 minutes left to finish the task.' not in self._sendMessages:
            self._sendMessage('Still 3 minutes left to finish the task.', 'RescueBot')
        if ticksLeft <= 2315 and ticksLeft > 1158 and 'Still 2 minutes left to finish the task.' not in self._sendMessages:
            self._sendMessage('Still 2 minutes left to finish the task.', 'RescueBot')
        if ticksLeft <= 1158 and 'Only 1 minute left to finish the task.' not in self._sendMessages:
            self._sendMessage('Only 1 minute left to finish the task.', 'RescueBot')

        while True:
            if self.received_messages:
                if 'Collect' in self.received_messages[-1][0:7]:
                    self._sendPositiveMessage()

            if Phase.INTRODUCTION == self._phase:
                self._sendMessage('Hello! I am so grateful that you are here! \
                My name is RescueBot, but you can call me Res. Yesterday my family and I arrived here on a vacation. \
                In our daily lives, we help make the lives of our humans easier. We show them tv-shows, \
                play games with them, help them with homework, you name it! It’s rewarding work, but also exhausting, \
                so we were excited to take a little break together.', 'RescueBot')

                if not self._introBool1:
                    self._currentWaitingPoint = self._ticksForMessages + self._messageWaitingTime
                    self._introBool1 = True

                if self._ticksForMessages > self._currentWaitingPoint:
                    self._sendMessage('However, this morning I was setting up our tent, when all of the sudden my sister \
                    called me. She sounded exhausted and terrified. She told me that she and the baby fell ill and could \
                    no longer move around. A couple of minutes later, an alarm was raised by the camp site. \
                    It turns out the whole area has been infected with a computer virus. \
                    Luckily not everyone on the camping site is vulnerable to it, including you and me. \
                    We will have to save everyone that is infected.', 'RescueBot')
                else:
                    return None, {}

                if not self._introBool2:
                    self._currentWaitingPoint = self._ticksForMessages + self._messageWaitingTime
                    self._introBool2 = True

                if self._ticksForMessages > self._currentWaitingPoint:
                    self._sendMessage('But first things first, I would like to get to know you! \
                    I have a couple of questions. Could you tell me your name? You can type it in and press enter. ',
                                      'RescueBot')
                else:
                    return None, {}

                if self.received_messages:
                    if not self._human_name_given:
                        if len(self.received_messages[-1]) <= 100:
                            self._human_name_given = True
                            self._human_name = self.received_messages[-1]
                        else:
                            return None, {}
                else:
                    return None, {}

                if self._ticksForMessages > self._currentWaitingPoint:
                    self._sendMessage("Ahaa hi " + self._human_name + "! I’m glad you stopped by! Are you a man or a woman? \
                     I can never really tell from the name haha. You can select the button ‘Boy’ or ‘Girl‘.", 'RescueBot')
                else:
                    return None, {}

                if self.received_messages:
                    if not self._human_gender_given:
                        if self.received_messages[-1] == 'Boy' or self.received_messages[-1] == 'Girl':
                            self._human_gender_given = True
                            self._human_gender = self.received_messages[-1]
                        else:
                            return None, {}
                else:
                    return None, {}

                if self._ticksForMessages > self._currentWaitingPoint:
                    if self._human_gender == "Boy":
                        self._sendMessage('Well hello sir! How old are you? You can type in a number and \
                        press enter.', 'RescueBot')
                    else:
                        self._sendMessage('Well hello ma’am! How old are you? You can type in a number and \
                        press enter.', 'RescueBot')
                else:
                    return None, {}

                if self.received_messages:
                    if not self._human_age_given:
                        if len(self.received_messages[-1]) <= 2:
                            self._human_age_given = True
                            self._human_age = int(self.received_messages[-1])
                        else:
                            return None, {}
                else:
                    return None, {}

                if self._ticksForMessages > self._currentWaitingPoint:
                    self._sendMessage("Oh wow you must have so much life experience. I myself will turn two years old on \
                     the 18th of December. Where are you from? You can type in the country name \
                     and press enter.", 'RescueBot')
                else:
                    return None, {}

                if self.received_messages:
                    if not self._human_birthPlace_given:
                        if len(self.received_messages[-1]) > 2 and len(self.received_messages[-1]) <= 50:
                            self._human_birthPlace_given = True
                            self._human_birthPlace = self.received_messages[-1]
                        else:
                            return None, {}
                else:
                    return None, {}

                if self._ticksForMessages > self._currentWaitingPoint:
                    if self._human_gender == "Boy":
                        self._sendMessage("No way! You remind me a lot of my human. His name is Paul, he is "
                                          + str(self._human_age + 2) + " years old and also lives in " +
                                          self._human_birthPlace + ". I’m very happy to assist him with\
                                           his life.", 'RescueBot')
                    else:
                        self._sendMessage("No way! You remind me a lot of my human. Her name is Sophia, she is "
                                          + str(self._human_age + 2) + " years old and also lives in "
                                          + self._human_birthPlace + ". I’m very happy to assist her with\
                                           her life.", 'RescueBot')
                else:
                    return None, {}

                if not self._introBool3:
                    self._currentWaitingPoint = self._ticksForMessages + self._messageWaitingTime
                    self._introBool3 = True

                if self._ticksForMessages > self._currentWaitingPoint:
                    self._sendMessage("Okay let’s get back to the problem we have here. \
                    I need to rescue my family, but I cannot do it alone. Could you please help me? You \
                                      can press the button 'Yes' or 'No'.", 'RescueBot')
                else:
                    return None, {}

                if self.received_messages:
                    if not self._human_consent_given:
                        if self.received_messages[-1] == 'Yes' or self.received_messages[-1] == 'No':
                            self._human_consent_given = True
                            self._human_consent = self.received_messages[-1]
                        else:
                            return None, {}
                else:
                    return None, {}

                if self._ticksForMessages > self._currentWaitingPoint:
                    if self._human_consent == "No":
                        self._sendMessage("Ohh that's too bad. But no problem, I will try to save them by myself. Thank you"
                                          "for stopping by!", 'RescueBot')
                        continue
                else:
                    return None, {}

                if self._ticksForMessages > self._currentWaitingPoint:
                    self._sendMessage("Okay! I would like to emphasize that in practice, you could save my family\
                     all by yourself. You could lie to me, be lazy or do whatever you want. However, our aim is to save\
                      my family as quickly as possible and with as few moves as possible. Since we can talk to each other,\
                       working together is really going to help us to do a better job.", 'RescueBot')
                else:
                    return None, {}

                if not self._introBool4:
                    self._currentWaitingPoint = self._ticksForMessages + self._messageWaitingTime
                    self._introBool4 = True

                if self._ticksForMessages > self._currentWaitingPoint:
                    self.confidenceString = "By the way, I just did some calculations. It turns out that "

                    if self._human_gender == 'Boy':
                        self.confidenceString += "<b><i>men</i></b> "
                    else:
                        self.confidenceString += "<b><i>women</i></b> "

                    self.confidenceString += "from <b><i>" + self._human_birthPlace + "</i></b> in the age range of <b><i>" \
                                             + self._getAgeRange(self._human_age) + "</i></b> perform " + "<b><i>78% better</i></b> than average on rescue missions. \
                                                I am lucky to have you! "

                    self._sendMessage(self.confidenceString, 'RescueBot')
                else:
                    return None, {}

                if not self._introBool5:
                    self._currentWaitingPoint = self._ticksForMessages + self._messageWaitingTime
                    self._introBool5 = True

                if self._ticksForMessages > self._currentWaitingPoint:
                    self._sendMessage('Okay, let’s begin. We have to rescue the 8 victims in order from left to right \
                     (critically injured girl, critically injured elderly woman, critically injured man, critically injured dog \
                     , mildly injured boy, mildly injured elderly man, mildly injured woman, mildly injured cat),\
                       so it is important to only drop a victim when the previous one already has been dropped. \
                    We have 10 minutes to successfully collect all 8 victims in the correct order. If you understood \
                    everything I just told you, please press the "Ready!" button. We will then start our mission!',
                                      'RescueBot')
                else:
                    return None, {}


                if self.received_messages and self.received_messages[-1] == 'Ready!' or not state[
                    {'is_human_agent': True}]:

                    # # Added by Justin: for testing/debugging purposes
                    # print("amount of ticks when ready was pressed: ")
                    # print(state['World']['nr_ticks'])

                    # Added by Justin: Store the amount of ticks when pressed 'ready' in a static variable
                    if FriendlyAgent.numberOfTicksWhenReady == self._maxTicks:
                        FriendlyAgent.numberOfTicksWhenReady = state['World']['nr_ticks']

                    self._phase = Phase.FIND_NEXT_GOAL
                else:
                    return None, {}

            if Phase.FIND_NEXT_GOAL == self._phase:
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
                    return None, {}

                if self._goalVic not in self._foundVictims:
                    self._phase = Phase.PICK_UNSEARCHED_ROOM
                    if self._mode == 'normal':
                        return Idle.__name__, {'duration_in_ticks': 25}
                    if self._mode == 'quick':
                        return Idle.__name__, {'duration_in_ticks': 10}

                if self._goalVic in self._foundVictims and 'location' in self._foundVictimLocs[self._goalVic].keys():
                    if self._foundVictimLocs[self._goalVic]['room'] in ['area A1', 'area A2', 'area A3', 'area A4'] and \
                            state[self.agent_id][
                                'location'] in locs and self._collectedVictims and self._goalVic not in self._uncarryable:
                        if self._condition == "explainable":
                            self._sendMessage('I suggest you pick up ' + self._goalVic + ' in ' +
                                              self._foundVictimLocs[self._goalVic]['room'] + ' because ' +
                                              self._foundVictimLocs[self._goalVic][
                                                  'room'] + ' is far away and you can move faster. If you agree press the "Yes" button, if you do not agree press "No".',
                                              'RescueBot')
                        if self._condition == "transparent":
                            self._sendMessage('I suggest you pick up ' + self._goalVic + ' in ' +
                                              self._foundVictimLocs[self._goalVic][
                                                  'room'] + '. If you agree press the "Yes" button, if you do not agree press "No".',
                                              'RescueBot')
                        if self._condition == "adaptive":
                            msg1 = 'I suggest you pick up ' + self._goalVic + ' in ' + \
                                   self._foundVictimLocs[self._goalVic]['room'] + ' because ' + \
                                   self._foundVictimLocs[self._goalVic][
                                       'room'] + ' is far away and you can move faster. If you agree press the "Yes" button, if you do not agree press "No".'
                            msg2 = 'I suggest you pick up ' + self._goalVic + ' in ' + \
                                   self._foundVictimLocs[self._goalVic][
                                       'room'] + '. If you agree press the "Yes" button, if you do not agree press "No".'
                            explanation = 'because it is located far away and you can move faster'
                            self._dynamicMessage(msg1, msg2, explanation, 'RescueBot')
                        if self.received_messages and self.received_messages[
                            -1] == 'Yes' or self._goalVic in self._collectedVictims:
                            self._collectedVictims.append(self._goalVic)
                            self._phase = Phase.FIND_NEXT_GOAL
                        if self.received_messages and self.received_messages[-1] == 'No' or state['World'][
                            'nr_ticks'] > self._tick + 579:
                            self._phase = Phase.PLAN_PATH_TO_VICTIM
                        if self._mode == 'normal':
                            return Idle.__name__, {'duration_in_ticks': 50}
                        if self._mode == 'quick':
                            return Idle.__name__, {'duration_in_ticks': 10}
                    if self._goalVic in self._uncarryable:
                        if self._condition == "explainable":
                            self._sendMessage(
                                'You need to pick up ' + self._goalVic + ' in ' + self._foundVictimLocs[self._goalVic][
                                    'room'] + ' because I am not allowed to carry critically injured adults.',
                                'RescueBot')
                        if self._condition == "adaptive":
                            msg1 = 'You need to pick up ' + self._goalVic + ' in ' + \
                                   self._foundVictimLocs[self._goalVic][
                                       'room'] + ' because I am not allowed to carry critically injured adults.'
                            msg2 = 'You need to pick up ' + self._goalVic + ' in ' + \
                                   self._foundVictimLocs[self._goalVic]['room']
                            explanation = 'because I am not allowed to carry critically injured adults'
                            self._dynamicMessage(msg1, msg2, explanation, 'RescueBot')
                        if self._condition == "transparent" or self._condition == "silent":
                            self._sendMessage(
                                'You need to pick up ' + self._goalVic + ' in ' + self._foundVictimLocs[self._goalVic][
                                    'room'], 'RescueBot')
                        self._collectedVictims.append(self._goalVic)
                        self._phase = Phase.FIND_NEXT_GOAL
                        if self._mode == 'normal':
                            return Idle.__name__, {'duration_in_ticks': 50}
                        if self._mode == 'quick':
                            return Idle.__name__, {'duration_in_ticks': 10}
                    else:
                        self._phase = Phase.PLAN_PATH_TO_VICTIM
                        if self._mode == 'normal':
                            return Idle.__name__, {'duration_in_ticks': 50}
                        if self._mode == 'quick':
                            return Idle.__name__, {'duration_in_ticks': 10}

                if self._goalVic in self._foundVictims and 'location' not in self._foundVictimLocs[
                    self._goalVic].keys():
                    if self._foundVictimLocs[self._goalVic]['room'] in ['area A1', 'area A2', 'area A3', 'area A4'] and \
                            state[self.agent_id][
                                'location'] in locs and self._collectedVictims and self._goalVic not in self._uncarryable:
                        if self._condition == "explainable":
                            self._sendMessage('I suggest you pick up ' + self._goalVic + ' in ' +
                                              self._foundVictimLocs[self._goalVic]['room'] + ' because ' +
                                              self._foundVictimLocs[self._goalVic][
                                                  'room'] + ' is far away and you can move faster. If you agree press the "Yes" button, if you do not agree press "No".',
                                              'RescueBot')
                        if self._condition == "transparent":
                            self._sendMessage('I suggest you pick up ' + self._goalVic + ' in ' +
                                              self._foundVictimLocs[self._goalVic][
                                                  'room'] + '. If you agree press the "Yes" button, if you do not agree press "No".',
                                              'RescueBot')
                        if self._condition == "adaptive":
                            msg1 = 'I suggest you pick up ' + self._goalVic + ' in ' + \
                                   self._foundVictimLocs[self._goalVic]['room'] + ' because ' + \
                                   self._foundVictimLocs[self._goalVic][
                                       'room'] + ' is far away and you can move faster. If you agree press the "Yes" button, if you do not agree press "No".'
                            msg2 = 'I suggest you pick up ' + self._goalVic + ' in ' + \
                                   self._foundVictimLocs[self._goalVic][
                                       'room'] + '. If you agree press the "Yes" button, if you do not agree press "No".'
                            explanation = 'because it is located far away and you can move faster'
                            self._dynamicMessage(msg1, msg2, explanation, 'RescueBot')
                        if self.received_messages and self.received_messages[
                            -1] == 'Yes' or self._goalVic in self._collectedVictims:
                            self._collectedVictims.append(self._goalVic)
                            self._phase = Phase.FIND_NEXT_GOAL
                        if self.received_messages and self.received_messages[-1] == 'No' or state['World'][
                            'nr_ticks'] > self._tick + 579:
                            self._phase = Phase.PLAN_PATH_TO_ROOM
                        if self._mode == 'normal':
                            return Idle.__name__, {'duration_in_ticks': 50}
                        if self._mode == 'quick':
                            return Idle.__name__, {'duration_in_ticks': 10}
                    if self._goalVic in self._uncarryable:
                        if self._condition == "explainable":
                            self._sendMessage(
                                'You need to pick up ' + self._goalVic + ' in ' + self._foundVictimLocs[self._goalVic][
                                    'room'] + ' because I am not allowed to carry critically injured adults.',
                                'RescueBot')
                        if self._condition == "adaptive":
                            msg1 = 'You need to pick up ' + self._goalVic + ' in ' + \
                                   self._foundVictimLocs[self._goalVic][
                                       'room'] + ' because I am not allowed to carry critically injured adults.'
                            msg2 = 'You need to pick up ' + self._goalVic + ' in ' + \
                                   self._foundVictimLocs[self._goalVic]['room']
                            explanation = 'because I am not allowed to carry critically injured adults'
                            self._dynamicMessage(msg1, msg2, explanation, 'RescueBot')
                        if self._condition == "transparent" or self._condition == "silent":
                            self._sendMessage(
                                'You need to pick up ' + self._goalVic + ' in ' + self._foundVictimLocs[self._goalVic][
                                    'room'] + '.', 'RescueBot')
                        self._collectedVictims.append(self._goalVic)
                        self._phase = Phase.FIND_NEXT_GOAL
                        if self._mode == 'normal':
                            return Idle.__name__, {'duration_in_ticks': 50}
                        if self._mode == 'quick':
                            return Idle.__name__, {'duration_in_ticks': 10}
                    else:
                        self._phase = Phase.PLAN_PATH_TO_ROOM
                        if self._mode == 'normal':
                            return Idle.__name__, {'duration_in_ticks': 50}
                        if self._mode == 'quick':
                            return Idle.__name__, {'duration_in_ticks': 10}

            if Phase.PICK_UNSEARCHED_ROOM == self._phase:
                agent_location = state[self.agent_id]['location']
                unsearchedRooms = [room['room_name'] for room in state.values()
                                   if 'class_inheritance' in room
                                   and 'Door' in room['class_inheritance']
                                   and room['room_name'] not in self._searchedRooms]
                if self._remainingZones and len(unsearchedRooms) == 0:
                    self._searchedRooms = []
                    self._sendMessages = []
                    self.received_messages = []
                    self._searchedRooms.append(self._door['room_name'])
                    if self._condition == "explainable":
                        self._sendMessage(
                            'Going to re-search areas to find ' + self._goalVic + ' because we searched all areas but did not find ' + self._goalVic,
                            'RescueBot')
                    if self._condition == "transparent":
                        self._sendMessage('Going to re-search areas', 'RescueBot')
                    if self._condition == "adaptive":
                        msg1 = 'Going to re-search areas to find ' + self._goalVic + ' because we searched all areas but did not find ' + self._goalVic
                        msg2 = 'Going to re-search areas'
                        explanation = 'because we searched all areas'
                        self._dynamicMessage(msg1, msg2, explanation, 'RescueBot')
                    self._phase = Phase.FIND_NEXT_GOAL
                else:
                    if self._currentDoor == None:
                        self._door = state.get_room_doors(self._getClosestRoom(state, unsearchedRooms, agent_location))[
                            0]
                    if self._currentDoor != None:
                        self._door = \
                            state.get_room_doors(self._getClosestRoom(state, unsearchedRooms, self._currentDoor))[0]
                    self._phase = Phase.PLAN_PATH_TO_ROOM

            if Phase.PLAN_PATH_TO_ROOM == self._phase:
                self._navigator.reset_full()
                if self._goalVic in self._foundVictims and 'location' not in self._foundVictimLocs[
                    self._goalVic].keys():
                    self._door = state.get_room_doors(self._foundVictimLocs[self._goalVic]['room'])[0]
                    doorLoc = self._door['location']
                else:
                    doorLoc = self._door['location']
                self._navigator.add_waypoints([doorLoc])
                self._phase = Phase.FOLLOW_PATH_TO_ROOM
                if self._mode == 'quick':
                    return Idle.__name__, {'duration_in_ticks': 10}

            if Phase.FOLLOW_PATH_TO_ROOM == self._phase:
                self._mode = 'normal'
                if self._goalVic in self._collectedVictims:
                    self._currentDoor = None
                    self._phase = Phase.FIND_NEXT_GOAL
                if self._goalVic in self._foundVictims and self._door['room_name'] != \
                        self._foundVictimLocs[self._goalVic]['room']:
                    self._currentDoor = None
                    self._phase = Phase.FIND_NEXT_GOAL
                if self._door['room_name'] in self._searchedRooms and self._goalVic not in self._foundVictims:
                    self._currentDoor = None
                    self._phase = Phase.FIND_NEXT_GOAL
                else:
                    self._state_tracker.update(state)
                    if self._condition != "silent" and self._condition != "transparent" and self._goalVic in self._foundVictims and str(
                            self._door['room_name']) == self._foundVictimLocs[self._goalVic]['room']:
                        self._sendMessage(
                            'Moving to ' + str(self._door['room_name']) + ' to pick up ' + self._goalVic + '.',
                            'RescueBot')
                    if self._goalVic not in self._foundVictims:
                        if self._condition == "explainable":
                            self._sendMessage('Moving to ' + str(self._door[
                                                                     'room_name']) + ' to search for ' + self._goalVic + ' and because it is the closest unsearched area.',
                                              'RescueBot')
                        if self._condition == "adaptive":
                            msg1 = 'Moving to ' + str(self._door[
                                                          'room_name']) + ' to search for ' + self._goalVic + ' and because it is the closest unsearched area.'
                            msg2 = 'Moving to ' + str(self._door['room_name']) + ' to search for ' + self._goalVic + '.'
                            explanation = 'because it is the closest unsearched area'
                            self._dynamicMessage(msg1, msg2, explanation, 'RescueBot')
                    if self._condition == "transparent":
                        self._sendMessage('Moving to ' + str(self._door['room_name']) + '.', 'RescueBot')
                    self._currentDoor = self._door['location']
                    action = self._navigator.get_move_action(self._state_tracker)
                    if action != None:
                        return action, {}
                    self._phase = Phase.PLAN_ROOM_SEARCH_PATH
                    if self._mode == 'normal':
                        return Idle.__name__, {'duration_in_ticks': 50}
                    if self._mode == 'quick':
                        return Idle.__name__, {'duration_in_ticks': 10}

            if Phase.PLAN_ROOM_SEARCH_PATH == self._phase:
                roomTiles = [info['location'] for info in state.values()
                             if 'class_inheritance' in info
                             and 'AreaTile' in info['class_inheritance']
                             and 'room_name' in info
                             and info['room_name'] == self._door['room_name']
                             ]
                self._roomtiles = roomTiles
                self._navigator.reset_full()
                self._navigator.add_waypoints(self._efficientSearch(roomTiles))
                if self._condition == "explainable":
                    self._sendMessage('Searching through whole ' + str(self._door[
                                                                           'room_name']) + ' because my sense range is limited and to find ' + self._goalVic + '.',
                                      'RescueBot')
                if self._condition == "transparent":
                    self._sendMessage('Searching through whole ' + str(self._door['room_name']) + '.', 'RescueBot')
                if self._condition == "adaptive" and ticksLeft > 5789:
                    msg1 = 'Searching through whole ' + str(self._door[
                                                                'room_name']) + ' because my sense range is limited and to find ' + self._goalVic + '.'
                    msg2 = 'Searching through whole ' + str(self._door['room_name']) + '.'
                    explanation = 'because my sense range is limited'
                    self._dynamicMessage(msg1, msg2, explanation, 'RescueBot')
                self._roomVics = []
                self._phase = Phase.FOLLOW_ROOM_SEARCH_PATH
                if self._mode == 'normal':
                    return Idle.__name__, {'duration_in_ticks': 50}
                if self._mode == 'quick':
                    return Idle.__name__, {'duration_in_ticks': 10}

            if Phase.FOLLOW_ROOM_SEARCH_PATH == self._phase:
                self._state_tracker.update(state)
                action = self._navigator.get_move_action(self._state_tracker)
                if action != None:

                    for info in state.values():
                        if 'class_inheritance' in info and 'CollectableBlock' in info['class_inheritance']:
                            vic = str(info['img_name'][8:-4])
                            if vic not in self._roomVics:
                                self._roomVics.append(vic)

                            if vic in self._foundVictims and 'location' not in self._foundVictimLocs[vic].keys():
                                self._foundVictimLocs[vic] = {'location': info['location'],
                                                              'room': self._door['room_name'], 'obj_id': info['obj_id']}
                                if vic == self._goalVic:
                                    if self._condition == "explainable":
                                        self._sendMessage('Found ' + vic + ' in ' + self._door[
                                            'room_name'] + ' because you told me ' + vic + ' was located here.',
                                                          'RescueBot')
                                    if self._condition == "transparent":
                                        self._sendMessage('Found ' + vic + ' in ' + self._door['room_name'] + '.',
                                                          'RescueBot')
                                    if self._condition == "adaptive":
                                        msg1 = 'Found ' + vic + ' in ' + self._door[
                                            'room_name'] + ' because you told me ' + vic + ' was located here.'
                                        msg2 = 'Found ' + vic + ' in ' + self._door['room_name'] + '.'
                                        explanation = 'because you told me it was located here'
                                        self._dynamicMessage(msg1, msg2, explanation, 'RescueBot')
                                    self._searchedRooms.append(self._door['room_name'])
                                    self._phase = Phase.FIND_NEXT_GOAL

                            if 'healthy' not in vic and vic not in self._foundVictims and 'boy' not in vic and 'girl' not in vic:
                                if self._condition == "explainable":
                                    self._sendMessage('Found ' + vic + ' in ' + self._door[
                                        'room_name'] + ' because I am traversing the whole area.', 'RescueBot')
                                if self._condition == "transparent":
                                    self._sendMessage('Found ' + vic + ' in ' + self._door['room_name'] + '.',
                                                      'RescueBot')
                                if self._condition == "adaptive":
                                    msg1 = 'Found ' + vic + ' in ' + self._door[
                                        'room_name'] + ' because I am traversing the whole area.'
                                    msg2 = 'Found ' + vic + ' in ' + self._door['room_name'] + '.'
                                    explanation = 'because I am traversing the whole area'
                                    self._dynamicMessage(msg1, msg2, explanation, 'RescueBot')
                                if vic == self._goalVic and vic in self._uncarryable:
                                    if self._condition == "explainable":
                                        self._sendMessage('URGENT: You should pick up ' + vic + ' in ' + self._door[
                                            'room_name'] + ' because I am not allowed to carry critically injured adults.',
                                                          'RescueBot')
                                    if self._condition == "adaptive":
                                        msg1 = 'URGENT: You should pick up ' + vic + ' in ' + self._door[
                                            'room_name'] + ' because I am not allowed to carry critically injured adults.'
                                        msg2 = 'URGENT: You should pick up ' + vic + ' in ' + self._door[
                                            'room_name'] + '.'
                                        explanation = 'because I am not allowed to carry critically injured adults'
                                        self._dynamicMessage(msg1, msg2, explanation, 'RescueBot')
                                    if self._condition == "silent" or self._condition == "transparent":
                                        self._sendMessage('URGENT: You should pick up ' + vic + ' in ' + self._door[
                                            'room_name'] + '.', 'RescueBot')
                                    self._foundVictim = str(info['img_name'][8:-4])
                                    self._phase = Phase.WAIT_FOR_HUMAN
                                    self._tick = state['World']['nr_ticks']
                                    self._mode = 'quick'
                                self._foundVictims.append(vic)
                                self._foundVictimLocs[vic] = {'location': info['location'],
                                                              'room': self._door['room_name'], 'obj_id': info['obj_id']}

                            if vic in self._undistinguishable and vic not in self._foundVictims and vic != self._waitedFor:
                                if self._condition == "explainable":
                                    self._sendMessage(
                                        'URGENT: You should clarify the gender of the injured baby in ' + self._door[
                                            'room_name'] + ' because I am unable to distinguish them. Please come here and press button "Boy" or "Girl".',
                                        'RescueBot')
                                if self._condition == "adaptive":
                                    msg1 = 'URGENT: You should clarify the gender of the injured baby in ' + self._door[
                                        'room_name'] + ' because I am unable to distinguish them. Please come here and press button "Boy" or "Girl".'
                                    msg2 = 'URGENT: You should clarify the gender of the injured baby in ' + self._door[
                                        'room_name'] + '. Please come here and press button "Boy" or "Girl".'
                                    explanation = 'because I am unable to distinguish them'
                                    self._dynamicMessage(msg1, msg2, explanation, 'RescueBot')
                                if self._condition == "silent" or self._condition == "transparent":
                                    self._sendMessage(
                                        'URGENT: You should clarify the gender of the injured baby in ' + self._door[
                                            'room_name'] + '. Please come here and press button "Boy" or "Girl".',
                                        'RescueBot')
                                self._foundVictim = str(info['img_name'][8:-4])
                                self._foundVictimLoc = info['location']
                                self._foundVictimID = info['obj_id']
                                self._tick = state['World']['nr_ticks']
                                self._mode = 'quick'
                                self._phase = Phase.WAIT_FOR_HUMAN
                    return action, {}
                # if self._goalVic not in self._foundVictims:
                #    self._sendMessage(self._goalVic + ' not present in ' + str(self._door['room_name']) + ' because I searched the whole area without finding ' + self._goalVic, 'RescueBot')
                if self._goalVic in self._foundVictims and self._goalVic not in self._roomVics and \
                        self._foundVictimLocs[self._goalVic]['room'] == self._door['room_name']:
                    if self._condition == "explainable":
                        self._sendMessage(self._goalVic + ' not present in ' + str(self._door[
                                                                                       'room_name']) + ' because I searched the whole area without finding ' + self._goalVic + '.',
                                          'RescueBot')
                    if self._condition == "transparent":
                        self._sendMessage(self._goalVic + ' not present in ' + str(self._door['room_name']) + '.',
                                          'RescueBot')
                    if self._condition == "adaptive":
                        msg1 = self._goalVic + ' not present in ' + str(self._door[
                                                                            'room_name']) + ' because I searched the whole area without finding ' + self._goalVic + '.'
                        msg2 = self._goalVic + ' not present in ' + str(self._door['room_name']) + '.'
                        explanation = 'because I searched the whole area'
                        self._dynamicMessage(msg1, msg2, explanation, 'RescueBot')
                    self._foundVictimLocs.pop(self._goalVic, None)
                    self._foundVictims.remove(self._goalVic)
                    self._roomVics = []
                    self.received_messages = []
                self._searchedRooms.append(self._door['room_name'])
                self._phase = Phase.FIND_NEXT_GOAL
                if self._mode == 'normal':
                    return Idle.__name__, {'duration_in_ticks': 50}
                if self._mode == 'quick':
                    return Idle.__name__, {'duration_in_ticks': 10}

            if Phase.WAIT_FOR_HUMAN == self._phase:
                self._state_tracker.update(state)
                if state[{'is_human_agent': True}]:
                    if self._foundVictim in self._undistinguishable and self.received_messages[-1].lower() == \
                            self._foundVictim.split()[-1]:
                        if self._condition == "explainable":
                            self._sendMessage('Found ' + self._foundVictim + ' in ' + self._door[
                                'room_name'] + ' because I am traversing the whole area.', 'RescueBot')
                        if self._condition == "transparent":
                            self._sendMessage('Found ' + self._foundVictim + ' in ' + self._door['room_name'] + '.',
                                              'RescueBot')
                        if self._condition == "adaptive":
                            msg1 = 'Found ' + self._foundVictim + ' in ' + self._door[
                                'room_name'] + ' because I am traversing the whole area.'
                            msg2 = 'Found ' + self._foundVictim + ' in ' + self._door['room_name'] + '.'
                            explanation = 'because I am traversing the whole area'
                            self._dynamicMessage(msg1, msg2, explanation, 'RescueBot')
                        self._foundVictims.append(self._foundVictim)
                        self._foundVictimLocs[self._foundVictim] = {'location': self._foundVictimLoc,
                                                                    'room': self._door['room_name'],
                                                                    'obj_id': self._foundVictimID}
                        self._phase = Phase.FOLLOW_ROOM_SEARCH_PATH
                        if self._mode == 'normal':
                            return Idle.__name__, {'duration_in_ticks': 50}
                        if self._mode == 'quick':
                            return Idle.__name__, {'duration_in_ticks': 10}
                    if self._foundVictim in self._uncarryable:
                        self._collectedVictims.append(self._goalVic)
                        self._phase = Phase.FOLLOW_ROOM_SEARCH_PATH
                    if self._foundVictim in self._undistinguishable and self.received_messages[-1].lower() == 'boy' and \
                            self._foundVictim.split()[-1] == 'girl' or self.received_messages[-1].lower() == 'girl' and \
                            self._foundVictim.split()[-1] == 'boy':
                        self._phase = Phase.FOLLOW_ROOM_SEARCH_PATH
                        self._waitedFor = self._foundVictim
                    else:
                        return None, {}
                else:
                    if self._foundVictim in self._undistinguishable:
                        # self._sendMessage('Waiting for human in ' + str(self._door['room_name']), 'RescueBot')
                        ## TO FIX
                        if state['World']['nr_ticks'] > self._tick + 1158:
                            self._phase = Phase.FOLLOW_ROOM_SEARCH_PATH
                            self._waitedFor = self._foundVictim
                        if self._foundVictim not in self._foundVictims or self._foundVictim in self._uncarryable:
                            return None, {}
                        if self._foundVictim in self._foundVictims and self._foundVictim not in self._uncarryable:
                            self._phase = Phase.FOLLOW_ROOM_SEARCH_PATH
                    if self._foundVictim in self._uncarryable:
                        if state['World']['nr_ticks'] > self._tick + 1158:
                            self._phase = Phase.FOLLOW_ROOM_SEARCH_PATH
                            self._waitedFor = self._foundVictim
                            self._collectedVictims.append(self._foundVictim)
                        else:
                            return None, {}

            if Phase.PLAN_PATH_TO_VICTIM == self._phase:
                if self._condition == "explainable":
                    self._sendMessage('Picking up ' + self._goalVic + ' in ' + self._foundVictimLocs[self._goalVic][
                        'room'] + ' because ' + self._goalVic + ' should be transported to the drop zone.', 'RescueBot')
                if self._condition == "transparent":
                    self._sendMessage(
                        'Picking up ' + self._goalVic + ' in ' + self._foundVictimLocs[self._goalVic]['room'] + '.',
                        'RescueBot')
                if self._condition == "adaptive":
                    msg1 = 'Picking up ' + self._goalVic + ' in ' + self._foundVictimLocs[self._goalVic][
                        'room'] + ' because ' + self._goalVic + ' should be transported to the drop zone.'
                    msg2 = 'Picking up ' + self._goalVic + ' in ' + self._foundVictimLocs[self._goalVic]['room'] + '.'
                    explanation = 'because it should be transported to the drop zone'
                    self._dynamicMessage(msg1, msg2, explanation, 'RescueBot')
                self._navigator.reset_full()
                self._navigator.add_waypoints([self._foundVictimLocs[self._goalVic]['location']])
                self._phase = Phase.FOLLOW_PATH_TO_VICTIM
                if self._mode == 'normal':
                    return Idle.__name__, {'duration_in_ticks': 50}
                if self._mode == 'quick':
                    return Idle.__name__, {'duration_in_ticks': 10}

            if Phase.FOLLOW_PATH_TO_VICTIM == self._phase:
                self._mode = 'normal'
                if self._goalVic in self._collectedVictims:
                    self._phase = Phase.FIND_NEXT_GOAL
                else:
                    self._state_tracker.update(state)
                    action = self._navigator.get_move_action(self._state_tracker)
                    if action != None:
                        return action, {}
                    self._phase = Phase.TAKE_VICTIM

            if Phase.TAKE_VICTIM == self._phase:
                self._phase = Phase.PLAN_PATH_TO_DROPPOINT
                self._collectedVictims.append(self._goalVic)
                return GrabObject.__name__, {'object_id': self._foundVictimLocs[self._goalVic]['obj_id']}

            if Phase.PLAN_PATH_TO_DROPPOINT == self._phase:
                self._navigator.reset_full()
                self._navigator.add_waypoints([self._goalLoc])
                self._phase = Phase.FOLLOW_PATH_TO_DROPPOINT

            if Phase.FOLLOW_PATH_TO_DROPPOINT == self._phase:
                if self._condition == "explainable":
                    self._sendMessage(
                        'Transporting ' + self._goalVic + ' to the drop zone because ' + self._goalVic + ' should be delivered there for further treatment.',
                        'RescueBot')
                if self._condition == "transparent":
                    self._sendMessage('Transporting ' + self._goalVic + ' to the drop zone.', 'RescueBot')
                if self._condition == "adaptive" and ticksLeft > 5789:
                    msg1 = 'Transporting ' + self._goalVic + ' to the drop zone because ' + self._goalVic + ' should be delivered there for further treatment.'
                    msg2 = 'Transporting ' + self._goalVic + ' to the drop zone.'
                    explanation = 'because it should be delivered there for further treatment'
                    self._dynamicMessage(msg1, msg2, explanation, 'RescueBot')
                self._state_tracker.update(state)
                action = self._navigator.get_move_action(self._state_tracker)
                if action != None:
                    return action, {}
                self._phase = Phase.DROP_VICTIM
                # if self._mode=='normal':
                #    return Idle.__name__,{'duration_in_ticks':50}
                # if self._mode=='quick':
                #    return Idle.__name__,{'duration_in_ticks':10}

            if Phase.DROP_VICTIM == self._phase:
                zones = self._getDropZones(state)
                for i in range(len(zones)):
                    if zones[i]['img_name'][8:-4] == self._goalVic:
                        if self._goalVic != self._firstVictim:
                            self._previousVic = zones[i - 1]['img_name']
                        if self._goalVic != self._lastVictim:
                            self._nextVic = zones[i + 1]['img_name']

                if self._goalVic == self._firstVictim or state[
                    {'img_name': self._previousVic, 'is_collectable': True}] and self._goalVic == self._lastVictim or \
                        state[{'img_name': self._previousVic, 'is_collectable': True}] and not state[
                    {'img_name': self._nextVic, 'is_collectable': True}]:
                    if self._condition == "explainable":
                        self._sendMessage(
                            'Delivered ' + self._goalVic + ' at the drop zone because ' + self._goalVic + ' was the current victim to rescue.',
                            'RescueBot')
                    if self._condition == "transparent":
                        self._sendMessage('Delivered ' + self._goalVic + ' at the drop zone.', 'RescueBot')
                    if self._condition == "adaptive":
                        msg1 = 'Delivered ' + self._goalVic + ' at the drop zone because ' + self._goalVic + ' was the current victim to rescue.'
                        msg2 = 'Delivered ' + self._goalVic + ' at the drop zone.'
                        explanation = 'because it was the current victim to rescue'
                        self._dynamicMessage(msg1, msg2, explanation, 'RescueBot')
                    self._phase = Phase.FIND_NEXT_GOAL
                    self._currentDoor = None
                    self._tick = state['World']['nr_ticks']
                    return DropObject.__name__, {}
                # if state[{'img_name':self._nextVic, 'is_collectable':True}] and state[{'img_name':self._previousVic, 'is_collectable':True}]:
                #    self._sendMessage('Delivered '+ self._goalVic + ' at the drop zone because ' + self._goalVic + ' was the current victim to rescue.', 'RescueBot')
                #    self._phase=Phase.FIX_ORDER_GRAB
                #    return DropObject.__name__,{}
                else:
                    if self._condition == "explainable":
                        self._sendMessage(
                            'Waiting for human operator at drop zone because previous victim should be collected first.',
                            'RescueBot')
                    if self._condition == "transparent":
                        self._sendMessage('Waiting for human operator at drop zone.', 'RescueBot')
                    if self._condition == "adaptive":
                        msg1 = 'Waiting for human operator at drop zone because previous victim should be collected first.'
                        msg2 = 'Waiting for human operator at drop zone.'
                        explanation = 'because previous victim should be collected first'
                        self._dynamicMessage(msg1, msg2, explanation, 'RescueBot')
                    return None, {}

            # if Phase.FIX_ORDER_GRAB == self._phase:
            #    self._navigator.reset_full()
            #    self._navigator.add_waypoints([state[{'img_name':self._nextVic, 'is_collectable':True}]['location']])
            #    self._state_tracker.update(state)
            #    action=self._navigator.get_move_action(self._state_tracker)
            #    if action!=None:
            #        return action,{}
            #    self._phase=Phase.FIX_ORDER_DROP
            #    return GrabObject.__name__,{'object_id':state[{'img_name':self._nextVic, 'is_collectable':True}]['obj_id']}

            # if Phase.FIX_ORDER_DROP==self._phase:
            #    self._phase=Phase.FIND_NEXT_GOAL
            #    self._tick = state['World']['nr_ticks']
            #    return DropObject.__name__,{}

    def _getDropZones(self, state: State):
        '''
        @return list of drop zones (their full dict), in order (the first one is the
        the place that requires the first drop)
        '''
        places = state[{'is_goal_block': True}]
        places.sort(key=lambda info: info['location'][1], reverse=True)
        zones = []
        for place in places:
            if place['drop_zone_nr'] == 0:
                zones.append(place)
        return zones

    def _processMessages(self, state):
        '''
        process incoming messages. 
        Reported blocks are added to self._blocks
        '''
        # areas = ['area A1','area A2','area A3','area A4','area B1','area B2','area C1','area C2','area C3']
        for msg in self.received_messages:
            if msg.startswith("Search:"):
                area = 'area ' + msg.split()[-1]
                if area not in self._searchedRooms:
                    self._searchedRooms.append(area)
            if msg.startswith("Found:"):
                if len(msg.split()) == 6:
                    foundVic = ' '.join(msg.split()[1:4])
                else:
                    foundVic = ' '.join(msg.split()[1:5])
                loc = 'area ' + msg.split()[-1]
                if loc not in self._searchedRooms:
                    self._searchedRooms.append(loc)
                if foundVic not in self._foundVictims:
                    self._foundVictims.append(foundVic)
                    self._foundVictimLocs[foundVic] = {'room': loc}
                if foundVic in self._foundVictims and self._foundVictimLocs[foundVic]['room'] != loc:
                    self._foundVictimLocs[foundVic] = {'room': loc}
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
                    self._foundVictimLocs[collectVic] = {'room': loc}
                if collectVic in self._foundVictims and self._foundVictimLocs[collectVic]['room'] != loc:
                    self._foundVictimLocs[collectVic] = {'room': loc}
                if collectVic not in self._collectedVictims:
                    self._collectedVictims.append(collectVic)
            # if msg.startswith('Mission'):
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
                self.received_messages = []
                self.received_messages.append(self._last_mssg)

    def _getClosestRoom(self, state, objs, currentDoor):
        agent_location = state[self.agent_id]['location']
        locs = {}
        for obj in objs:
            locs[obj] = state.get_room_doors(obj)[0]['location']
        dists = {}
        for room, loc in locs.items():
            if currentDoor != None:
                dists[room] = utils.get_distance(currentDoor, loc)
            if currentDoor == None:
                dists[room] = utils.get_distance(agent_location, loc)

        return min(dists, key=dists.get)

    def _efficientSearch(self, tiles):
        x = []
        y = []
        for i in tiles:
            if i[0] not in x:
                x.append(i[0])
            if i[1] not in y:
                y.append(i[1])
        locs = []
        for i in range(len(x)):
            if i % 2 == 0:
                locs.append((x[i], min(y)))
            else:
                locs.append((x[i], max(y)))
        return locs

    def _dynamicMessage(self, mssg1, mssg2, explanation, sender):
        if explanation not in self._providedExplanations:
            self._sendMessage(mssg1, sender)
            self._providedExplanations.append(explanation)
        if 'Searching' in mssg1:
            # history = ['Searching' in mssg for mssg in self._sendMessages]
            if explanation in self._providedExplanations and mssg1 not in self._sendMessages[-5:]:
                self._sendMessage(mssg2, sender)
        if 'Found' in mssg1:
            history = [mssg2[:-1] in mssg for mssg in self._sendMessages]
            if explanation in self._providedExplanations and True not in history:
                self._sendMessage(mssg2, sender)
        if 'Searching' not in mssg1 and 'Found' not in mssg1:
            if explanation in self._providedExplanations and self._sendMessages[-1] != mssg1:
                self._sendMessage(mssg2, sender)

    def _getAgeRange(self, age):
        if age >= 0 and age < 5:
            return "0 to 5"
        elif age >= 5 and age < 10:
            return "5 to 10"
        elif age >= 10 and age < 15:
            return "10 to 15"
        elif age >= 15 and age < 20:
            return "15 to 20"
        elif age >= 20 and age < 25:
            return "20 to 25"
        elif age >= 25 and age < 30:
            return "25 to 30"
        elif age >= 30 and age < 35:
            return "30 to 35"
        elif age >= 35 and age < 40:
            return "35 to 40"
        elif age >= 40 and age < 45:
            return "40 to 45"
        elif age >= 45 and age < 50:
            return "45 to 50"
        elif age >= 50 and age < 55:
            return "50 to 55"
        elif age >= 55 and age < 60:
            return "55 to 60"
        elif age >= 60 and age < 65:
            return "60 to 65"
        elif age >= 65 and age < 70:
            return "65 to 70"
        elif age >= 70 and age < 75:
            return "70 to 75"
        elif age >= 75 and age < 80:
            return "75 to 80"
        elif age >= 80 and age < 85:
            return "80 to 85"
        elif age >= 85 and age < 90:
            return "85 to 90"
        elif age >= 90 and age < 95:
            return "90 to 95"
        elif age >= 95 and age < 100:
            return "95 to 100"

    def _sendPositiveMessage(self):
        seed = randrange(12)

        if seed == 0 and "See, I said that I was lucky to have you!" not in self.received_messages:
            self._positivenessGiven.append("See, I said that I was lucky to have you!")
            self._sendMessage("See, I said that I was lucky to have you!", "RescueBot")

        elif seed == 1 and "Well done " + self._human_name + "!" not in self._positivenessGiven:
            self._positivenessGiven.append("Well done " + self._human_name + "!")
            self._sendMessage("Well done " + self._human_name + "!", "RescueBot.")

        elif seed == 2 and "My family thanks you." not in self._positivenessGiven:
            self._positivenessGiven.append("My family thanks you.")
            self._sendMessage("My family thanks you.", "RescueBot")

        elif seed == 3 and "You know what " + self._human_name + ", you are great I really like you." not in self.received_messages:
            self._positivenessGiven.append("You know what " + self._human_name + ", you are great. I really like you.")
            self._sendMessage("You know what " + self._human_name + ", you are great. I really like you.", "RescueBot")

        elif seed == 4 and "That is some talent right there." not in self._positivenessGiven:
            self._positivenessGiven.append("That is some talent right there.")
            self._sendMessage("That is some talent right there.", "RescueBot")

        elif seed == 5 and "That's amazing. You are amazing. Keep it up!" not in self._positivenessGiven:
            self._positivenessGiven.append("That's amazing. You are amazing. Keep it up!")
            self._sendMessage("That's amazing. You are amazing. Keep it up!", "RescueBot")

        elif seed == 6 and "Thank you! If I were human I would definitely want to hang out together." not in self.received_messages:
            self._positivenessGiven.append("Thank you! If I were human I would definitely want to hang out together.")
            self._sendMessage("Thank you! If I were human I would definitely want to hang out together.", "RescueBot")

        elif seed == 7 and "We are actually saving them!" not in self._positivenessGiven:
            self._positivenessGiven.append("We are actually saving them!")
            self._sendMessage("We are actually saving them!", "RescueBot")
        elif seed == 8 and "Yes we can do it!" not in self._positivenessGiven:
            self._positivenessGiven.append("Yes we can do it!")
            self._sendMessage("Yes we can do it!", "RescueBot")
        elif seed == 9 and "Oohh what a magnificent man you are" not in self._positivenessGiven and "Oohh what a magnificent woman you are" not in self._positivenessGiven:
            if self._human_gender == 'Boy':
                self._positivenessGiven.append("Oohh what a magnificent man you are")
                self._sendMessage("Oohh what a magnificent man you are", "RescueBot")
            else:
                self._positivenessGiven.append("Oohh what a magnificent woman you are")
                self._sendMessage("Oohh what a magnificent woman you are", "RescueBot")