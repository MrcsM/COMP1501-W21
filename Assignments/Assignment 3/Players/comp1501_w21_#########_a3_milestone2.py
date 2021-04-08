# -> AURELIUS

arena_dimensions = (750, 750)
good_dist = 60
e_range = 200
scans = 30

types = {"column": "C", "player": "P", "weapon": "W", "hazard": "H", "wall": "M"}
states = {"move": "0M", "get_weapon": "0G", "avoid": "0A", "hide": "0H", "reveal": "0R", "go_behind": "0B",}
reverse_states = {"0M": "move", "0G": "get_weapon", "0A": "avoid", "0H": "hide", "0R": "reveal", "0B": "go_behind",}

def start():
    return "w_move", {}

def w_move():

    position = get_position_tuple()
    values = get_my_stored_data()
    next_state = "w_move"

    debug_circle = []
    (target1_type, target1_distance, target1_angle, target1_info) = player_scan(values, debug_circle)
    (target2_type, target2_distance, target2_angle, target2_info) = weapon_scan(values, debug_circle)

    if target2_type == types["weapon"] and not get_if_have_weapon():
        next_state = "w_get_weapon"

    if get_if_have_weapon():
        next_state = "a_move"

    if target2_type == types["player"] and target1_info[1]:
        next_state = "c_move"

    s = max(abs(arena_dimensions[0] / 2 - position[0]), abs(arena_dimensions[1] / 2 - position[1]))

    dx = float(arena_dimensions[0] / 2 - position[0]) / s
    dy = float(arena_dimensions[1] / 2 - position[1]) / s

    rot_cc = 0
    rot_cw = 0
    if target1_type == types["player"]:
        throw = get_throwing_angle()
        delta = ((target1_angle - throw) + 360) % 360

        if delta > 180:
            rot_cc = 0
            rot_cw = 1
        else:
            rot_cc = 1
            rot_cw = 0

    (danger, target3_type, target3_distance, target3_angle) = danger_scan(position, get_velocity_tuple())
    if danger:
        next_state = "w_avoid"

    return next_state, create_state_dict(position, dx, dy, rot_cc, rot_cw, "move", target1_type, target1_distance,
                                        target1_angle, target2_type, target2_distance, target2_angle, target3_type,
                                        target3_distance, target3_angle, debug_circle)

def w_get_weapon():

    position = get_position_tuple()
    values = get_my_stored_data()
    next_state = "w_get_weapon"

    debug_circle = []
    (target1_type, target1_distance, target1_angle, target1_info) = player_scan(values, debug_circle)
    (weapon_type, weapon_distance, weapon_angle, weapon_info) = weapon_scan(values, debug_circle)

    if get_if_have_weapon():
        next_state = "a_move"

    if target1_type == types["player"] and target1_info[1]:
        next_state = "c_move"

    if weapon_type != types["weapon"] or weapon_info:
        next_state = "w_" + reverse_states[values[0]]

    (danger, target3_type, target3_distance, target3_angle) = danger_scan(position, get_velocity_tuple())
    if danger:
        next_state = "w_avoid"

    s = max(abs(weapon_distance[0]), abs(weapon_distance[1]))

    dx = float(weapon_distance[0]) / s
    dy = float(weapon_distance[1]) / s

    rot_cc = 0
    rot_cw = 0
    if target1_type == types["player"]:
        throw = get_throwing_angle()
        delta = ((target1_angle - throw) + 360) % 360

        if delta > 180:
            rot_cc = 0
            rot_cw = 1
        else:
            rot_cc = 1
            rot_cw = 0

    state_dict = create_state_dict(position, dx, dy, rot_cc, rot_cw, "get_weapon", target1_type, target1_distance,
                                  target1_angle, weapon_type, weapon_distance, weapon_angle, target3_type,
                                  target3_distance, target3_angle, debug_circle)
    state_dict["WEAPON"] = True

    return next_state, state_dict

