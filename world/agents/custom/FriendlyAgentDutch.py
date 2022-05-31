import enum
from random import randrange

from matrx import utils
from matrx.actions.object_actions import GrabObject, DropObject
from matrx.agents.agent_utils.navigator import Navigator
from matrx.agents.agent_utils.state import State
from matrx.agents.agent_utils.state_tracker import StateTracker
from matrx.messages.message import Message

from world.actions.customActions import *
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


class FriendlyAgentDutch(BW4TBrain):
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
        FriendlyAgentDutch.numberOfTicksWhenReady = self._maxTicks
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

    def decide_on_bw4t_action(self, state:State):
        ticksLeft = self._maxTicks - state['World']['nr_ticks']

        if ticksLeft <= 5789 and ticksLeft > 4631 and 'U heeft nog  5 minuten om de taak te voltooien.' not in self._sendMessages:
            self._sendMessage('U heeft nog  5 minuten om de taak te voltooien.', 'RescueBot')
        if ticksLeft <= 4631 and ticksLeft > 3473 and 'U heeft nog  4 minuten om de taak te voltooien.' not in self._sendMessages:
            self._sendMessage('U heeft nog  4 minuten om de taak te voltooien.', 'RescueBot')
        if ticksLeft <= 3473 and ticksLeft > 2315 and 'U heeft nog  3 minuten om de taak te voltooien.' not in self._sendMessages:
            self._sendMessage('U heeft nog  3 minuten om de taak te voltooien.', 'RescueBot')
        if ticksLeft <= 2315 and ticksLeft > 1158 and 'U heeft nog  2 minuten om de taak te voltooien.' not in self._sendMessages:
            self._sendMessage('U heeft nog  2 minuten om de taak te voltooien.', 'RescueBot')
        if ticksLeft <= 1158 and 'U heeft nog  1 minuut om de taak te voltooien.' not in self._sendMessages:
            self._sendMessage('U heeft nog  1 minuut om de taak te voltooien.', 'RescueBot')

        while True:
            self._ticksForMessages += 1
            if self.received_messages:
                if 'Collect' in self.received_messages[-1][0:7]:
                    self._sendPositiveMessage()

            if Phase.INTRODUCTION == self._phase:
                self._sendMessage('Hoi! Ik ben zo blij dat u er bent! \
                Mijn naam is RescueBot, maar u mag mij Res noemen. Gisteren kwamen mijn familie en ik hier aan \
                op vakantie. In ons dagelijks leven helpen we onze mensen om hun leven makkelijker te \
                 maken. We laten ze tv-series zien, spelen spelletjes met ze, helpen ze met huiswerk, noem maar op! Het werk \
                geeft veel voldoening maar kost ook veel energie. Daarom waren we zo blij om er even op uit te gaan \
                met zijn allen.', 'RescueBot')

                if not self._introBool1:
                    self._currentWaitingPoint = self._ticksForMessages + self._messageWaitingTime
                    self._introBool1 = True

                if self._ticksForMessages > self._currentWaitingPoint:
                    self._sendMessage('Maar vanmorgen was ik onze tent aan het opzetten, toen opeens mijn zus belde. \
                    Ze klonk uitgeput en doodsbang. Ze vertelde dat zij en de baby ziek waren geworden en niet meer \
                    konden bewegen. Een paar minuten later ging het alarm af op de camping. Blijkbaar is het \
                    hele gebied getroffen door een computer virus. Gelukkig is niet iedereen daar vatbaar voor. \
                    U en ik zijn immuun. Wij zullen iedereen die besmet is moeten redden.', 'RescueBot')
                else:
                    return None, {}

                if not self._introBool2:
                    self._currentWaitingPoint = self._ticksForMessages + self._messageWaitingTime
                    self._introBool2 = True

                if self._ticksForMessages > self._currentWaitingPoint:

                    self._sendMessage('Maar voordat we aan de slag gaan, zou ik u graag leren kennen! Ik heb een paar \
                     vragen voor u. Wat is uw naam? U kunt het intypen en op enter \
                     drukken', 'RescueBot')
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

                    self._sendMessage("Ahaa hallo " + self._human_name + "! Fijn dat u even langs bent gekomen. \
                     Bent u een man of een vrouw? Ik kan dat nooit echt aan de naam zien haha. U kunt op het knopje \
                     'Jongen' of 'Meisje' drukken.", 'RescueBot')
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
                        self._sendMessage('Oké, dag meneer! Hoe oud bent u? U kunt een getal intypen \
                          en op enter drukken.', 'RescueBot')
                    else:
                        self._sendMessage('Oké, dag mevrouw! Hoe oud bent u? U kunt een getal intypen \
                        en op enter drukken', 'RescueBot')
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
                    self._sendMessage("Oh wauw, u moet zoveel levenservaring hebben. Zelf wordt ik twee jaar oud op \
                    18 December. Waar komt u vandaan? U kunt de naam van het land intypen en op enter \
                    drukken.", 'RescueBot')
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

                        self._sendMessage("Nee joh dat meent u niet! U doet me zoveel aan mijn persoonlijke mens \
                         denken. Zijn naam is Paul. Hij is "
                                          + str(self._human_age + 2) + " en woont ook in " +
                                          self._human_birthPlace + ". Ik wordt er altijd heel blij van om hem in \
                                           het leven te ondersteunen.", 'RescueBot')
                    else:
                        self._sendMessage("Nee joh dat meent u niet! U doet me zoveel aan mijn persoonlijke mens \
                         denken. Haar naam is Sophia. Ze is "
                                          + str(self._human_age + 2) + " en woont ook in " +
                                          self._human_birthPlace + ". Ik wordt er altijd heel blij van om haar in \
                                           het leven te ondersteunen.", 'RescueBot')
                else:
                    return None, {}

                if not self._introBool3:
                    self._currentWaitingPoint = self._ticksForMessages + self._messageWaitingTime
                    self._introBool3 = True

                if self._ticksForMessages > self._currentWaitingPoint:
                    self._sendMessage("Oke, terug naar het probleem dat we hier hebben.\
                     Ik moet mijn familie redden, maar kan het niet alleen. Wilt u mij helpen?\
                      U op het knopje 'Ja' of 'Nee' klikken.", 'RescueBot')
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
                        self._sendMessage("Ohh dat is zo jammer. Maar geen probleem, ik zal proberen om ze zelf te \
                         redden. Bedankt voor het langskomen!", 'RescueBot')
                        continue
                else:
                    return None, {}

                if self._ticksForMessages > self._currentWaitingPoint:
                    self._sendMessage("Oke! Ik zou graag benadrukken dat u mijn familie in principe helemaal in uw eentje \
                                      zou kunnen redden. U kunt ook liegen, lui zijn, of eigenlijk gewoon maar \
                                      doen wat u wilt. Maar onthoud dat ons doel is om mijn familie zo snel mogelijk \
                                      te redden en met zo min mogelijk stappen. Aangezien we met elkaar kunnen praten, \
                                      gaat samenwerking ons echt helpen om beter te presteren.", 'RescueBot')
                else:
                    return None, {}

                if not self._introBool4:
                    self._currentWaitingPoint = self._ticksForMessages + self._messageWaitingTime
                    self._introBool4 = True

                if self._ticksForMessages > self._currentWaitingPoint:
                    self.confidenceString = "Trouwens, ik heb net wat berekeningen gedaan. Het blijkt dat "

                    if self._human_gender == 'Boy':
                        self.confidenceString += "<b><i>mannen</i></b> "
                    else:
                        self.confidenceString += "<b><i>vrouwen</i></b> "

                    self.confidenceString += "uit <b><i>" + self._human_birthPlace + "</i></b> met een leeftijd tussen <b><i>" \
                                             + self._getAgeRange(self._human_age) + "</i></b> gemiddeld " \
                                             + "<b><i>78% beter</i></b> presteren op reddingsacties. \
                                                Ik heb geluk met u! "

                    self._sendMessage(self.confidenceString, 'RescueBot')
                else:
                    return None, {}

                if not self._introBool5:
                    self._currentWaitingPoint = self._ticksForMessages + self._messageWaitingTime
                    self._introBool5 = True

                if self._ticksForMessages > self._currentWaitingPoint:

                    self._sendMessage('Oke, laten we beginnen. Wij zullen straks samen proberen om de volgende \
                    8 slachtoffers zo snel mogelijk te vinden en te redden. We moeten de slachtoffers redden in volgorde \
                    van links naar rechts (critically injured girl, critically injured elderly woman, \
                    critically injured man, critically injured dog, mildly injured boy, mildly injured elderly man, \
                    mildly injured woman, mildly injured cat). Dus het is belangrijk om een slachtoffer pas af \
                    te leveren wanneer de vorige eerst afgeleverd is. We hebben 10 minuten om alle 8 slachtoffers \
                    in de juiste volgorde te verzamelen. Als je alles hebt begrepen, dan kun je op het "Ready!" \
                    knopje drukken en dan starten we onze missie!', 'RescueBot')
                else:
                    return None, {}

                if self.received_messages and self.received_messages[-1] == 'Ready!' or not state[
                    {'is_human_agent': True}]:

                    # # Added by Justin: for testing/debugging purposes
                    # print("amount of ticks when ready was pressed: ")
                    # print(state['World']['nr_ticks'])

                    # Added by Justin: Store the amount of ticks when pressed 'ready' in a static variable
                    if FriendlyAgentDutch.numberOfTicksWhenReady == self._maxTicks:
                        FriendlyAgentDutch.numberOfTicksWhenReady = state['World']['nr_ticks']

                    self._phase = Phase.FIND_NEXT_GOAL
                else:
                    return None, {}

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
                    if self._mode=='normal':
                        return Idle.__name__,{'duration_in_ticks':25}
                    if self._mode=='quick':
                        return Idle.__name__,{'duration_in_ticks':10}

                if self._goalVic in self._foundVictims and 'location' in self._foundVictimLocs[self._goalVic].keys():
                    if self._foundVictimLocs[self._goalVic]['room'] in ['area A1', 'area A2', 'area A3', 'area A4'] and state[self.agent_id]['location'] in locs and self._collectedVictims and self._goalVic not in self._uncarryable:
                        if self._condition=="explainable":
                            self._sendMessage('Ik stel voor dat u ' + self._goalVic + ' oppakt in ' + self._foundVictimLocs[self._goalVic]['room'] + ' omdat ' + self._foundVictimLocs[self._goalVic]['room'] + ' ver weg is en u sneller kunt lopen. Als u het ermee eens bent, druk dan het "Yes" knopje. Zo niet, druk dan op "No"', 'RescueBot')
                        if self._condition=="transparent":
                            self._sendMessage('Ik stel voor dat u ' + self._goalVic + ' oppakt in ' + self._foundVictimLocs[self._goalVic]['room'] + '. Als u het ermee eens bent, druk dan het "Yes" knopje. Zo niet, druk dan op "No".', 'RescueBot')
                        if self._condition=="adaptive":
                            msg1 = 'Ik stel voor dat u ' + self._goalVic + ' oppakt in ' + self._foundVictimLocs[self._goalVic]['room'] + ' omdat ' + self._foundVictimLocs[self._goalVic]['room'] + ' ver weg is en u sneller kunt lopen. Als u het ermee eens bent, druk dan het "Yes" knopje. Zo niet, druk dan op "No"'
                            msg2 = 'Ik stel voor dat u ' + self._goalVic + ' oppakt in ' + self._foundVictimLocs[self._goalVic]['room'] + '. Als u het ermee eens bent, druk dan het "Yes" knopje. Zo niet, druk dan op "No".'
                            explanation = 'omdat het ver weg is en u sneller kunt lopen'
                            self._dynamicMessage(msg1,msg2,explanation,'RescueBot')
                        if self.received_messages and self.received_messages[-1]=='Yes' or self._goalVic in self._collectedVictims:
                            self._collectedVictims.append(self._goalVic)
                            self._phase=Phase.FIND_NEXT_GOAL
                        if self.received_messages and self.received_messages[-1]=='No' or state['World']['nr_ticks'] > self._tick + 579:
                            self._phase=Phase.PLAN_PATH_TO_VICTIM
                        if self._mode=='normal':
                            return Idle.__name__,{'duration_in_ticks':50}
                        if self._mode=='quick':
                            return Idle.__name__,{'duration_in_ticks':10}
                    if self._goalVic in self._uncarryable:
                        if self._condition=="explainable":
                            self._sendMessage('U zal ' + self._goalVic + ' moeten oppakken in ' + self._foundVictimLocs[self._goalVic]['room'] + ' want ik mag geen kritiek gewonde volwassenen tillen.', 'RescueBot')
                        if self._condition=="adaptive":
                            msg1 = 'U zal ' + self._goalVic + ' moeten oppakken in ' + self._foundVictimLocs[self._goalVic]['room'] + ' want ik mag geen kritiek gewonde volwassenen tillen.'
                            msg2 = 'U zal ' + self._goalVic + ' moeten oppakken in ' + self._foundVictimLocs[self._goalVic]['room']
                            explanation = 'want ik mag geen kritiek gewonde volwassenen tillen.'
                            self._dynamicMessage(msg1,msg2,explanation,'RescueBot')
                        if self._condition=="transparent" or self._condition=="silent":
                            self._sendMessage('U zal ' + self._goalVic + ' moeten oppaken in ' + self._foundVictimLocs[self._goalVic]['room'], 'RescueBot')
                        self._collectedVictims.append(self._goalVic)
                        self._phase=Phase.FIND_NEXT_GOAL
                        if self._mode=='normal':
                            return Idle.__name__,{'duration_in_ticks':50}
                        if self._mode=='quick':
                            return Idle.__name__,{'duration_in_ticks':10}
                    else:
                        self._phase=Phase.PLAN_PATH_TO_VICTIM
                        if self._mode=='normal':
                            return Idle.__name__,{'duration_in_ticks':50}
                        if self._mode=='quick':
                            return Idle.__name__,{'duration_in_ticks':10}

                if self._goalVic in self._foundVictims and 'location' not in self._foundVictimLocs[self._goalVic].keys():
                    if self._foundVictimLocs[self._goalVic]['room'] in ['area A1', 'area A2', 'area A3', 'area A4'] and state[self.agent_id]['location'] in locs and self._collectedVictims and self._goalVic not in self._uncarryable:
                        if self._condition=="explainable":
                            self._sendMessage('Ik stel voor dat u ' + self._goalVic + ' oppakt in ' + self._foundVictimLocs[self._goalVic]['room'] + ' omdat ' + self._foundVictimLocs[self._goalVic]['room'] + ' ver weg is en u sneller kunt lopen. Als u het ermee eens bent, druk dan het "Yes" knopje. Zo niet, druk dan op "No"', 'RescueBot')
                        if self._condition=="transparent":
                            self._sendMessage('Ik stel voor dat u ' + self._goalVic + ' oppakt in ' + self._foundVictimLocs[self._goalVic]['room'] + '. Als u het ermee eens bent, druk dan het "Yes" knopje. Zo niet, druk dan op "No"', 'RescueBot')
                        if self._condition=="adaptive":
                            msg1 = 'Ik stel voor dat u ' + self._goalVic + ' oppakt in ' + self._foundVictimLocs[self._goalVic]['room'] + ' omdat ' + self._foundVictimLocs[self._goalVic]['room'] + ' ver weg is en u sneller kunt lopen. Als u het ermee eens bent, druk dan het "Yes" knopje. Zo niet, druk dan op "No"'
                            msg2 = 'Ik stel voor dat u ' + self._goalVic + ' oppakt in ' + self._foundVictimLocs[self._goalVic]['room'] + '. Als u het ermee eens bent, druk dan het "Yes" knopje. Zo niet, druk dan op "No"'
                            explanation = 'omdat het ver weg is en u sneller kunt lopen.'
                            self._dynamicMessage(msg1,msg2,explanation,'RescueBot')
                        if self.received_messages and self.received_messages[-1]=='Yes' or self._goalVic in self._collectedVictims:
                            self._collectedVictims.append(self._goalVic)
                            self._phase=Phase.FIND_NEXT_GOAL
                        if self.received_messages and self.received_messages[-1]=='No' or state['World']['nr_ticks'] > self._tick + 579:
                            self._phase=Phase.PLAN_PATH_TO_ROOM
                        if self._mode=='normal':
                            return Idle.__name__,{'duration_in_ticks':50}
                        if self._mode=='quick':
                            return Idle.__name__,{'duration_in_ticks':10}
                    if self._goalVic in self._uncarryable:
                        if self._condition=="explainable":
                            self._sendMessage('U zal ' + self._goalVic + ' moeten oppakken in ' + self._foundVictimLocs[self._goalVic]['room'] + ' want ik mag geen kritiek gewonde volwassenen tillen.', 'RescueBot')
                        if self._condition=="adaptive":
                            msg1 = 'U zal ' + self._goalVic + ' moeten oppakken in ' + self._foundVictimLocs[self._goalVic]['room'] + ' want ik mag geen kritiek gewonde volwassenen tillen.'
                            msg2 = 'U zal ' + self._goalVic + ' moeten oppakken in ' + self._foundVictimLocs[self._goalVic]['room']
                            explanation = ' want ik mag geen kritiek gewonde volwassenen tillen.'
                            self._dynamicMessage(msg1,msg2,explanation,'RescueBot')
                        if self._condition=="transparent" or self._condition=="silent":
                            self._sendMessage('U zal ' + self._goalVic + ' moeten oppakken in ' + self._foundVictimLocs[self._goalVic]['room']+'.','RescueBot')
                        self._collectedVictims.append(self._goalVic)
                        self._phase=Phase.FIND_NEXT_GOAL
                        if self._mode=='normal':
                            return Idle.__name__,{'duration_in_ticks':50}
                        if self._mode=='quick':
                            return Idle.__name__,{'duration_in_ticks':10}
                    else:
                        self._phase=Phase.PLAN_PATH_TO_ROOM
                        if self._mode=='normal':
                            return Idle.__name__,{'duration_in_ticks':50}
                        if self._mode=='quick':
                            return Idle.__name__,{'duration_in_ticks':10}

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
                        self._sendMessage('Ik ga kamers opnieuw doorzoeken' + self._goalVic +'Omdat we alles hebben doorzocht maar dit slachtoffer niet hebben gevonden:' + self._goalVic,'RescueBot')
                    if self._condition=="transparent":
                        self._sendMessage('Ik ga kamers opnieuw doorzoeken','RescueBot')
                    if self._condition=="adaptive":
                        msg1 = 'Ik ga kamers opnieuw doorzoeken' + self._goalVic +'Omdat we alles hebben doorzocht maar dit slachtoffer niet hebben gevonden:' + self._goalVic
                        msg2 = 'Ik ga kamers opnieuw doorzoeken'
                        explanation = 'Omdat we alles hebben doorzocht'
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
                if self._mode=='quick':
                    return Idle.__name__,{'duration_in_ticks':10}

            if Phase.FOLLOW_PATH_TO_ROOM==self._phase:
                self._mode='normal'
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
                        self._sendMessage('Ik ga naar ' + str(self._door['room_name']) + ' om dit slachtoffer op te pakken: ' + self._goalVic+'.', 'RescueBot')
                    if self._goalVic not in self._foundVictims:
                        if self._condition=="explainable":
                            self._sendMessage('Ik ga naar ' + str(self._door['room_name']) + ' om te zoeken naar ' + self._goalVic + ' omdat dat gebied het meest dichtbij en niet doorzocht is', 'RescueBot')
                        if self._condition=="adaptive":
                            msg1 = 'Ik ga naar ' + str(self._door['room_name']) + ' om te zoeken naar ' + self._goalVic + ' omdat dat gebied het meest dichtbij en niet doorzocht is'
                            msg2 = 'Ik ga naar ' + str(self._door['room_name']) + ' om te zoeken naar ' + self._goalVic +'.'
                            explanation = 'omdat dat gebied het meest dichtbij en niet doorzocht is'
                            self._dynamicMessage(msg1,msg2,explanation,'RescueBot')
                    if self._condition=="transparent":
                        self._sendMessage('Ik ga naar ' + str(self._door['room_name'])+'.', 'RescueBot')
                    self._currentDoor=self._door['location']
                    action = self._navigator.get_move_action(self._state_tracker)
                    if action!=None:
                        return action,{}
                    self._phase=Phase.PLAN_ROOM_SEARCH_PATH
                    if self._mode=='normal':
                        return Idle.__name__,{'duration_in_ticks':50}
                    if self._mode=='quick':
                        return Idle.__name__,{'duration_in_ticks':10}

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
                    self._sendMessage('Ik doorzoek heel ' + str(self._door['room_name']) + ' omdat ik niet zo ver kan kijken. Ik probeer te vinden: ' + self._goalVic+'.', 'RescueBot')
                if self._condition=="transparent":
                    self._sendMessage('Ik doorzoek heel ' + str(self._door['room_name']) + '.', 'RescueBot')
                if self._condition=="adaptive" and ticksLeft>5789:
                    msg1 = 'Ik doorzoek heel ' + str(self._door['room_name']) + ' omdat ik niet zo ver kan kijken. Ik probeer te vinden: ' + self._goalVic + '.'
                    msg2 = 'Ik doorzoek heel ' + str(self._door['room_name']) +'.'
                    explanation = 'omdat ik niet zo ver kan kijken.'
                    self._dynamicMessage(msg1,msg2,explanation,'RescueBot')
                self._roomVics=[]
                self._phase=Phase.FOLLOW_ROOM_SEARCH_PATH
                if self._mode=='normal':
                    return Idle.__name__,{'duration_in_ticks':50}
                if self._mode=='quick':
                    return Idle.__name__,{'duration_in_ticks':10}

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
                                        self._sendMessage('Ik heb '+ vic + ' gevonden in ' + self._door['room_name'] + ' omdat u mij vertelde dat ' + vic + ' zich daar bevond.', 'RescueBot')
                                    if self._condition=="transparent":
                                        self._sendMessage('Ik heb '+ vic + ' gevonden in ' + self._door['room_name'] + '.', 'RescueBot')
                                    if self._condition=="adaptive":
                                        msg1 = 'Ik heb '+ vic + ' gevonden in ' + self._door['room_name'] + ' omdat u mij vertelde dat ' + vic + ' zich daar bevond.'
                                        msg2 = 'Ik heb '+ vic + ' gevonden in ' + self._door['room_name'] + '.'
                                        explanation = 'omdat u mij vertelde dat die zich daar bevond'
                                        self._dynamicMessage(msg1,msg2,explanation,'RescueBot')
                                    self._searchedRooms.append(self._door['room_name'])
                                    self._phase=Phase.FIND_NEXT_GOAL

                            if 'healthy' not in vic and vic not in self._foundVictims and 'boy' not in vic and 'girl' not in vic:
                                if self._condition=="explainable":
                                    self._sendMessage('Ik heb '+ vic + ' gevonden in ' + self._door['room_name'] + ' omdat ik het hele gebied doorzoek.', 'RescueBot')
                                if self._condition=="transparent":
                                    self._sendMessage('Ik heb  '+ vic + ' gevonden in ' + self._door['room_name'] + '.', 'RescueBot')
                                if self._condition=="adaptive":
                                    msg1 = 'Ik heb '+ vic + ' gevonden in ' + self._door['room_name'] + ' omdat ik het hele gebied doorzoek.'
                                    msg2 = 'Ik heb '+ vic + ' gevonden in ' + self._door['room_name']+'.'
                                    explanation = 'omdat ik het hele gebied doorzoek.'
                                    self._dynamicMessage(msg1,msg2,explanation,'RescueBot')
                                if vic==self._goalVic and vic in self._uncarryable:
                                    if self._condition=="explainable":
                                        self._sendMessage('URGENT: U zal ' + vic + ' moeten oppakken in ' + self._door['room_name'] + ' want ik mag geen kritiek gewonde volwassenen tillen.', 'RescueBot')
                                    if self._condition=="adaptive":
                                        msg1 = 'URGENT: U zal ' + vic + ' moeten oppakken in ' + self._door['room_name'] + ' want ik mag geen kritiek gewonde volwassenen tillen.'
                                        msg2 = 'URGENT: U zal ' + vic + ' moeten oppakken in ' + self._door['room_name'] +'.'
                                        explanation = 'want ik mag geen kritiek gewonde volwassenen tillen.'
                                        self._dynamicMessage(msg1,msg2,explanation,'RescueBot')
                                    if self._condition=="silent" or self._condition=="transparent":
                                        self._sendMessage('URGENT: U zal ' + vic + ' moeten oppakken in ' + self._door['room_name']+'.', 'RescueBot')
                                    self._foundVictim=str(info['img_name'][8:-4])
                                    self._phase=Phase.WAIT_FOR_HUMAN
                                    self._tick = state['World']['nr_ticks']
                                    self._mode='quick'
                                self._foundVictims.append(vic)
                                self._foundVictimLocs[vic] = {'location':info['location'],'room':self._door['room_name'],'obj_id':info['obj_id']}

                            if vic in self._undistinguishable and vic not in self._foundVictims and vic!=self._waitedFor:
                                if self._condition=="explainable":
                                    self._sendMessage('URGENT: U zal mij moeten vertellen of de gewonde baby een jongen of meisje is ' + self._door['room_name'] + ' omdat ik die niet kan onderscheiden. Komt u alstublieft hiernaartoe en druk op het knopje "Boy" or "Girl".', 'RescueBot')
                                if self._condition=="adaptive":
                                    msg1 = 'URGENT: U zal mij moeten vertellen of de gewonde baby een jongen of meisje is ' + self._door['room_name'] + ' omdat ik die niet kan onderscheiden. Komt u alstublieft hiernaartoe en druk op het knopje "Boy" or "Girl".'
                                    msg2 = 'URGENT: U zal mij moeten vertellen of de gewonde baby een jongen of meisje is ' + self._door['room_name'] + '. Komt u alstublieft hiernaartoe en druk op het knopje "Boy" or "Girl".'
                                    explanation = 'because I am unable to distinguish them'
                                    self._dynamicMessage(msg1,msg2,explanation,'RescueBot')
                                if self._condition=="silent" or self._condition=="transparent":
                                    self._sendMessage('URGENT: U zal mij moeten vertellen of de gewonde baby een jongen of meisje is ' + self._door['room_name'] + '. Komt u alstublieft hiernaartoe en druk op het knopje "Boy" or "Girl".', 'RescueBot')
                                self._foundVictim=str(info['img_name'][8:-4])
                                self._foundVictimLoc=info['location']
                                self._foundVictimID=info['obj_id']
                                self._tick = state['World']['nr_ticks']
                                self._mode='quick'
                                self._phase=Phase.WAIT_FOR_HUMAN
                    return action,{}
                #if self._goalVic not in self._foundVictims:
                #    self._sendMessage(self._goalVic + ' not present in ' + str(self._door['room_name']) + ' because I searched the whole area without finding ' + self._goalVic, 'RescueBot')
                if self._goalVic in self._foundVictims and self._goalVic not in self._roomVics and self._foundVictimLocs[self._goalVic]['room']==self._door['room_name']:
                    if self._condition=="explainable":
                        self._sendMessage(self._goalVic + ' is niet aanwezig in ' + str(self._door['room_name']) + ' want ik het het hele gebied doorzocht zonder dit slachtoffer te vinden: ' + self._goalVic+'.', 'RescueBot')
                    if self._condition=="transparent":
                        self._sendMessage(self._goalVic + ' is niet aanwezig in ' + str(self._door['room_name']) + '.', 'RescueBot')
                    if self._condition=="adaptive":
                        msg1 = self._goalVic + ' is niet aanwezig in ' + str(self._door['room_name']) + ' want ik het het hele gebied doorzocht zonder dit slachtoffer te vinden: ' + self._goalVic +'.'
                        msg2 = self._goalVic + ' is niet aanwezig in ' + str(self._door['room_name'])+'.'
                        explanation = 'want ik het het hele gebied doorzocht'
                        self._dynamicMessage(msg1,msg2,explanation,'RescueBot')
                    self._foundVictimLocs.pop(self._goalVic, None)
                    self._foundVictims.remove(self._goalVic)
                    self._roomVics = []
                    self.received_messages=[]
                self._searchedRooms.append(self._door['room_name'])
                self._phase=Phase.FIND_NEXT_GOAL
                if self._mode=='normal':
                    return Idle.__name__,{'duration_in_ticks':50}
                if self._mode=='quick':
                    return Idle.__name__,{'duration_in_ticks':10}

            if Phase.WAIT_FOR_HUMAN==self._phase:
                self._state_tracker.update(state)
                if state[{'is_human_agent':True}]:
                    if self._foundVictim in self._undistinguishable and self.received_messages[-1].lower()==self._foundVictim.split()[-1]:
                        if self._condition=="explainable":
                            self._sendMessage('Ik heb '+self._foundVictim + ' gevonden in ' + self._door['room_name'] + ' want ik doorzoek het hele gebied.', 'RescueBot')
                        if self._condition=="transparent":
                            self._sendMessage('Ik heb  '+self._foundVictim + ' gevonden in ' + self._door['room_name'] + '.', 'RescueBot')
                        if self._condition=="adaptive":
                            msg1 = 'Ik heb '+ self._foundVictim + ' gevonden in ' + self._door['room_name'] + ' want ik doorzoek het hele gebied.'
                            msg2 = 'Ik heb '+ self._foundVictim + ' gevonden in ' + self._door['room_name']+'.'
                            explanation = 'want ik doorzoek het hele gebied.'
                            self._dynamicMessage(msg1,msg2,explanation,'RescueBot')
                        self._foundVictims.append(self._foundVictim)
                        self._foundVictimLocs[self._foundVictim] = {'location':self._foundVictimLoc,'room':self._door['room_name'],'obj_id':self._foundVictimID}
                        self._phase=Phase.FOLLOW_ROOM_SEARCH_PATH
                        if self._mode=='normal':
                            return Idle.__name__,{'duration_in_ticks':50}
                        if self._mode=='quick':
                            return Idle.__name__,{'duration_in_ticks':10}
                    if self._foundVictim in self._uncarryable:
                        self._collectedVictims.append(self._goalVic)
                        self._phase=Phase.FOLLOW_ROOM_SEARCH_PATH
                    if self._foundVictim in self._undistinguishable and self.received_messages[-1].lower()=='boy' and self._foundVictim.split()[-1]=='girl' or self.received_messages[-1].lower()=='girl' and self._foundVictim.split()[-1]=='boy':
                        self._phase=Phase.FOLLOW_ROOM_SEARCH_PATH
                        self._waitedFor=self._foundVictim
                    else:
                        return None,{}
                else:
                    if self._foundVictim in self._undistinguishable:
                        #self._sendMessage('Waiting for human in ' + str(self._door['room_name']), 'RescueBot')
                        ## TO FIX
                        if state['World']['nr_ticks'] > self._tick + 1158:
                            self._phase=Phase.FOLLOW_ROOM_SEARCH_PATH
                            self._waitedFor=self._foundVictim
                        if self._foundVictim not in self._foundVictims or self._foundVictim in self._uncarryable:
                            return None,{}
                        if self._foundVictim in self._foundVictims and self._foundVictim not in self._uncarryable:
                            self._phase=Phase.FOLLOW_ROOM_SEARCH_PATH
                    if self._foundVictim in self._uncarryable:
                        if state['World']['nr_ticks'] > self._tick + 1158:
                            self._phase=Phase.FOLLOW_ROOM_SEARCH_PATH
                            self._waitedFor=self._foundVictim
                            self._collectedVictims.append(self._foundVictim)
                        else:
                            return None,{}

            if Phase.PLAN_PATH_TO_VICTIM==self._phase:
                if self._condition=="explainable":
                    self._sendMessage('Ik pak ' + self._goalVic + ' op in ' + self._foundVictimLocs[self._goalVic]['room'] + ' omdat ' + self._goalVic + ' naar de afleverlocatie gebracht moet worden.', 'RescueBot')
                if self._condition=="transparent":
                    self._sendMessage('Picking up ' + self._goalVic + ' in ' + self._foundVictimLocs[self._goalVic]['room'] + '.', 'RescueBot')
                if self._condition=="adaptive":
                    msg1 = 'Ik pak ' + self._goalVic + ' op in ' + self._foundVictimLocs[self._goalVic]['room'] + ' omdat ' + self._goalVic + ' naar de afleverlocatie gebracht moet worden.'
                    msg2 = 'Ik pak ' + self._goalVic + ' op in ' + self._foundVictimLocs[self._goalVic]['room']+'.'
                    explanation = 'omdat het naar de afleverlocatie gebracht moet worden.'
                    self._dynamicMessage(msg1,msg2,explanation,'RescueBot')
                self._navigator.reset_full()
                self._navigator.add_waypoints([self._foundVictimLocs[self._goalVic]['location']])
                self._phase=Phase.FOLLOW_PATH_TO_VICTIM
                if self._mode=='normal':
                    return Idle.__name__,{'duration_in_ticks':50}
                if self._mode=='quick':
                    return Idle.__name__,{'duration_in_ticks':10}

            if Phase.FOLLOW_PATH_TO_VICTIM==self._phase:
                self._mode='normal'
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
                    self._sendMessage('Ik verplaats '+ self._goalVic + ' naar de afleverlocatie omdat ' + self._goalVic + ' daar naartoe gebracht moet worden voor behandeling.', 'RescueBot')
                if self._condition=="transparent":
                    self._sendMessage('Ik verplaats '+ self._goalVic + ' naar de afleverlocatie.', 'RescueBot')
                if self._condition=="adaptive" and ticksLeft>5789:
                    msg1 = 'Ik verplaats '+ self._goalVic + ' naar de afleverlocatie omdat ' + self._goalVic + ' daar naartoe gebracht moet worden voor behandeling.'
                    msg2 = 'Ik verplaats '+ self._goalVic + ' naar de afleverlocatie.'
                    explanation = 'omdat die daar naartoe gebracht moet worden voor behandeling'
                    self._dynamicMessage(msg1,msg2,explanation,'RescueBot')
                self._state_tracker.update(state)
                action=self._navigator.get_move_action(self._state_tracker)
                if action!=None:
                    return action,{}
                self._phase=Phase.DROP_VICTIM
                #if self._mode=='normal':
                #    return Idle.__name__,{'duration_in_ticks':50}
                #if self._mode=='quick':
                #    return Idle.__name__,{'duration_in_ticks':10}

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
                        self._sendMessage('Ik heb '+ self._goalVic + ' afgeleverd op de afleverlocatie omdat ' + self._goalVic + ' aan de beurt was om gered te worden.', 'RescueBot')
                    if self._condition=="transparent":
                        self._sendMessage('Ik heb '+ self._goalVic + ' afgeleverd op de afleverlocatie.', 'RescueBot')
                    if self._condition=="adaptive":
                        msg1 = 'Ik heb '+ self._goalVic + ' afgeleverd op de afleverlocatie omdat ' + self._goalVic + ' aan de beurt was om gered te worden.'
                        msg2 = 'Ik heb '+ self._goalVic + ' afgeleverd op de afleverlocatie.'
                        explanation = 'omdat die aan de beurt was om gered te worden.'
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
                        self._sendMessage('Ik wacht op de menselijke bestuurder bij de afleverlocatie omdat het vorige slachtoffer eerst verzameld moet worden.', 'RescueBot')
                    if self._condition=="transparent":
                        self._sendMessage('Ik wacht op de menselijke bestuurder bij de afleverlocatie.', 'RescueBot')
                    if self._condition=="adaptive":
                        msg1 = 'Ik wacht op de menselijke bestuurder bij de afleverlocatie omdat het vorige slachtoffer eerst verzameld moet worden.'
                        msg2 = 'Ik wacht op de menselijke bestuurder bij de afleverlocatie.'
                        explanation = 'omdat het vorige slachtoffer eerst verzameld moet worden.'
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
            if msg.startswith("'Ik doorzoek'"):
                area = 'area '+ msg.split()[-1]
                if area not in self._searchedRooms:
                    self._searchedRooms.append(area)
            if msg.startswith("Ik heb:"):
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
            if self._last_mssg.startswith('Ik doorzoek') or self._last_mssg.startswith('Ik ga naar'):
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
        if 'Ik doorzoek' in mssg1:
            #history = ['Searching' in mssg for mssg in self._sendMessages]
            if explanation in self._providedExplanations and mssg1 not in self._sendMessages[-5:]:
                self._sendMessage(mssg2,sender)
        if 'Ik heb ' in mssg1:
            history = [mssg2[:-1] in mssg for mssg in self._sendMessages]
            if explanation in self._providedExplanations and True not in history:
                self._sendMessage(mssg2,sender)
        if 'Ik doorzoek' not in mssg1 and 'Ik heb ' not in mssg1:
            if explanation in self._providedExplanations and self._sendMessages[-1]!=mssg1:
                self._sendMessage(mssg2,sender)

    def _getAgeRange(self, age):
        if age >= 0 and age < 5:
            return "0 en 5"
        elif age >= 5 and age < 10:
            return "5 en 10"
        elif age >= 10 and age < 15:
            return "10 en 15"
        elif age >= 15 and age < 20:
            return "15 en 20"
        elif age >= 20 and age < 25:
            return "20 en 25"
        elif age >= 25 and age < 30:
            return "25 en 30"
        elif age >= 30 and age < 35:
            return "30 en 35"
        elif age >= 35 and age < 40:
            return "35 en 40"
        elif age >= 40 and age < 45:
            return "40 en 45"
        elif age >= 45 and age < 50:
            return "45 en 50"
        elif age >= 50 and age < 55:
            return "50 en 55"
        elif age >= 55 and age < 60:
            return "55 en 60"
        elif age >= 60 and age < 65:
            return "60 en 65"
        elif age >= 65 and age < 70:
            return "65 en 70"
        elif age >= 70 and age < 75:
            return "70 en 75"
        elif age >= 75 and age < 80:
            return "75 en 80"
        elif age >= 80 and age < 85:
            return "80 en 85"
        elif age >= 85 and age < 90:
            return "85 en 90"
        elif age >= 90 and age < 95:
            return "90 en 95"
        elif age >= 95 and age < 100:
            return "95 en 100"

    def _sendPositiveMessage(self):
        seed = randrange(12)

        if seed == 0 and "Ziet u wel, ik zei toch dat ik geluk met u had!" not in self.received_messages:
            self._positivenessGiven.append("Ziet u wel, ik zei toch dat ik geluk met u had!")
            self._sendMessage("Ziet u wel, ik zei toch dat ik geluk met u had!", "RescueBot")

        elif seed == 1 and "Goed gedaan " + self._human_name + "!" not in self._positivenessGiven:
            self._positivenessGiven.append("Goed gedaan " + self._human_name + "!")
            self._sendMessage("Goed gedaan " + self._human_name + "!", "RescueBot.")

        elif seed == 2 and "Mijn familie is u dankbaar." not in self._positivenessGiven:
            self._positivenessGiven.append("Mijn familie is u dankbaar.")
            self._sendMessage("Mijn familie is u dankbaar.", "RescueBot")

        elif seed == 3 and "Weet u wat " + self._human_name + ", U bent fantastisch en ik mag u heel graag." not in self.received_messages:
            self._positivenessGiven.append("Weet u wat " + self._human_name + ", U bent fantastisch en ik mag u heel graag.")
            self._sendMessage("Weet u wat " + self._human_name + ", U bent fantastisch en ik mag u heel graag.", "RescueBot")

        elif seed == 4 and "Ik herken talent wanneer ik het zie." not in self._positivenessGiven:
            self._positivenessGiven.append("Ik herken talent wanneer ik het zie.")
            self._sendMessage("Ik herken talent wanneer ik het zie.", "RescueBot")

        elif seed == 5 and "Dat is fantastisch. U bent fantastisch. Ga zo door!" not in self._positivenessGiven:
            self._positivenessGiven.append("Dat is fantastisch. U bent fantastisch. Ga zo door!")
            self._sendMessage("Dat is fantastisch. U bent fantastisch. Ga zo door!", "RescueBot")

        elif seed == 6 and "Dankuwel! Als ik een mens was geweest had ik zeker met u samen willen chillen." not in self.received_messages:
            self._positivenessGiven.append("Dankuwel! Als ik een mens was geweest had ik zeker met u samen willen chillen.")
            self._sendMessage("Dankuwel! Als ik een mens was geweest had ik zeker met u samen willen chillen.", "RescueBot")

        elif seed == 7 and "We zijn ze daadwerkelijk aan het redden!" not in self._positivenessGiven:
            self._positivenessGiven.append("We zijn ze daadwerkelijk aan het redden!")
            self._sendMessage("We zijn ze daadwerkelijk aan het redden!", "RescueBot")
        elif seed == 8 and "Yes we kunnen het!" not in self._positivenessGiven:
            self._positivenessGiven.append("Yes we kunnen het!")
            self._sendMessage("Yes we kunnen het!", "RescueBot")
        elif seed == 9 and "Oohh wat een prachtige man dat u bent" not in self._positivenessGiven and "Oohh wat een prachtige vrouw dat u bent" not in self._positivenessGiven:
            if self._human_gender == 'Boy':
                self._positivenessGiven.append("Oohh wat een prachtige man dat u bent")
                self._sendMessage("Oohh wat een prachtige man dat u bent", "RescueBot")
            else:
                self._positivenessGiven.append("Oohh wat een prachtige vrouw dat u bent")
                self._sendMessage("Oohh wat een prachtige vrouw dat u bent", "RescueBot")
