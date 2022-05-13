import numpy as np

ROOMS = [
    {"top_left_location": (17, 1), "width": 6, "height": 10, "room_name": 'A4', "door_location": (17, 5)},
    {"top_left_location": (3, 2), "width": 3, "height": 3, "room_name": 'A1', "door_location": (4, 4)},
    {"top_left_location": (7, 2), "width": 3, "height": 3, "room_name": 'A2', "door_location": (8, 4)},
    {"top_left_location": (11, 2), "width": 3, "height": 3, "room_name": 'A3', "door_location": (12, 4)},
    {"top_left_location": (1, 7), "width": 3, "height": 5, "room_name": 'B1', "door_location": (2, 11)},
    {"top_left_location": (5, 7), "width": 9, "height": 6, "room_name": 'B2', "door_location": (9, 12)},
    {"top_left_location": (1, 17), "width": 5, "height": 4, "room_name": 'C1', "door_location": (3, 17)},
    {"top_left_location": (7, 17), "width": 5, "height": 4, "room_name": 'C2', "door_location": (9, 17)},
    {"top_left_location": (16, 13), "width": 7, "height": 11, "room_name": 'C3', "door_location": (16, 18)}]

DROPOFF_LOCATION = [
    {"top_left_location": (1, 23), "person": "critically injured girl in area C2"},
    {"top_left_location": (2, 23), "person": "critically injured elderly woman in area A1"},
    {"top_left_location": (3, 23), "person": "critically injured man in area A4"},
    {"top_left_location": (4, 23), "person": "critically injured dog in area C3"},
    {"top_left_location": (5, 23), "person": "mildly injured boy in area B2"},
    {"top_left_location": (6, 23), "person": "mildly injured elderly man in area A4"},
    {"top_left_location": (7, 23), "person": "mildly injured woman in area C3"},
    {"top_left_location": (8, 23), "person": "mildly injured cat in area C1"},
]

NUMBER_OF_VICTIMS = 8


# returns true if person is dropped off in their correct drop-off location.
def is_correct_drop_location(person, location):
    for drop_off in DROPOFF_LOCATION:
        if drop_off["top_left_location"] == location and drop_off["person"] == person:
            return True
    return False


# returns the room if the given position is inside that room
def is_in_room(location):
    for room in ROOMS:
        if location == room["door_location"] or (
                room["top_left_location"][0] < location[0] < room["top_left_location"][0] + room["width"] and
                room["top_left_location"][1] < location[1] < room["top_left_location"][1] + room["height"]):
            return room["room_name"]


# returns persons in a certain room
def get_persons_in_room(room_name, map_state):
    persons = []
    for person in map_state["persons"]:
        if is_in_room(person["location"]) == room_name:
            persons.append(person)
    return persons


# Returns true if a person is in sense range (1 block) of the human
def is_in_range(person_location, human_location):
    return np.abs(person_location[0] - human_location[0]) <= 1 and np.abs(
        person_location[1] - human_location[1]) <= 1 and (
                   person_location[0] == human_location[0] or person_location[1] == human_location[1])