def c_move():

    position = get_position_tuple()
    values = get_my_stored_data()
    next_state = "c_move"

    debug_circle = []
    (target1_type, target1_distance, target1_angle, target1_info) = player_scan(values, debug_circle)
    (target2_type, target2_distance, target2_angle, target2_info) = column_scan(values, debug_circle)

    if get_if_have_weapon():
        next_state = "a_move"

    if target1_type == types["player"] and target2_type == types["column"] and target1_info[1]:
        next_state = "c_hide"
    elif target1_type == types["player"] and not target1_info[1]:
        next_state = "w_move"

    target1_angle += 90
    if target1_angle > 359:
        target1_angle = 0 + (target1_angle - 359)
    dx = cos(radians(target1_angle))
    dy = sin(radians(target1_angle))
    if dx > dy:
        dy = 0
    else:
        dx = 0

    rot_cc = 0
    rot_cw = 0
    if target1_type == types["player"]:
        throw = get_throwing_angle()
        delta = ((target1_angle - throw) + 360) % 360

        if delta > 180:
            rot_cc = 0
            rot_cw = 1
        else:
            rot_cc = 1
            rot_cw = 0

    (danger, target3_type, target3_distance, target3_angle) = danger_scan(position, get_velocity_tuple())
    if danger:
        next_state = "c_avoid"

    return next_state, create_state_dict(position, dx, dy, rot_cc, rot_cw, "move", target1_type, target1_distance,
                                        target1_angle, target2_type, target2_distance, target2_angle, target3_type,
                                        target3_distance, target3_angle, debug_circle)

def c_hide():

    position = get_position_tuple()
    values = get_my_stored_data()
    next_state = "c_hide"

    debug_circle = []
    (target1_type, target1_distance, target1_angle, target1_info) = player_scan(values, debug_circle)
    (target2_type, target2_distance, target2_angle, _) = column_scan(values, debug_circle)

    if target1_type != types["player"]:
        next_state = "c_reveal"

    if target2_type != types["column"]:
        next_state = "c_move"

    if target1_type == types["player"] and not target1_info[1]:
        next_state = "w_move"

    player_to_col_vector = (
        target2_distance[0] - target1_distance[0],
        target2_distance[1] - target1_distance[1],
    )
    vector_length = sqrt(player_to_col_vector[0] ** 2 + player_to_col_vector[1] ** 2)
    direction = (player_to_col_vector[0] / vector_length, player_to_col_vector[1] / vector_length)
    vector_behind_col = (
        target2_distance[0] + direction[0] * good_dist,
        target2_distance[1] + direction[1] * good_dist
    )

    s = max(abs(vector_behind_col[0]), abs(vector_behind_col[1]))

    dx = float(vector_behind_col[0]) / s
    if (dx > 1):
        dx = 1
    elif (dx < -1):
        dx = -1
    dy = float(vector_behind_col[1]) / s
    if (dy > 1):
        dy = 1
    elif (dy < -1):
        dy = -1

    if (target2_distance[0] ** 2 + target2_distance[1] ** 2) <= good_dist ** 2:
        dx -= cos(radians(target2_angle))
        if (dx > 1):
            dx = 1
        elif (dx < -1):
            dx = -1
        dy -= sin(radians(target2_angle))
        if (dy > 1):
            dy = 1
        elif (dy < -1):
            dy = -1

    rot_cc = 0
    rot_cw = 0
    if target1_type == types["player"]:
        throw = get_throwing_angle()
        delta = ((target1_angle - throw) + 360) % 360

        if delta > 180:
            rot_cc = 0
            rot_cw = 1
        else:
            rot_cc = 1
            rot_cw = 0

    (danger, target3_type, target3_distance, target3_angle) = danger_scan(position, get_velocity_tuple())
    if danger:
        next_state = "c_avoid"

    state_dict = create_state_dict(position, dx, dy, rot_cc, rot_cw, "hide", target1_type, target1_distance,
                                  target1_angle, target2_type, target2_distance, target2_angle, target3_type,
                                  target3_distance, target3_angle, debug_circle)
    state_dict["DEBUGS"].append((
        int(position[0]),
        int(position[1]),
        int(position[0] + vector_behind_col[0]),
        int(position[1] + vector_behind_col[1]),
    ))

    return next_state, state_dict

