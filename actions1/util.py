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


# returns the room if the given position is inside that room
def is_in_room(location):
    for room in ROOMS:
        if location == room["door_location"] or (
                room["top_left_location"][0] < location[0] < room["top_left_location"][0] + room["width"] and \
                room["top_left_location"][1] < location[1] < room["top_left_location"][1] + room["height"]):
            return room["room_name"]
