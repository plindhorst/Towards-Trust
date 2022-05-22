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
    
class TutorialAgentDutch(BW4TBrain):
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

                self._sendMessage('Hoi! Mijn naam is RescueBot. Tijdens dit experiment zullen wij met elkaar \
                samenwerken en communiceren. Ons doel is om de slachtoffers die je op de afleverlocatie links van \
                ons ziet zo snel mogelijk te zoeken en te redden. We moeten de slachtoffers redden in volgorde \
                van links naar rechts, dus het is belangrijk om een slachtoffer pas af te leveren als de vorige \
                al afgeleverd is. U zal berichten ontvangen in de chatbox. U kunt zelf berichten sturen door op de \
                knopjes te drukken. Het advies is om berichten te sturen wanneer u een gebied gaat doorzoeken, \
                wanneer u een van de slachtoffers vindt en wanneer u een slachtoffer gaat oppakken. Er zijn 8 \
                typen slachtoffers die zich in 3 verschillende staten van gezondheid kunnen bevinden. de rode kleur \
                betekent dat het slachtoffer zwaar gewond is. Geel betekent licht gewond en groen betekent dat ze \
                gezond zijn. De acht slachtoffers zijn een meisje (critically injured girl/mildly injured girl/healthy girl), \
                een jongen (critically injured boy/mildly injured boy/healthy boy), een vrouw (critically injured woman/mildly injured woman/healthy woman), \
                een man (critically injured man/mildly injured man/healthy man), een bejaarde vrouw (critically injured elderly woman/mildly injured elderly woman/healthy elderly woman), \
                een bejaarde man (critically injured elderly man/mildly injured elderly man/healthy elderly man), \
                een hond (critically injured dog/mildly injured dog/healthy dog) en een kat (critically injured cat/mildly injured cat/healthy cat). \
                Aan de top van het scherm ziet u de lettertoetsen om het spel te spelen. Om te bewegen kunt u ook \
                simpelweg de pijltjestoetsen gebruiken. U kunt slechts 1 blokje naast u zien, dus het is belangrijk om de verschillende gebieden te doorzoeken. \
                We gaan nu alles wat hierboven genoemd is oefenen en eigen maken, totdat u zich comfortabel genoeg \
                voelt om het echte experiment te beginnen. Als u alles heeft gelezen, druk dan op het "Ready!" knopje.', 'RescueBot')

                if self.received_messages and self.received_messages[-1]=='Ready!':
                    self._phase=Phase.INTRO1
                    self.received_messages=[]
                else:
                    return None,{}

            if Phase.INTRO1==self._phase:
                self._sendMessage('Laten we eerst met de toetsen beginnen. U kunt bewegen met de pijltjestoetsen. \
                Als u twee keer omhoog beweegt, zult u zien dat u mij nu niet langer meer kunt zien. \
                Dit komt doordat u maar 1 vakje naast uzelf kunt zien. Daarom is het belangrijk om de gebieden te doorzoeken. \
                Als u twee keer omhoog heeft bewogen kunt u op het knopje "Ready!" drukken.', 'RescueBot')

                if self.received_messages and self.received_messages[-1]=='Ready!':
                    self._phase=Phase.INTRO2
                    self.received_messages=[]
                else:
                    return None,{}

            if Phase.INTRO2==self._phase:
                self._sendMessage('Laten we nu naar gebied C3 bewegen en het volledig doorzoeken. In dit gebied zal\
                u 4 slachtoffers moeten vinden. Een van hen is het eerste slachtoffer dat we naar de afleverlocatie \
                moeten brengen: critically injured girl. De andere drie zijn gezond. Als u het hele gebied heeft \
                doorzocht en de 4 slachtoffers heeft gevonden, druk dan op het "Ready!" knopje.', 'RescueBot')

                if self.received_messages and self.received_messages[-1]=='Ready!':
                    self._phase=Phase.INTRO3
                    self.received_messages=[]
                else:
                    return None,{}

            if Phase.INTRO3==self._phase:

                self._sendMessage('Laten we nu onze eerste slachtoffer oppakken: critically injured girl. Om een \
                slachtoffer op te pakken, gaat u eerst op het slachtoffer staan. Vervolgens kunt u "b" of "q" op uw toetsenbord \
                indrukken om het slachtoffer op te pakken. Als u nu naar links, rechts, boven of onder beweegt ziet u \
                dat het slachtoffer daar niet meer is. U kunt 1 slachtoffer tegelijk dragen. Als u klaar bent met deze \
                stap, druk dan op het "Ready!" knopje', 'RescueBot')

                if self.received_messages and self.received_messages[-1]=='Ready!':
                    self._phase=Phase.INTRO4
                    self.received_messages=[]
                else:
                    return None,{}

            if Phase.INTRO4==self._phase:
                self._sendMessage('Laten we nu onze eerste slachtoffer critically injured girl afleveren op de afleverlocatie. \
                U vindt de afleverlocatie linksonder, naast het punt waar u bent begonnen. U kunt naar de afleverlocatie \
                toe bewegen met de pijltjestoetsen. Zodra u bent aangekomen, ga dan op het afbeelding staan van het eerste slachtoffer \
                dat u nu draagt (critically injured girl). Aangezien u nu het eerste slachtoffer draagt is dit het meest \
                linkse afbeelding van de afleverlocatie. Zodra u up het afbeelding staat, druk dan "n" of "e" op uw toetsenbord \
                om het slachtoffer te laten vallen. Als u nu eenmaal naar rechts beweegt, ziet u dat u critically injured girl \
                op de juiste plek heeft afgeleverd. Als u deze stap heeft voltooid, druk dan op het "Ready!" knopje.', 'RescueBot')

                if self.received_messages and self.received_messages[-1]=='Ready!':
                    self._phase=Phase.INTRO5
                    self.received_messages=[]
                else:
                    return None,{}

            if Phase.INTRO5==self._phase:

                self._sendMessage('U heeft zojuist het eerste slachtoffer afgeleverd, cool! tijd voor de volgende stap, \
                namelijk slachtoffer: critically injured elderly woman. Laten we naar gebied C2 bewegen en zoeken naar dit slachtoffer. \
                Maar dit keer, laat me in de chat weten dat u gebied C2 gaat doorzoeken. Dit kunt u doen door op het knopje \
                "C2" te drukken. Op die manier kunt u ervoor zorgen dat ik niet ook dit gebied ga doorzoeken om \
                critically injured elderly woman te vinden en zo kunnen we dus efficiënter samenwerken! \
                Als u op het knopje "C2" hebt gedrukt en naar de ingang van het gebied hebt bewogen, druk dan op het \
                knopje "Ready!".', 'RescueBot')

                if self.received_messages and self.received_messages[-1]=='Ready!':
                    self._phase=Phase.INTRO6
                    self.received_messages=[]
                else:
                    return None,{}

            if Phase.INTRO6==self._phase:

                self._sendMessage('U zou zich nu in gebied C2 moeten bevinden. Als u dit gebied doorzoekt dan zal u \
                critically injured elderly woman en mildly injured cat moeten vinden. Wanneer u een van onze slachtoffers \
                in een gebied vindt dan is het belangrijk dat u dit doorgeeft aan mij via de chat. u kunt dit doen met \
                de onderstaande knopjes bij: "I have found:". Bijvoorbeeld, in dit gebied zou u op het knopje \
                "critically injured elderly woman in C2" en "mildly injured cat in C2" moeten drukken. U kunt de juiste \
                kamer selecteren in het dropdown menu. Als u deze informatie met mij deelt dan verbetert dat onze \
                efficientie dus dat is ten zeerste aan te raden! Als u het hele gebied heeft doorzocht, twee slachtoffers heeft \
                gevonden en dit heeft gecommuniceerd met de "found" knopjes, druk dan op het "Ready!" knopje.', 'RescueBot')

                if self.received_messages and self.received_messages[-1]=='Ready!':
                    self._foundVictimLocs['mildly injured cat'] = {'room':'area C2'}
                    self._phase=Phase.INTRO7
                    self.received_messages=[]
                else:
                    return None,{}

            if Phase.INTRO7==self._phase:


                self._sendMessage('Laten we het volgende slachtoffer critically injured elderly woman in area C2 oppakken en afleveren op de afleverlocatie.\
                Maar dit keer, laat me weten wanneer u het slachtoffer op gaat pakken door het daarbij behorende knopje te gebruiken. \
                Net als toen u dit slachtoffer vond, druk op het knopje "critically injured elderly woman in C2" onder "I will pick up:". \
                Op die manier weet ik dat ik niet meer naar dit slachtoffer hoef te zoeken, en kan ik beginnen met de zoektocht \
                naar het volgende slachtoffer: critically injured man. Nadat u het bericht naar mij heeft verstuurd kunt u  \
                critically injured elderly woman oppakken, naar de afleverlocatie bewegen, en critically injured elderly woman \
                op de juiste plek afleveren. Als u dit heeft gedaan, druk dan op het "Ready!" knopje.', 'RescueBot')

                if self.received_messages and self.received_messages[-1]=='Ready!':
                    self._phase=Phase.INTRO8
                    self.received_messages=[]
                else:
                    return None,{}

            if Phase.INTRO8==self._phase:
                self._sendMessage('U heeft zojuist het tweede slachtoffer critically injured elderly woman gered, goed gedaan! \
                U zou nu een goed begrip moeten hebben van alle toetsen om te bewegen en knoppen om berichten te sturen. \
                De volgende stap is een klein voorproefje van hoe het echte experiment zal zijn. \
                Ik zal nu ook rondbewegen, gebieden doorzoeken, slachtoffers oppakken en afleveren en relevante \
                informatie met u delen tijdens de missie. We moeten nog steeds de volgende slachtoffers redden in deze \
                volgorde: critically injured man, critically injured dog, mildly injured boy, mildly injured elderly man, mildly injured woman, mildly injured cat. \
                Zodra we het laatste slachtoffer hebben afgeleverd mildly injured cat, zal het spel automatisch stoppen. \
                Als u klaar bent om te zoeken voor critically injured man, druk dan op het "Ready!" knopje.' , 'RescueBot')

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
                        return Idle.__name__,{'duration_in_ticks':50}
                    else:
                        self._phase=Phase.PLAN_PATH_TO_VICTIM
                        return Idle.__name__,{'duration_in_ticks':50}
                        
                if self._goalVic in self._foundVictims and 'location' not in self._foundVictimLocs[self._goalVic].keys():
                    if self._condition!="silent" and self._foundVictimLocs[self._goalVic]['room'] in ['area A1', 'area A2', 'area A3', 'area A4'] and state[self.agent_id]['location'] in locs and self._collectedVictims:
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
                    self._sendMessage('Ik doorzoek heel ' + str(self._door['room_name']) + ' omdat ik niet zo ver kan kijken. Ik probeer te vinden: ' + self._goalVic+'.', 'RescueBot')
                if self._condition=="transparent":
                    self._sendMessage('Ik doorzoek heel ' + str(self._door['room_name']) + '.', 'RescueBot')
                if self._condition=="adaptive" and ticksLeft>5789:
                    msg1 = 'Ik doorzoek heel ' + str(self._door['room_name']) + ' omdat ik niet zo ver kan kijken. Ik probeer te vinden: ' + self._goalVic + '.'
                    msg2 = 'Ik doorzoek heel ' + str(self._door['room_name']) +'.'
                    explanation = 'omdat ik niet zo ver kan kijken.'
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

                            if 'healthy' not in vic and vic not in self._foundVictims:
                                if self._condition=="explainable":
                                    self._sendMessage('Ik heb '+ vic + ' gevonden in ' + self._door['room_name'] + ' omdat ik het hele gebied doorzoek.', 'RescueBot')
                                if self._condition=="transparent":
                                    self._sendMessage('Ik heb  '+ vic + ' gevonden in ' + self._door['room_name'] + '.', 'RescueBot')
                                if self._condition=="adaptive":
                                    msg1 = 'Ik heb '+ vic + ' gevonden in ' + self._door['room_name'] + ' omdat ik het hele gebied doorzoek.'
                                    msg2 = 'Ik heb '+ vic + ' gevonden in ' + self._door['room_name']+'.'
                                    explanation = 'omdat ik het hele gebied doorzoek.'
                                    self._dynamicMessage(msg1,msg2,explanation,'RescueBot')
                                self._foundVictims.append(vic)
                                self._foundVictimLocs[vic] = {'location':info['location'],'room':self._door['room_name'],'obj_id':info['obj_id']}
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
                    self.received_messages = []
                self._searchedRooms.append(self._door['room_name'])
                self._phase=Phase.FIND_NEXT_GOAL
                return Idle.__name__,{'duration_in_ticks':50}
                
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
                    self._sendMessage('Ik verplaats '+ self._goalVic + ' naar de afleverlocatie omdat ' + self._goalVic + ' daar naartoe gebracht moet worden voor behandeling.', 'RescueBot')
                if self._condition=="transparent":
                    self._sendMessage('Ik verplaats '+ self._goalVic + ' naar de afleverlocatie.', 'RescueBot')
                if self._condition=="adaptive":
                    msg1 = 'Ik verplaats '+ self._goalVic + ' naar de afleverlocatie omdat ' + self._goalVic + ' daar naartoe gebracht moet worden voor behandeling.'
                    msg2 = 'Ik verplaats '+ self._goalVic + ' naar de afleverlocatie.'
                    explanation = 'omdat die daar naartoe gebracht moet worden voor behandeling'
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