def c_reveal():

    position = get_position_tuple()
    values = get_my_stored_data()
    next_state = "c_reveal"

    debug_circle = []
    (target1_type, target1_distance, target1_angle, target1_info) = player_scan(values, debug_circle)
    (target2_type, target2_distance, target2_angle, _) = column_scan(values, debug_circle)

    if target1_type == types["player"] and target1_info[1]:
        next_state = "c_hide"
    elif target1_type == types["player"] and not target1_info[1]:
        next_state = "w_move"

    if target2_type != types["column"]:
        next_state = "c_move"

    if target2_type == types["column"] and (target2_distance[0] ** 2 + target2_distance[1] ** 2 >= 150 ** 2):
        next_state = "c_hide"

    dx = -cos(radians(target2_angle))
    dy = -sin(radians(target2_angle))

    rot_cc = 0
    rot_cw = 0
    if target1_type == types["player"]:
        throw = get_throwing_angle()
        delta = ((target1_angle - throw) + 360) % 360

        if delta > 180:
            rot_cc = 0
            rot_cw = 1
        else:
            rot_cc = 1
            rot_cw = 0

    (danger, target3_type, target3_distance, target3_angle) = danger_scan(position, get_velocity_tuple())
    if danger:
        next_state = "c_avoid"

    return next_state, create_state_dict(position, dx, dy, rot_cc, rot_cw, "reveal", target1_type, target1_distance,
                                        target1_angle, target2_type, target2_distance, target2_angle, target3_type,
                                        target3_distance, target3_angle, debug_circle)

def a_move():

    position = get_position_tuple()
    values = get_my_stored_data()
    next_state = "a_move"

    debug_circle = []
    (target1_type, target1_distance, target1_angle, target1_info) = player_scan(values, debug_circle)
    (target2_type, target2_distance, target2_angle, target2_info) = weapon_scan(values, debug_circle)

    if not get_if_have_weapon():
        if target1_type == types["player"] and target1_info[1]:
            next_state = "c_move"
        else:
            next_state = "w_move"

    if target1_type == types["player"] and not target1_info[1]:
        next_state = "a_go_behind"
    elif target1_type == types["player"] and get_current_status() <= 50 and target1_info[1]:
        next_state = "c_move"

    rot_cc = 0
    rot_cw = 0
    if target1_type == types["player"]:
        throw = get_throwing_angle()
        delta = ((target1_angle - throw) + 360) % 360

        if delta > 180:
            rot_cc = 0
            rot_cw = 1
        else:
            rot_cc = 1
            rot_cw = 0

    (danger, target3_type, target3_distance, target3_angle) = danger_scan(position, get_velocity_tuple())
    if danger:
        next_state = "a_evade"

    return next_state, create_state_dict(position, 0, 0, rot_cc, rot_cw, "move", target1_type, target1_distance,
                                        target1_angle, target2_type, target2_distance, target2_angle, target3_type,
                                        target3_distance, target3_angle, debug_circle)

def a_go_behind():

    position = get_position_tuple()
    values = get_my_stored_data()
    next_state = "a_go_behind"

    debug_circle = []
    (target1_type, target1_distance, target1_angle, target1_info) = player_scan(values, debug_circle)
    (target2_type, target2_distance, target2_angle, target2_info) = weapon_scan(values, debug_circle)

    if not get_if_have_weapon():
        if target1_type == types["player"] and target1_info[1]:
            next_state = "c_move"
        else:
            next_state = "w_move"

    if target1_type != types["player"]:
        next_state = "a_move"

    if target1_type == types["player"] and get_current_status() <= 50 and target1_info[1]:
        next_state = "c_move"

    rot_cc = 0
    rot_cw = 0
    dx = 0
    dy = 0
    debug_line = ()
    fire = False
    if target1_type == types["player"]:
        throw = get_throwing_angle()
        delta = ((target1_angle - throw) + 360) % 360

        if delta > 180:
            rot_cc = 0
            rot_cw = 1
        else:
            rot_cc = 1
            rot_cw = 0

        player_angle = target1_info[2]
        behind_vector = vector_to_components(good_dist, invert_angle(player_angle))

        player_to_behind_vector = (
            behind_vector[0] + target1_distance[0],
            behind_vector[1] + target1_distance[1],
        )

        s = max(abs(player_to_behind_vector[0]), abs(player_to_behind_vector[1]))

        dx = float(player_to_behind_vector[0]) / s
        dy = float(player_to_behind_vector[1]) / s

        debug_line = (
            int(position[0]),
            int(position[1]),
            int(position[0] + player_to_behind_vector[0]),
            int(position[1] + player_to_behind_vector[1]),
        )

        if (delta < 1 or delta > 359) and abs(target1_distance[0] ** 2 + target1_distance[1] ** 2) < e_range ** 2:
            fire = True
            if target1_info[1]:
                next_state = "c_move"
            else:
                next_state = "w_move"

    (danger, target3_type, target3_distance, target3_angle) = danger_scan(position, get_velocity_tuple())
    if danger:
        next_state = "a_avoid"

    state_dict = create_state_dict(position, dx, dy, rot_cc, rot_cw, "go_behind", target1_type, target1_distance,
                                  target1_angle, target2_type, target2_distance, target2_angle, target3_type,
                                  target3_distance, target3_angle, debug_circle)
    state_dict["DEBUGS"].append(debug_line)

    if fire:
        state_dict["WEAPON"] = False

    return next_state, state_dict

###### Avoid Functions ######
# The first 3 functions are just there to call the main one with the state
# of the avoid being called, just so when it needs a state to return to
# afterwards, it can do that with no issues.

def w_avoid():
    return avoids("w_")

def c_avoid():
    return avoids("c_")

def a_avoid():
    return avoids("a_")

def avoids(state):

    position = get_position_tuple()
    values = get_my_stored_data()
    next_state = state + "avoid"

    debug_circle = []
    (target1_type, target1_distance, target1_angle, target1_info) = player_scan(values, debug_circle)
    (target2_type, target2_distance, target2_angle, _) = weapon_scan(values, debug_circle)

    target3_type = "\x00"
    target3_angle = 0

    if values[5] != "\x00\x00" and values[6] != "\x00\x00":
        target3_type = values[5][:1]
        target3_angle = ord(values[5][1:])

    dx = 0
    dy = 0
    if target3_type != "\x00":
        target_angle = invert_angle(target3_angle)

        dx = cos(radians(target_angle))
        dy = sin(radians(target_angle))

    (danger, target3_type, target3_distance, target3_angle) = danger_scan(position, get_velocity_tuple())
    if not danger:
        next_state = state + reverse_states[values[0]]

    return next_state, create_state_dict(position, dx, dy, 0, 0, reverse_states[values[0]], target1_type,
                                        target1_distance, target1_angle, target2_type, target2_distance, target2_angle,
                                        target3_type, target3_distance, target3_angle, debug_circle)

###### Scan Functions ######
# Scans the area around the last known location to find a target. 
# It uses 2 checks, it'll check the last known location and follow 
# if there is nothing in the way, then it'll scan in a random quadrant for the target.

def player_scan(values, debug_circles):

    target_type = "\x00"
    target_distance = (0, 0)
    target_angle = 0
    target_info = 0

    if values[1] != "\x00\x00" and values[2] != "\x00\x00":
        target_type = values[1][:1]
        target_angle = ord(values[1][1:])
        target_distance = (
            ord(values[2][:1]) - arena_dimensions[0],
            ord(values[2][1:]) - arena_dimensions[1],
        )

    if target_type == types["player"]:
        debug_circles.append((target_distance, scans))

        found = False
        for angle in angle_range(target_angle, scans):
            (entity_type, distance, info) = get_the_radar_data(angle)

            if entity_type == "player":
                found = True
                target_type = types[entity_type]
                target_distance = vector_to_components(distance, angle)
                target_angle = angle
                target_info = info
                break

        if not found:
            target_type = "\x00"
            target_distance = (0, 0)
            target_angle = 0

    if not target_type == types["player"]:
        for angle in range(0, 359):
            (entity_type, distance, info) = get_the_radar_data(angle)

            if entity_type == "player":
                target_type = types[entity_type]
                target_distance = vector_to_components(distance, angle)
                target_angle = angle
                target_info = info
                break

    return target_type, target_distance, target_angle, target_info

def weapon_scan(values, debug_circles):

    target_type = "\x00"
    target_distance = (0, 0)
    target_angle = 0
    target_info = 0

    if values[3] != "\x00\x00" and values[4] != "\x00\x00":
        target_type = values[3][:1]
        target_angle = ord(values[3][1:])
        target_distance = (
            ord(values[4][:1]) - arena_dimensions[0],
            ord(values[4][1:]) - arena_dimensions[1],
        )

    if get_if_have_weapon():
        return target_type, target_distance, target_angle, target_info

    if target_type == types["weapon"]:
        debug_circles.append((target_distance, scans))

        found = False
        for angle in angle_range(target_angle, scans):
            (entity_type, distance, info) = get_the_radar_data(angle)

            if entity_type == "weapon" and not info:
                dist = vector_to_components(distance, angle)
                pos = get_position_tuple()
                if (pos[0] + dist[0]) < 700:
                    if (pos[1] + dist[1]) < 700:
                        found = True
                        target_type = types[entity_type]
                        target_distance = vector_to_components(distance, angle)
                        target_angle = angle
                        target_info = info
                        break

        if not found:
            target_type = "\x00"
            target_distance = (0, 0)
            target_angle = 0

    if not target_type == types["weapon"]:
        info_for_return = None
        for angle in range(0, 359):
            (entity_type, distance, info) = get_the_radar_data(angle)
            distance_compo = vector_to_components(distance, angle)

            if info_for_return is None and entity_type == "weapon" and not info:
                info_for_return = (entity_type, distance_compo, angle, info)
            elif info_for_return is not None and entity_type == "weapon" and compare_distance(distance_compo, info_for_return[1]) and not info:
                info_for_return = (entity_type, distance_compo, angle, info)

        if info_for_return is not None and info_for_return[0] == "weapon":
            target_type = types[info_for_return[0]]
            target_distance = info_for_return[1]
            target_angle = info_for_return[2]
            target_info = info_for_return[3]

    return target_type, target_distance, target_angle, target_info

def column_scan(values, debug_circles):

    target_type = "\x00"
    target_distance = (0, 0)
    target_angle = 0
    target_info = 0

    if values[3] != "\x00\x00" and values[4] != "\x00\x00":
        target_type = values[3][:1]
        target_angle = ord(values[3][1:])
        target_distance = (
            ord(values[4][:1]) - arena_dimensions[0],
            ord(values[4][1:]) - arena_dimensions[1],
        )

    if target_type == types["column"]:
        debug_circles.append((target_distance, scans))

        found = False
        for angle in angle_range(target_angle, scans):
            (entity_type, distance, info) = get_the_radar_data(angle)

            if entity_type == "column":
                found = True
                target_type = types[entity_type]
                target_distance = vector_to_components(distance, angle)
                target_angle = angle
                target_info = info
                break

        if not found:
            target_type = "\x00"
            target_distance = (0, 0)
            target_angle = 0

    if not target_type == types["column"]:
        info_for_return = None
        for angle in range(0, 359):
            (entity_type, distance, info) = get_the_radar_data(angle)
            distance_compo = vector_to_components(distance, angle)

            if info_for_return is None and entity_type == "column":
                info_for_return = (entity_type, distance_compo, angle, info)
            elif info_for_return is not None and entity_type == "column" and compare_distance(distance_compo, info_for_return[1]):
                info_for_return = (entity_type, distance_compo, angle, info)

        if info_for_return is not None and info_for_return[0] == "column":
            target_type = types[info_for_return[0]]
            target_distance = info_for_return[1]
            target_angle = info_for_return[2]
            target_info = info_for_return[3]

    return target_type, target_distance, target_angle, target_info

def danger_scan(position, velocity):

    if position[0] - good_dist < 0:
        return True, types["wall"], (0 - position[0], 0), 180
    if position[0] + good_dist > arena_dimensions[0]:
        return True, types["wall"], (arena_dimensions[0] - position[0], 0), 0
    if position[1] - good_dist < 0:
        return True, types["wall"], (0, 0 - position[1]), 270
    if position[1] + good_dist > arena_dimensions[1]:
        return True, types["wall"], (0, arena_dimensions[1] - position[1]), 90

    agent_angle = int(degrees(atan2(velocity[1], velocity[0])))

    for angle in angle_range(agent_angle, scans):
        (entity_type, distance, info) = get_the_radar_data(angle)

        if (entity_type == "player" or entity_type == "column" or entity_type == "hazard") and distance < good_dist:
            return True, types[entity_type], vector_to_components(distance, angle), angle

        if entity_type == "weapon" and distance < good_dist and info:
            return True, types[entity_type], vector_to_components(distance, angle), angle

    return False, "\x00", (0, 0), 0

###### Helpful Functions ######
# Used for things that would require tons of repeating and extra lines in the main functions
# Creating the state dictionary for instructions, angle range, figuring out x and y components
# and comparing distances

def create_state_dict(position, dx, dy, rot_cc, rot_cw, state, target1_type, target1_distance, target1_angle,
                     target2_type, target2_distance, target2_angle, target3_type, target3_distance, target3_angle,
                     debug_circles):

    target1_distance1_char = "0"
    target1_distance2_char = "0"
    target1_angle_char = "0"
    try:
        target1_distance1_char = chr(int(arena_dimensions[0] + target1_distance[0]))
        target1_distance2_char = chr(int(arena_dimensions[1] + target1_distance[1]))
        target1_angle_char = chr(int(abs(target1_angle)))
    except ValueError:
        print("[ERROR] Bad data given to CHAR for TAR_1_DIST")

    target2_distance1_char = "0"
    target2_distance2_char = "0"
    target2_angle_char = "0"
    try:
        target2_distance1_char = chr(int(arena_dimensions[0] + target2_distance[0]))
        target2_distance2_char = chr(int(arena_dimensions[1] + target2_distance[1]))
        target2_angle_char = chr(int(abs(target2_angle)))
    except ValueError:
        print("[ERROR] Bad data given to CHAR for TAR_2_DIST")

    target3_distance1_char = "0"
    target3_distance2_char = "0"
    target3_angle_char = "0"
    try:
        target3_distance1_char = chr(int(arena_dimensions[0] + target3_distance[0]))
        target3_distance2_char = chr(int(arena_dimensions[1] + target3_distance[1]))
        target3_angle_char = chr(int(abs(target3_angle)))
    except ValueError:
        print("[ERROR] Bad data given to CHAR for TAR_3_DIST")

    debug = [
        (
            int(position[0]),
            int(position[1]),
            int(target1_distance[0] + position[0]),
            int(target1_distance[1] + position[1]),
        ),
        (
            int(position[0]),
            int(position[1]),
            int(target2_distance[0] + position[0]),
            int(target2_distance[1] + position[1])
        ),
        (
            int(position[0]),
            int(position[1]),
            int(target3_distance[0] + position[0]),
            int(target3_distance[1] + position[1])
        ),
    ]

    for circle in debug_circles:
        debug.append((
            int(circle[0][0] + position[0]),
            int(circle[0][1] + position[1]),
            int(circle[1]),
        ))

    if (dx > 1) or (dx < -1):
        print("(aclt_x error) coming from: " + state)
    if (dy > 1) or (dy < -1):
        print("(aclt_y error) coming from: " + state)
    return {
        'ACLT_X': dx,
        'ACLT_Y': dy,
        'ROT_CC': rot_cc,
        'ROT_CW': rot_cw,
        'SAVE_A': states[state],
        'SAVE_B': target1_type + target1_angle_char,
        'SAVE_C': target1_distance1_char + target1_distance2_char,
        'SAVE_D': target2_type + target2_angle_char,
        'SAVE_E': target2_distance1_char + target2_distance2_char,
        'SAVE_F': target3_type + target3_angle_char,
        'SAVE_X': target3_distance1_char + target3_distance2_char,
        'DEBUGS': debug
    }


def angle_range(angle, wanted_range):
    got_range = []
    for i in range(angle - wanted_range // 2, angle + wanted_range // 2, 1):
        got_range.append(i if angle > 0 else 359 - i)
    return got_range


def invert_angle(angle):
    new_angle = angle - 180
    if new_angle < 0:
        new_angle = 359 + new_angle
    return new_angle


def vector_to_components(dist, angle):
    return(
        dist * cos(radians(angle)),
        dist * sin(radians(angle)),
    )


def compare_distance(dist1, dist2):
    return (dist1[0] ** 2 + dist1[1] ** 2) <= (dist2[0] ** 2 + dist2[1] ** 2)