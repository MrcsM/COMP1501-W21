import random
import time
import pygame
import math
import ast
import sys
import os
import zipfile

from pygame.locals import *

# ================================================================================

STATE_TITLE = 0
STATE_START = 1
STATE_MATCH = 2
STATE_FINAL = 3

PLAYER_LIST_INDEX = 0
COLUMN_LIST_INDEX = 1
HAZARD_LIST_INDEX = 2
WEAPON_LIST_INDEX = 3
DEBRIS_LIST_INDEX = 4

COLUMN_RADIUS = 21 #20
HAZARD_RADIUS = 30
WEAPON_RADIUS = 5
PLAYER_RADIUS = 11 #10

COLOUR_WHT = (255, 255, 255)
COLOUR_DIM = (127, 127, 127)
COLOUR_OFF = (  1,   1,   1)
COLOUR_BLK = (  0,   0,   0)
COLOUR_ERR = (255,   0,   0)
COLOUR_BLU = (159, 191, 255)

register_key_value = ["SAVE_A", "SAVE_B", "SAVE_C", "SAVE_D", "SAVE_E", "SAVE_F", "SAVE_X", "SAVE_Y"]

maximum_speed = 5

maximum_health_bar_width = 50

maximum_collision_damage = 20

frame_rate = 30

maximum_match_duration = 5 * 60 * frame_rate
current_match_duration = 0

# the number of columns, hazards, and weapons cannot be changed without altering the nature of the "shared memory"
number_of_columns = 4
number_of_hazards = 3
number_of_weapons = 6

# generate a random number to append to the names of the functions provided
random_header = str(random.randint(100000, 999999))

# set the dimensions of the window and the arena
window_size = (1366,  768)
arena_dimens = ( 750,  750)
arena_offset = (   9,    9)

# because line width will be 3, decrease left/top by 1 and increase dim by 4
game_arena_rect = (  7,   7, 754, 754) 
upper_view_rect = (769,   7, 590, 373)
lower_view_rect = (769, 388, 590, 373)

# create surfaces for the sprites
splash_sprite = pygame.Surface((1131, 369))
player_sprite = pygame.Surface((21, 21))
column_sprite = pygame.Surface((40, 40))
hazard_sprite = pygame.Surface((61, 61))
weapon_sprite = pygame.Surface((11, 11))
onion1_sprite = pygame.Surface((11, 11))
onion2_sprite = pygame.Surface((11, 11))

# create surfaces for the visual effects
fx_fade_surf = pygame.Surface((1131, 369))

# create the caption surfaces for each player
caption_for_player_0 = pygame.Surface((10, 10))
caption_for_player_0.fill((255, 0, 0))
caption_for_player_1 = pygame.Surface((10, 10))
caption_for_player_1.fill((255, 0, 0))

# create the surface for clearing all but the green channel
channel_g = pygame.Surface((window_size[0], window_size[1]))
channel_g.fill(pygame.Color(255, 0, 255))

# create the surface for clearing all but the red and green channels
channel_y = pygame.Surface((window_size[0], window_size[1]))
channel_y.fill(pygame.Color(127, 127, 255))

# create the surface for achieving the scan line effect 
scan_line = pygame.Surface((window_size[0], window_size[1]))
scan_line.fill(pygame.Color(207, 207, 207))
for i in range(0, window_size[1], 2):
	pygame.draw.line(scan_line, pygame.Color(255, 255, 255), (0, i), (window_size[0] - 1, i))

# ================================================================================


class Entity:

	def __init__(self, x, y):
		self.x = x
		self.y = y
		
class Column(Entity):

	def __init__(self, x, y):
		Entity.__init__(self, x, y)

class Hazard(Entity):

	def __init__(self, x, y):
		Entity.__init__(self, x, y)

class Mobile(Entity):

	def __init__(self, x, y, dx, dy):
		Entity.__init__(self, x, y)
		self.dx = dx
		self.dy = dy

class Weapon(Mobile):

	def __init__(self, x, y):
	
		#x = random.randint(1, 10)
		#y = random.randint(1, 10)
		random_angle = random.randint(0, 359)
		initial_speed = random.randint(1, 5)
		Mobile.__init__(self, x, y, math.cos(math.radians(random_angle)) * initial_speed, math.sin(math.radians(random_angle)) * initial_speed)
		self.px = 0
		self.py = 0
		self.ppx = 0
		self.ppy = 0
		self.currently_held_by = -1
		self.moving_fast_enough_to_damage = False
		
class Debris(Mobile):

	def __init__(self, x, y, angle):
	
		self.timer = random.randint(10, 40)
		initial_speed = random.randint(1, 5)
		Mobile.__init__(self, x, y, math.cos(math.radians(angle)) * initial_speed, math.sin(math.radians(angle)) * initial_speed)
		

class Player(Mobile):

	def __init__(self, id, x, y, angle):
		Mobile.__init__(self, x, y, 0, 0)
		self.id = id
		self.ddx = 0
		self.ddy = 0		
		self.current_status = 100
		self.trying_for_a_weapon = False
		self.holding_onto_weapon = -1
		self.throwing_angle = angle
		self.function_state = "start"
		self.storage_memory = [chr(0) + chr(0) for i in range(8)]
		self.waiting_period = 0
		self.register_dictionary = {}
		self.is_falling_into_hazard = -1
		
		
# ================================================================================
		
		
def create_backgd_surface():

	# create the surface
	backgd_surf = pygame.Surface(window_size)
	
	# fil it with the background colour
	backgd_surf.fill(pygame.Color('black'))

	# draw the vertical gridlines
	for col in range(8, 750, 15):
		pygame.draw.line(backgd_surf, COLOUR_DIM, (col + game_arena_rect[0] + 1, game_arena_rect[1]), (col + game_arena_rect[0] + 1, game_arena_rect[1] + game_arena_rect[3]), 1)

	# draw the horizontal gridlines
	for row in range(8, 750, 15):
		pygame.draw.line(backgd_surf, COLOUR_DIM, (game_arena_rect[0], row + game_arena_rect[1] + 1), (game_arena_rect[0] + game_arena_rect[2], row + game_arena_rect[1] + 1), 1)
	
	# return the surface
	return backgd_surf

	
def create_foregd_surface():

	# create the surface
	foregd_surf = pygame.Surface(window_size)
	
	# fill it with the background colour
	foregd_surf.fill(COLOUR_BLK)

	# blit the finite state machine graphs
	if not player_0_fsm_hidden:		
		foregd_surf.blit(player_0_fsm_graph[0], (upper_view_rect[0], upper_view_rect[1]))
	else:
		foregd_surf.blit(special_text_QMARK, (upper_view_rect[0] + upper_view_rect[2] // 2 - (special_text_QMARK.get_width() // 2) , upper_view_rect[1] + upper_view_rect[3] // 2 - (special_text_QMARK.get_height() // 2))	)
	if not player_1_fsm_hidden:		
		foregd_surf.blit(player_1_fsm_graph[0], (lower_view_rect[0], lower_view_rect[1]))
	else:
		foregd_surf.blit(special_text_QMARK, (lower_view_rect[0] + lower_view_rect[2] // 2 - (special_text_QMARK.get_width() // 2) , lower_view_rect[1] + lower_view_rect[3] // 2 - (special_text_QMARK.get_height() // 2))	)
	
	# draw the interface borders
	pygame.draw.rect(foregd_surf, COLOUR_WHT, game_arena_rect, 3)
	pygame.draw.rect(foregd_surf, COLOUR_WHT, upper_view_rect, 3)
	pygame.draw.rect(foregd_surf, COLOUR_WHT, lower_view_rect, 3)

	# set the transparency colour
	foregd_surf.set_colorkey(COLOUR_BLK)
	
	# return the surface
	return foregd_surf	

	
def create_an_fsm_graph(file_data):

	try:
		
		syntax_tree = ast.parse(file_data)

		fsm_adjacency_list = {}

		graph_node_index = 0
		for func in ast.walk(syntax_tree):
			if isinstance(func, ast.FunctionDef):
				valid_state_function = True
				possible_transitions = []
				for node in func.body:
					for part in ast.walk(node):
						if isinstance(part, ast.Return):
							if isinstance(part.value, ast.Tuple) and len(part.value.elts) == 2 and isinstance(part.value.elts[0], ast.Str) and isinstance(part.value.elts[1], ast.Dict):
								if part.value.elts[0].s not in possible_transitions:
									possible_transitions.append(part.value.elts[0].s)
							else:
								valid_state_function = False

				if valid_state_function and len(possible_transitions) > 0:
					fsm_adjacency_list[func.name] = (possible_transitions, graph_node_index)
					graph_node_index += 1

		wide = 590
		high = 373

		node_radius = 15
		hexagon_dim = 80
		start_angle = 0
		layer_count = 0

		viewer_surf = pygame.Surface( (wide, high) )

		x_of_center = 0
		y_of_center = 0

		num_required_nodes = len(fsm_adjacency_list)
		hexagonal_vertices = [ (x_of_center, y_of_center) ]
		computed_positions = []

		while len(computed_positions) < num_required_nodes:
			if len(hexagonal_vertices) == 0:
				layer_count += 1
				hexagonal_vertices.append( (int(x_of_center + math.cos(math.radians(start_angle +   0)) * layer_count * hexagon_dim), int(y_of_center + math.sin(math.radians(start_angle +   0)) * layer_count * hexagon_dim)) )
				hexagonal_vertices.append( (int(x_of_center + math.cos(math.radians(start_angle + 120)) * layer_count * hexagon_dim), int(y_of_center + math.sin(math.radians(start_angle + 120)) * layer_count * hexagon_dim)) )
				hexagonal_vertices.append( (int(x_of_center + math.cos(math.radians(start_angle + 240)) * layer_count * hexagon_dim), int(y_of_center + math.sin(math.radians(start_angle + 240)) * layer_count * hexagon_dim)) )
				hexagonal_vertices.append( (int(x_of_center + math.cos(math.radians(start_angle + 300)) * layer_count * hexagon_dim), int(y_of_center + math.sin(math.radians(start_angle + 300)) * layer_count * hexagon_dim)) )
				hexagonal_vertices.append( (int(x_of_center + math.cos(math.radians(start_angle +  60)) * layer_count * hexagon_dim), int(y_of_center + math.sin(math.radians(start_angle +  60)) * layer_count * hexagon_dim)) )
				hexagonal_vertices.append( (int(x_of_center + math.cos(math.radians(start_angle + 180)) * layer_count * hexagon_dim), int(y_of_center + math.sin(math.radians(start_angle + 180)) * layer_count * hexagon_dim)) )
				if start_angle == 0:
					start_angle = 150
				else:
					start_angle = 0
			computed_positions.append(hexagonal_vertices.pop())

		square_side = 2 * hexagon_dim * (layer_count + 1)

		viewer_surf.fill((0,0,0))

		for key in fsm_adjacency_list:
			
			x = int(wide * (computed_positions[fsm_adjacency_list[key][1]][0] + square_side / 2) / square_side)
			y = int(high * (computed_positions[fsm_adjacency_list[key][1]][1] + square_side / 2) / square_side)
			
			for transition in fsm_adjacency_list[key][0]:
				a = int(wide * (computed_positions[fsm_adjacency_list[transition][1]][0] + square_side / 2) / square_side)
				b = int(high * (computed_positions[fsm_adjacency_list[transition][1]][1] + square_side / 2) / square_side)
				pygame.draw.line(viewer_surf, COLOUR_DIM, (x, y), (a, b), 2)

		dictionary_for_highlighting = {}

		for key in fsm_adjacency_list:

			node_caption = small_font.render(key, False, COLOUR_WHT)

			x = int(wide * (computed_positions[fsm_adjacency_list[key][1]][0] + square_side / 2) / square_side)
			y = int(high * (computed_positions[fsm_adjacency_list[key][1]][1] + square_side / 2) / square_side)
				
			pygame.draw.circle(viewer_surf, COLOUR_BLK, (x, y), node_radius)
			pygame.draw.circle(viewer_surf, COLOUR_DIM, (x, y), node_radius, 2)
			viewer_surf.blit(node_caption, (x - (node_caption.get_width() // 2), y + 25 - (node_caption.get_height() // 2)))

			dictionary_for_highlighting[key] = (x, y)
		
		return viewer_surf, dictionary_for_highlighting
		
	except:
	
		return pygame.Surface((1, 1)), {}


def initialize_game_objects():
	
	# initialize the player list
	player_list = []

	# determine the components of a random vector centered in the arena
	random_angle = random.randint(0, 359)
	initial_x = arena_dimens[0] * 0.5 * 0.7 * math.cos(math.radians(random_angle))
	initial_y = arena_dimens[1] * 0.5 * 0.7 * math.sin(math.radians(random_angle))
	
	# place the two players on opposing sides, facing away from each other
	player_list.append(Player(0, arena_dimens[0]/2 + initial_x, arena_dimens[1]/2 + initial_y, random_angle))
	player_list.append(Player(1, arena_dimens[0]/2 - initial_x, arena_dimens[1]/2 - initial_y, ((random_angle + 180) % 360)))

	# initialize the column list
	column_list = []

	# create an empty list to track which columns are placed
	placed_columns = []
	
	# place columns at random positions
	for i in range(number_of_columns):
	
		# ensure that the random column position selected was not already used
		random_angle = random.randint(0, 17) * 20
		while random_angle in placed_columns:
			random_angle = random.randint(0, 17) * 20
		
		# record each column placed
		placed_columns.append(random_angle)
		
		# determine the components of a random vector centered in the arena
		initial_x = arena_dimens[0] * 0.5 * 0.5 * math.cos(math.radians(random_angle))
		initial_y = arena_dimens[1] * 0.5 * 0.5 * math.sin(math.radians(random_angle))
		
		# place the column
		column_list.append(Column(arena_dimens[0]/2 + initial_x, arena_dimens[1]/2 + initial_y))
	
	# initialize the hazard list
	hazard_list = []

	# select three of the four corners to receive hazards
	permutation = [1, 2, 3, 4]
	random.shuffle(permutation)
	while len(permutation) > number_of_hazards:
		permutation.pop(0)
	
	# randomly place a hazard in the top left (if that region was selected)
	if 1 in permutation:
		initial_x = random.randint(3, 6) * 15 + 7
		initial_y = random.randint(3, 6) * 15 + 7
		hazard_list.append(Hazard(initial_x, initial_y))
		
	# randomly place a hazard in the top right (if that region was selected)
	if 2 in permutation:
		initial_x = 735 - random.randint(3, 6) * 15 + 7
		initial_y = random.randint(3, 6) * 15 + 7
		hazard_list.append(Hazard(initial_x, initial_y))
		
	# randomly place a hazard in the bottom right (if that region was selected)
	if 3 in permutation:
		initial_x = 735 - random.randint(3, 6) * 15 + 7
		initial_y = 735 - random.randint(3, 6) * 15 + 7
		hazard_list.append(Hazard(initial_x, initial_y))
		
	# randomly place a hazard in the bottom left (if that region was selected)
	if 4 in permutation:
		initial_x = random.randint(3, 6) * 15 + 7
		initial_y = 735 - random.randint(3, 6) * 15 + 7
		hazard_list.append(Hazard(initial_x, initial_y))	
		
	# initialize the weapon list
	weapon_list = []
	
	# place six
	for i in range(number_of_weapons):
	
		random_angle = random.randint(0, 359)
		
		initial_x = arena_dimens[0] * 0.5 * 0.3 * math.cos(math.radians(random_angle))
		initial_y = arena_dimens[1] * 0.5 * 0.3 * math.sin(math.radians(random_angle))
	
		weapon_list.append(Weapon(arena_dimens[0]/2 + initial_x, arena_dimens[1]/2 + initial_y))	
	
	object_list = []
	object_list.insert(PLAYER_LIST_INDEX, player_list)
	object_list.insert(COLUMN_LIST_INDEX, column_list)
	object_list.insert(HAZARD_LIST_INDEX, hazard_list)
	object_list.insert(WEAPON_LIST_INDEX, weapon_list)
	object_list.insert(DEBRIS_LIST_INDEX, [])
	
	return object_list

	
def update_compressed_environment_data(object_list, current_player_id):

	other_id = 1 - current_player_id
	
	compressed_environment_data[ 1] = object_list[PLAYER_LIST_INDEX][current_player_id].x
	compressed_environment_data[ 2] = object_list[PLAYER_LIST_INDEX][current_player_id].y
	compressed_environment_data[ 3] = object_list[PLAYER_LIST_INDEX][current_player_id].dx
	compressed_environment_data[ 4] = object_list[PLAYER_LIST_INDEX][current_player_id].dy				
	compressed_environment_data[ 5] = object_list[PLAYER_LIST_INDEX][current_player_id].current_status
	compressed_environment_data[ 6] = object_list[PLAYER_LIST_INDEX][current_player_id].holding_onto_weapon
	compressed_environment_data[ 7] = object_list[PLAYER_LIST_INDEX][current_player_id].storage_memory
	compressed_environment_data[ 8] = object_list[PLAYER_LIST_INDEX][current_player_id].throwing_angle
	
	compressed_environment_data[ 9] = object_list[PLAYER_LIST_INDEX][other_id].x
	compressed_environment_data[10] = object_list[PLAYER_LIST_INDEX][other_id].y
	compressed_environment_data[11] = object_list[PLAYER_LIST_INDEX][other_id].current_status
	compressed_environment_data[12] = object_list[PLAYER_LIST_INDEX][other_id].holding_onto_weapon
	compressed_environment_data[13] = object_list[PLAYER_LIST_INDEX][other_id].throwing_angle
	
	compressed_environment_data[14] = pygame.time.get_ticks()
	
	compressed_environment_data[15] = object_list[COLUMN_LIST_INDEX][0].x
	compressed_environment_data[16] = object_list[COLUMN_LIST_INDEX][0].y
	compressed_environment_data[17] = object_list[COLUMN_LIST_INDEX][1].x
	compressed_environment_data[18] = object_list[COLUMN_LIST_INDEX][1].y
	compressed_environment_data[19] = object_list[COLUMN_LIST_INDEX][2].x
	compressed_environment_data[20] = object_list[COLUMN_LIST_INDEX][2].y
	compressed_environment_data[21] = object_list[COLUMN_LIST_INDEX][3].x
	compressed_environment_data[22] = object_list[COLUMN_LIST_INDEX][3].y
	
	compressed_environment_data[23] = object_list[HAZARD_LIST_INDEX][0].x
	compressed_environment_data[24] = object_list[HAZARD_LIST_INDEX][0].y
	compressed_environment_data[25] = object_list[HAZARD_LIST_INDEX][1].x
	compressed_environment_data[26] = object_list[HAZARD_LIST_INDEX][1].y
	compressed_environment_data[27] = object_list[HAZARD_LIST_INDEX][2].x
	compressed_environment_data[28] = object_list[HAZARD_LIST_INDEX][2].y
	
	if object_list[WEAPON_LIST_INDEX][0].currently_held_by == -1:
		compressed_environment_data[29] = object_list[WEAPON_LIST_INDEX][0].x
		compressed_environment_data[30] = object_list[WEAPON_LIST_INDEX][0].y
		compressed_environment_data[31] = object_list[WEAPON_LIST_INDEX][0].moving_fast_enough_to_damage
	else:
		compressed_environment_data[29] = -999
		compressed_environment_data[30] = -999
		compressed_environment_data[31] = False

	if object_list[WEAPON_LIST_INDEX][1].currently_held_by == -1:
		compressed_environment_data[32] = object_list[WEAPON_LIST_INDEX][1].x
		compressed_environment_data[33] = object_list[WEAPON_LIST_INDEX][1].y
		compressed_environment_data[34] = object_list[WEAPON_LIST_INDEX][1].moving_fast_enough_to_damage
	else:
		compressed_environment_data[32] = -999
		compressed_environment_data[33] = -999
		compressed_environment_data[34] = False

	if object_list[WEAPON_LIST_INDEX][2].currently_held_by == -1:
		compressed_environment_data[35] = object_list[WEAPON_LIST_INDEX][2].x
		compressed_environment_data[36] = object_list[WEAPON_LIST_INDEX][2].y
		compressed_environment_data[37] = object_list[WEAPON_LIST_INDEX][2].moving_fast_enough_to_damage
	else:
		compressed_environment_data[35] = -999
		compressed_environment_data[36] = -999
		compressed_environment_data[37] = False

	if object_list[WEAPON_LIST_INDEX][3].currently_held_by == -1:
		compressed_environment_data[38] = object_list[WEAPON_LIST_INDEX][3].x
		compressed_environment_data[39] = object_list[WEAPON_LIST_INDEX][3].y
		compressed_environment_data[40] = object_list[WEAPON_LIST_INDEX][3].moving_fast_enough_to_damage
	else:
		compressed_environment_data[38] = -999
		compressed_environment_data[39] = -999
		compressed_environment_data[40] = False

	if object_list[WEAPON_LIST_INDEX][4].currently_held_by == -1:
		compressed_environment_data[41] = object_list[WEAPON_LIST_INDEX][4].x
		compressed_environment_data[42] = object_list[WEAPON_LIST_INDEX][4].y
		compressed_environment_data[43] = object_list[WEAPON_LIST_INDEX][4].moving_fast_enough_to_damage
	else:
		compressed_environment_data[41] = -999
		compressed_environment_data[42] = -999
		compressed_environment_data[43] = False

	if object_list[WEAPON_LIST_INDEX][5].currently_held_by == -1:
		compressed_environment_data[44] = object_list[WEAPON_LIST_INDEX][5].x
		compressed_environment_data[45] = object_list[WEAPON_LIST_INDEX][5].y
		compressed_environment_data[46] = object_list[WEAPON_LIST_INDEX][5].moving_fast_enough_to_damage
	else:
		compressed_environment_data[44] = -999
		compressed_environment_data[45] = -999
		compressed_environment_data[46] = False
	
	compressed_environment_data[47] = current_match_duration
	compressed_environment_data[48] = 0
	
	
def process_register_dictionary(object_list, id):

	global debug_elements_to_draw
	
	register_dictionary = object_list[PLAYER_LIST_INDEX][id].register_dictionary
	
	if "ACLT_X" in register_dictionary:
		register_value = register_dictionary["ACLT_X"]
		if (isinstance(register_value, int) or isinstance(register_value, float)) and -1 <= register_value <= 1:
			object_list[PLAYER_LIST_INDEX][id].ddx = register_value
		else:
			print("the value being sent to ACLT_X in player " + str(id) + " was invalid")
			print(type(register_value), register_value)
			
	if "ACLT_Y" in register_dictionary:
		register_value = register_dictionary["ACLT_Y"]
		if (isinstance(register_value, int) or isinstance(register_value, float)) and -1 <= register_value <= 1:
			object_list[PLAYER_LIST_INDEX][id].ddy = register_value
		else:
			print("the value being sent to ACLT_Y in player " + str(id) + " was invalid")
			
	if "ROT_CC" in register_dictionary:
		register_value = register_dictionary["ROT_CC"]
		if (isinstance(register_value, int) or isinstance(register_value, float)) and 0 <= register_value <= 1:
			object_list[PLAYER_LIST_INDEX][id].throwing_angle += (3 * register_value)
		else:
			print("the value being sent to ROT_CC in player " + str(id) + " was invalid")						
			
	if "ROT_CW" in register_dictionary:
		register_value = register_dictionary["ROT_CW"]
		if (isinstance(register_value, int) or isinstance(register_value, float)) and 0 <= register_value <= 1:
			object_list[PLAYER_LIST_INDEX][id].throwing_angle -= (3 * register_value)
		else:
			print("the value being sent to ROT_CW in player " + str(id) + " was invalid")			

	if "WEAPON" in register_dictionary:
		register_value = register_dictionary["WEAPON"]
		if (isinstance(register_value, bool)):
		
			# if weapon is set to True and the player is not holding a weapon, then it means the player is trying for a weapon
			if register_value == True and object_list[PLAYER_LIST_INDEX][id].holding_onto_weapon == -1:

				object_list[PLAYER_LIST_INDEX][id].trying_for_a_weapon = True
				
			# if weapon is set to False and the player is holding a weapon, then it means the player is throwing the weapon
			elif register_value == False and object_list[PLAYER_LIST_INDEX][id].holding_onto_weapon != -1:

				the_player = object_list[PLAYER_LIST_INDEX][id]
				the_weapon = object_list[WEAPON_LIST_INDEX][the_player.holding_onto_weapon]

				# release the weapon
				the_player.holding_onto_weapon = -1

				# give the weapon an initial velocity
				initial_speed = 14
				the_weapon.currently_held_by = -1
				the_weapon.dx = the_player.dx + math.cos(math.radians(the_player.throwing_angle)) * initial_speed
				the_weapon.dy = the_player.dy + math.sin(math.radians(the_player.throwing_angle)) * initial_speed
				
				# move the weapon away from the player that has thrown it until they are no longer in collision
				distance_squared = ((the_weapon.x - the_player.x) ** 2 + (the_weapon.y - the_player.y) ** 2)
				while distance_squared < (WEAPON_RADIUS + PLAYER_RADIUS) ** 2:
					the_weapon.x += (the_weapon.dx * 0.205)
					the_weapon.y += (the_weapon.dy * 0.205)
					distance_squared = ((the_weapon.x - the_player.x) ** 2 + (the_weapon.y - the_player.y) ** 2)
	
	for register_key_index in range(8):
		if register_key_value[register_key_index] in register_dictionary:
			register_value = register_dictionary[register_key_value[register_key_index]]
			if isinstance(register_value, str) and len(register_value) == 2:
				object_list[PLAYER_LIST_INDEX][id].storage_memory[register_key_index] = register_value
			else:
				print("the value being sent to " + register_key_value[register_key_index] + " in player " + str(id) + " was invalid")			
			
	if "DEBUGS" in register_dictionary:
		register_value = register_dictionary["DEBUGS"]
		for possible_element in register_value:
			if isinstance(possible_element, tuple):
				add_to_debug_elements = True
				for component in possible_element:
					if not isinstance(component, int):
						add_to_debug_elements = False
				if add_to_debug_elements:
					debug_elements_to_draw.append(possible_element)

def update_game_arena(object_list):

	# if the number of weapons is too low, add with probability such that expected wait is two seconds
	if len(object_list[WEAPON_LIST_INDEX]) < number_of_weapons and random.randint(1, 2 * frame_rate) == 1:
		random_angle = random.randint(0, 359)
		initial_x = arena_dimens[0] * 0.5 * 0.7 * math.cos(math.radians(random_angle))
		initial_y = arena_dimens[1] * 0.5 * 0.7 * math.sin(math.radians(random_angle))
		object_list[WEAPON_LIST_INDEX].append(Weapon(arena_dimens[0]/2 + initial_x, arena_dimens[1]/2 + initial_y))			

	# update each of the players
	for player in object_list[PLAYER_LIST_INDEX]:

		# apply thrust (if there is any)
		player.dx += player.ddx * 0.2
		player.dy += player.ddy * 0.2

		# apply drag
		player.dx *= 0.99
		player.dy *= 0.99
		
		# the magnitude of the player velocity is capped
		current_speed = (player.dx ** 2 + player.dy ** 2) ** 0.5
		if current_speed > maximum_speed:
			player.dx /= (current_speed / maximum_speed)
			player.dy /= (current_speed / maximum_speed)

		# update position relative to velocity
		player.x += player.dx
		player.y += player.dy
		
		player_collided_with_wall = False
		
		# detect and respond to collisions between the player and the arena boundaries
		if player.x - PLAYER_RADIUS < 0:
			player.dx *= -1
			player.x = 1 + PLAYER_RADIUS
			player.current_status -= abs((player.dx / maximum_speed) * maximum_collision_damage)
			player_collided_with_wall = True
			
		if player.x + PLAYER_RADIUS >= 750:
			player.dx *= -1
			player.x = 748 - PLAYER_RADIUS
			player.current_status -= abs((player.dx / maximum_speed) * maximum_collision_damage)
			player_collided_with_wall = True
			
		# detect and respond to collisions between the player and the arena boundaries
		if player.y - PLAYER_RADIUS < 0:
			player.dy *= -1
			player.y = 1 + PLAYER_RADIUS
			player.current_status -= abs((player.dy / maximum_speed) * maximum_collision_damage)
			player_collided_with_wall = True

		if player.y + PLAYER_RADIUS >= 750:
			player.dy *= -1
			player.y = 748 - PLAYER_RADIUS
			player.current_status -= abs((player.dy / maximum_speed) * maximum_collision_damage)
			player_collided_with_wall = True
			
		if player_collided_with_wall:
			for i in range(random.randint(15, 25)):
				object_list[DEBRIS_LIST_INDEX].append(Debris(player.x, player.y, random.randint(0,359)))	
				
		# detect and respond to collisions between the player and a column
		for column in object_list[COLUMN_LIST_INDEX]:
		
			distance_squared = (player.x - column.x) ** 2 + (player.y - column.y) ** 2
			
			if distance_squared < (PLAYER_RADIUS + COLUMN_RADIUS) ** 2:
			
				normal_magn = distance_squared ** 0.5
				normal_unit_x = (player.x - column.x) / normal_magn
				normal_unit_y = (player.y - column.y) / normal_magn
				dot_product = player.dx * normal_unit_x + player.dy * normal_unit_y
				reflection_x = player.dx - 2 * normal_unit_x * dot_product
				reflection_y = player.dy - 2 * normal_unit_y * dot_product

				player.dx = reflection_x
				player.dy = reflection_y

				player.current_status -= ( ((player.dx * normal_unit_x) + (player.dy * normal_unit_y)) / maximum_speed * maximum_collision_damage)
				
				for i in range(random.randint(15, 25)):
					object_list[DEBRIS_LIST_INDEX].append(Debris(player.x, player.y, random.randint(0,359)))	
				
				while distance_squared < (PLAYER_RADIUS + COLUMN_RADIUS) ** 2:
					player.x += (player.dx * 0.205)
					player.y += (player.dy * 0.205)
					distance_squared = (player.x - column.x) ** 2 + (player.y - column.y) ** 2
		
		# detect and respond to collisions between the player and a hazard
		for hazard in object_list[HAZARD_LIST_INDEX]:
		
			distance_squared = (player.x - hazard.x) ** 2 + (player.y - hazard.y) ** 2
			
			if distance_squared < (PLAYER_RADIUS + HAZARD_RADIUS) ** 2:
			
				if player.is_falling_into_hazard == -1:
				
					player.is_falling_into_hazard = 1
				
				player.dx = 3 * (hazard.x - player.x) / (distance_squared ** 0.5)
				player.dy = 3 * (hazard.y - player.y) / (distance_squared ** 0.5)

	# check for collisions between the players
	player_1 = object_list[PLAYER_LIST_INDEX][0]
	player_2 = object_list[PLAYER_LIST_INDEX][1]
	
	distance_squared = ((player_1.x - player_2.x) ** 2 + (player_1.y - player_2.y) ** 2)
	
	# respond if there has been a collision between the players
	if distance_squared < (2 * PLAYER_RADIUS) ** 2:

		normal_magn = ((player_1.x - player_2.x) ** 2 + (player_1.y - player_2.y) ** 2) ** 0.5
		normal_unit_x = (player_2.x - player_1.x) / normal_magn
		normal_unit_y = (player_2.y - player_1.y) / normal_magn
		
		angle = math.degrees(math.atan2(object_list[PLAYER_LIST_INDEX][1].y - player_1.y, object_list[PLAYER_LIST_INDEX][1].x - player_1.x)) % 360
		
		relative_speed_factor = abs(((player_1.dx - player_2.dx) * normal_unit_x) + ((player_1.dy - player_2.dy) * normal_unit_y)) / maximum_speed
		
		delta = (object_list[PLAYER_LIST_INDEX][0].throwing_angle - angle) % 360
		if delta > 180:
			delta -= 180
			
		if delta <= 90:
			crash_alignment_modifier = max(delta / 90, 0.167)
		else:
			crash_alignment_modifier = max((180 - delta) / 90, 0.167)
		
		player_1.current_status -= ( relative_speed_factor * maximum_collision_damage * crash_alignment_modifier)
	
		angle = (angle - 180) % 360
		
		delta = (object_list[PLAYER_LIST_INDEX][1].throwing_angle - angle) % 360
		if delta > 180:
			delta -= 180
			
		if delta <= 90:
			crash_alignment_modifier = max(delta / 90, 0.167)
		else:
			crash_alignment_modifier = max((180 - delta) / 90, 0.167)
		
		player_2.current_status -= ( relative_speed_factor * maximum_collision_damage * crash_alignment_modifier)

		# spawn some debris
		for i in range(random.randint(5, 15)):
			object_list[DEBRIS_LIST_INDEX].append(Debris(player_2.x, player_2.y, random.randint(0,359)))	
		for i in range(random.randint(5, 15)):
			object_list[DEBRIS_LIST_INDEX].append(Debris(player_1.x, player_1.y, random.randint(0,359)))	
		
		momentum = ((player_1.dx * normal_unit_x + player_1.dy * normal_unit_y) - (player_2.dx * normal_unit_x + player_2.dy * normal_unit_y))
		reflection_1_x = player_1.dx - momentum * normal_unit_x
		reflection_1_y = player_1.dy - momentum * normal_unit_y
		reflection_2_x = player_2.dx + momentum * normal_unit_x
		reflection_2_y = player_2.dy + momentum * normal_unit_y
		
		player_1.dx = reflection_1_x
		player_1.dy = reflection_1_y
		player_2.dx = reflection_2_x
		player_2.dy = reflection_2_y
		
		while distance_squared <= distance_squared < (2 * PLAYER_RADIUS) ** 2:
			player_1.x += (player_1.dx * 0.205)
			player_1.y += (player_1.dy * 0.205)
			player_2.x += (player_2.dx * 0.205)
			player_2.y += (player_2.dy * 0.205)
			distance_squared = ((player_1.x - player_2.x) ** 2 + (player_1.y - player_2.y) ** 2)		

	# update each of the weapons (in reverse order so they can be despawned if necessary)
	for i in range(len(object_list[WEAPON_LIST_INDEX])-1, -1, -1):
	
		weapon = object_list[WEAPON_LIST_INDEX][i]
		
		weapon.moving_fast_enough_to_damage = False
		
		if weapon.currently_held_by == -1:
			
			# apply drag to the weapons but do not let them stop entirely
			weapon_speed = (weapon.dx ** 2 + weapon.dy ** 2) ** 0.5
			
			if weapon_speed > 3:
				weapon.moving_fast_enough_to_damage = True
			
			if weapon_speed > 0.1:
				weapon.dx *= 0.99
				weapon.dy *= 0.99
			
			# keep the weapon "trail"
			weapon.ppx = weapon.px
			weapon.ppy = weapon.py
			weapon.px = weapon.x
			weapon.py = weapon.y
			
			# update the weapon positions
			weapon.x += weapon.dx
			weapon.y += weapon.dy

			# detect and respond to collisions between the weapon and the arena boundaries
			if weapon.x - WEAPON_RADIUS < 0:
				weapon.dx *= -1
				weapon.x = 1 + WEAPON_RADIUS
				
			if weapon.x + WEAPON_RADIUS >= 750:
				weapon.dx *= -1
				weapon.x = 748 - WEAPON_RADIUS
				
			# detect and respond to collisions between the weapon and the arena boundaries
			if weapon.y - WEAPON_RADIUS < 0:
				weapon.dy *= -1
				weapon.y = 1 + WEAPON_RADIUS

			if weapon.y + WEAPON_RADIUS >= 750:
				weapon.dy *= -1
				weapon.y = 748 - WEAPON_RADIUS

			# detect and respond to collisions between the weapon and a column
			for column in object_list[COLUMN_LIST_INDEX]:
			
				distance_squared = (weapon.x - column.x) ** 2 + (weapon.y - column.y) ** 2
				
				if distance_squared < (WEAPON_RADIUS + COLUMN_RADIUS) ** 2:
					normal_magn = distance_squared ** 0.5
					normal_unit_x = (weapon.x - column.x) / normal_magn
					normal_unit_y = (weapon.y - column.y) / normal_magn
					dot_product = weapon.dx * normal_unit_x + weapon.dy * normal_unit_y
					reflection_x = weapon.dx - 2 * normal_unit_x * dot_product
					reflection_y = weapon.dy - 2 * normal_unit_y * dot_product
					weapon.dx = reflection_x
					weapon.dy = reflection_y
					
					while distance_squared <= (WEAPON_RADIUS + COLUMN_RADIUS) ** 2:
						weapon.x += (weapon.dx * 0.205)
						weapon.y += (weapon.dy * 0.205)
						distance_squared = (weapon.x - column.x) ** 2 + (weapon.y - column.y) ** 2

			# detect and respond to collisisions between the weapon and a player
			for j in range(i):
			
				other_weapon = object_list[WEAPON_LIST_INDEX][j]
				
				distance_squared = ((weapon.x - other_weapon.x) ** 2 + (weapon.y - other_weapon.y) ** 2)

				if distance_squared < (WEAPON_RADIUS + WEAPON_RADIUS) ** 2:

					normal_magn = ((weapon.x - other_weapon.x) ** 2 + (weapon.y - other_weapon.y) ** 2) ** 0.5
					if normal_magn > 0:
						normal_unit_x = (other_weapon.x - weapon.x) / normal_magn
						normal_unit_y = (other_weapon.y - weapon.y) / normal_magn
					else:
						normal_unit_x = 1
						normal_unit_y = 1
					
					momentum = ((weapon.dx * normal_unit_x + weapon.dy * normal_unit_y) - (other_weapon.dx * normal_unit_x + other_weapon.dy * normal_unit_y))
					reflection_1_x = weapon.dx - momentum * normal_unit_x
					reflection_1_y = weapon.dy - momentum * normal_unit_y
					reflection_2_x = other_weapon.dx + momentum * normal_unit_x
					reflection_2_y = other_weapon.dy + momentum * normal_unit_y
					
					weapon.dx = reflection_1_x
					weapon.dy = reflection_1_y
					other_weapon.dx = reflection_2_x
					other_weapon.dy = reflection_2_y
					
					while distance_squared <= (WEAPON_RADIUS + WEAPON_RADIUS) ** 2:
						weapon.x += (weapon.dx * 0.205)
						weapon.y += (weapon.dy * 0.205)
						other_weapon.x += (other_weapon.dx * 0.205)
						other_weapon.y += (other_weapon.dy * 0.205)
						distance_squared = ((weapon.x - other_weapon.x) ** 2 + (weapon.y - other_weapon.y) ** 2)
						
			# detect and respond to collisisions between the weapon and a player
			for player in object_list[PLAYER_LIST_INDEX]:
			
				distance_squared = ((weapon.x - player.x) ** 2 + (weapon.y - player.y) ** 2)
		
				# respond if there has been a collision between this weapon and the player
				if distance_squared < (WEAPON_RADIUS + PLAYER_RADIUS) ** 2:

					normal_magn = ((weapon.x - player.x) ** 2 + (weapon.y - player.y) ** 2) ** 0.5
					normal_unit_x = (player.x - weapon.x) / normal_magn
					normal_unit_y = (player.y - weapon.y) / normal_magn
					
					if weapon_speed < 3 and player.trying_for_a_weapon and player.holding_onto_weapon == -1:
					
						weapon.x = player.x
						weapon.y = player.y
						weapon.dx = 0
						weapon.dy = 0
						weapon.currently_held_by = player.id
						player.trying_for_a_weapon = False
						player.holding_onto_weapon = i

					else:

						# this value is computed from the relative velocity projected onto the normal, to compute collision damage
						relative_speed_factor = abs(((weapon.dx - player.dx) * normal_unit_x) + ((weapon.dy - player.dy) * normal_unit_y)) / maximum_speed
					
						#if relative_speed_factor > 0.5:
						player.current_status -= ( relative_speed_factor * maximum_collision_damage)

						# spawn some debris
						for i in range(random.randint(15, 25)):
							object_list[DEBRIS_LIST_INDEX].append(Debris(weapon.x, weapon.y, random.randint(0,359)))	
					
						# the mass of the weapon relative to the mass of the player is 0.1 : 1.0
						momentum = ((weapon.dx * normal_unit_x + weapon.dy * normal_unit_y) - (player.dx * normal_unit_x + player.dy * normal_unit_y))
						reflection_1_x = weapon.dx - momentum * normal_unit_x
						reflection_1_y = weapon.dy - momentum * normal_unit_y
						reflection_2_x = player.dx + momentum * normal_unit_x
						reflection_2_y = player.dy + momentum * normal_unit_y
						
						weapon.dx = reflection_1_x
						weapon.dy = reflection_1_y
						player.dx = reflection_2_x
						player.dy = reflection_2_y
						
						while distance_squared <= (WEAPON_RADIUS + PLAYER_RADIUS) ** 2:
							weapon.x += (weapon.dx * 0.205)
							weapon.y += (weapon.dy * 0.205)
							player.x += (player.dx * 0.205)
							player.y += (player.dy * 0.205)
							distance_squared = ((weapon.x - player.x) ** 2 + (weapon.y - player.y) ** 2)
		
		else:
			
			weapon.x = object_list[PLAYER_LIST_INDEX][weapon.currently_held_by].x
			weapon.y = object_list[PLAYER_LIST_INDEX][weapon.currently_held_by].y
	

	# update each of the pieces of debris (in reverse order so they can be despawned if necessary)
	for i in range(len(object_list[DEBRIS_LIST_INDEX])-1, -1, -1):
		object_list[DEBRIS_LIST_INDEX][i].timer -= 1
		if object_list[DEBRIS_LIST_INDEX][i].timer < 0:
			object_list[DEBRIS_LIST_INDEX].pop(i)
		else:
			object_list[DEBRIS_LIST_INDEX][i].x += object_list[DEBRIS_LIST_INDEX][i].dx
			object_list[DEBRIS_LIST_INDEX][i].y += object_list[DEBRIS_LIST_INDEX][i].dy
	
	return object_list

	
def render_game_arena(camera_surf, object_list):

	# fill the camera surface
	camera_surf.fill(pygame.Color('black'))

	# draw the hazard entities
	for hazard in object_list[HAZARD_LIST_INDEX]:
	
		hazard_x = int(hazard.x) - HAZARD_RADIUS
		hazard_y = int(hazard.y) - HAZARD_RADIUS
		camera_surf.blit(hazard_sprite, (hazard_x, hazard_y))

	# draw the column entities
	for column in object_list[COLUMN_LIST_INDEX]:
	
		column_x = int(column.x) - COLUMN_RADIUS
		column_y = int(column.y) - COLUMN_RADIUS
		camera_surf.blit(column_sprite, (column_x, column_y))

	# draw the player entities
	for player in object_list[PLAYER_LIST_INDEX]:
	
		player_x = int(player.x) - PLAYER_RADIUS
		player_y = int(player.y) - PLAYER_RADIUS
		
		if player.is_falling_into_hazard == -1:
		
			camera_surf.blit(player_sprite, (player_x, player_y))
			
			# draw a line to indicate the direction this player faces
			handle_x = int(player.x) + int(PLAYER_RADIUS * math.cos(math.radians(player.throwing_angle)))
			handle_y = int(player.y) + int(PLAYER_RADIUS * math.sin(math.radians(player.throwing_angle)))
			pygame.draw.line(camera_surf, COLOUR_WHT, (int(player.x), int(player.y)), (handle_x, handle_y), 1)			
		
		else:
		
			zoom_size_for_falling = int (player.is_falling_into_hazard * PLAYER_RADIUS * 2)
			player_x = int(player.x - player.is_falling_into_hazard * PLAYER_RADIUS)
			player_y = int(player.y - player.is_falling_into_hazard * PLAYER_RADIUS)
			
			if zoom_size_for_falling > 0:
				camera_surf.blit(pygame.transform.smoothscale(player_sprite, (zoom_size_for_falling, zoom_size_for_falling)), (player_x, player_y))
				
			player.is_falling_into_hazard -= 0.1

	# draw the weapon entities
	for weapon in object_list[WEAPON_LIST_INDEX]:

		# only draw those weapons that are not in the possession of someone currently falling 
		if weapon.currently_held_by > -1 and object_list[PLAYER_LIST_INDEX][weapon.currently_held_by].is_falling_into_hazard > -1:
			pass
		else:
		
			if weapon.moving_fast_enough_to_damage:
				weapon_x = int(weapon.ppx) - WEAPON_RADIUS
				weapon_y = int(weapon.ppy) - WEAPON_RADIUS
				camera_surf.blit(onion2_sprite, (weapon_x, weapon_y))
				weapon_x = int(weapon.px) - WEAPON_RADIUS
				weapon_y = int(weapon.py) - WEAPON_RADIUS
				camera_surf.blit(onion1_sprite, (weapon_x, weapon_y))
			
			weapon_x = int(weapon.x) - WEAPON_RADIUS
			weapon_y = int(weapon.y) - WEAPON_RADIUS
			camera_surf.blit(weapon_sprite, (weapon_x, weapon_y))

			
	# draw the debris entities
	for debris in object_list[DEBRIS_LIST_INDEX]:
		camera_surf.set_at((int(debris.x), int(debris.y)), COLOUR_WHT)
	
	# render the player "names", above the sprite is possible and below if necessary
	if object_list[PLAYER_LIST_INDEX][0].x < 40:
		caption_offset_x = (40 - object_list[PLAYER_LIST_INDEX][0].x)
	elif object_list[PLAYER_LIST_INDEX][0].x > 750 - 40:
		caption_offset_x = (40 - (750 - object_list[PLAYER_LIST_INDEX][0].x)) * -1
	else:
		caption_offset_x = 0

	if object_list[PLAYER_LIST_INDEX][0].y < 40:
		caption_offset_y = + 12
	else:
		caption_offset_y = - 30
	camera_surf.blit(caption_for_player_0, (object_list[PLAYER_LIST_INDEX][0].x - (caption_for_player_0.get_width() // 2) + caption_offset_x, object_list[PLAYER_LIST_INDEX][0].y + caption_offset_y))
	current_health_bar_width = (object_list[PLAYER_LIST_INDEX][0].current_status / 100 * maximum_health_bar_width)
	pygame.draw.rect(camera_surf, COLOUR_WHT, (object_list[PLAYER_LIST_INDEX][0].x - (current_health_bar_width // 2) + caption_offset_x, object_list[PLAYER_LIST_INDEX][0].y + caption_offset_y + 13, current_health_bar_width, 1))
	pygame.draw.rect(camera_surf, COLOUR_WHT, (object_list[PLAYER_LIST_INDEX][0].x - (maximum_health_bar_width // 2) + caption_offset_x, object_list[PLAYER_LIST_INDEX][0].y + caption_offset_y + 11, maximum_health_bar_width, 5), 1)

	# render the player "names", above the sprite is possible and below if necessary
	if object_list[PLAYER_LIST_INDEX][1].x < 40:
		caption_offset_x = (40 - object_list[PLAYER_LIST_INDEX][1].x)
	elif object_list[PLAYER_LIST_INDEX][1].x > 750 - 40:
		caption_offset_x = (40 - (750 - object_list[PLAYER_LIST_INDEX][1].x)) * -1
	else:
		caption_offset_x = 0
		
	if object_list[PLAYER_LIST_INDEX][1].y < 40:
		caption_offset_y = + 12
	else:
		caption_offset_y = - 30
	camera_surf.blit(caption_for_player_1, (object_list[PLAYER_LIST_INDEX][1].x - (caption_for_player_1.get_width() // 2) + caption_offset_x, object_list[PLAYER_LIST_INDEX][1].y + caption_offset_y))
	current_health_bar_width = (object_list[PLAYER_LIST_INDEX][1].current_status / 100 * maximum_health_bar_width)
	pygame.draw.rect(camera_surf, COLOUR_WHT, (object_list[PLAYER_LIST_INDEX][1].x - (current_health_bar_width // 2) + caption_offset_x, object_list[PLAYER_LIST_INDEX][1].y + caption_offset_y + 13, current_health_bar_width, 1))
	pygame.draw.rect(camera_surf, COLOUR_WHT, (object_list[PLAYER_LIST_INDEX][1].x - (maximum_health_bar_width // 2) + caption_offset_x, object_list[PLAYER_LIST_INDEX][1].y + caption_offset_y + 11, maximum_health_bar_width, 5), 1)
		
	return camera_surf


def apply_visual_fx(arg_surface):

	left_glow_y = pygame.Surface((window_size[0], window_size[1]))
	left_glow_y.blit(arg_surface, (-1, 0))
	left_glow_y.blit(channel_y, (0, 0), special_flags = pygame.BLEND_SUB)

	hard_blur_g = pygame.transform.smoothscale(pygame.transform.smoothscale(arg_surface, (window_size[0] // 4, window_size[1] // 4)), (window_size[0], window_size[1]))
	soft_blur_g = pygame.transform.smoothscale(pygame.transform.smoothscale(arg_surface, (window_size[0] // 8, window_size[1] // 8)), (window_size[0], window_size[1]))
	
	ret_surface = pygame.Surface((window_size[0], window_size[1]))
	ret_surface.blit(hard_blur_g, (0, 0))
	ret_surface.blit(soft_blur_g, (0, 0), special_flags = pygame.BLEND_ADD)
	ret_surface.blit(channel_g, (0, 0), special_flags=pygame.BLEND_SUB)
	ret_surface.blit(left_glow_y, (0, 0), special_flags=pygame.BLEND_ADD)
	ret_surface.blit(arg_surface, (0, 0), special_flags=pygame.BLEND_MAX)
	ret_surface.blit(scan_line, (0, 0), special_flags=pygame.BLEND_MULT)
	
	return ret_surface

	
# ================================================================================

	
def main():
	
	global small_font
	global small_font
	global large_font

	global name_of_player_0
	global caption_for_player_0
	if not player_0_fsm_hidden:	
		caption_for_player_0 = small_font.render(name_of_player_0, False, COLOUR_WHT)
	else:
		caption_for_player_0 = small_font.render(name_of_player_0, False, COLOUR_BLU)
	
	global name_of_player_1
	global caption_for_player_1
	if not player_1_fsm_hidden:	
		caption_for_player_1 = small_font.render(name_of_player_1, False, COLOUR_WHT)
	else:
		caption_for_player_1 = small_font.render(name_of_player_1, False, COLOUR_BLU)

	
	special_text_READY = large_font.render('READY', False, COLOUR_WHT)
	special_text_FIGHT = large_font.render('FIGHT', False, COLOUR_WHT)
	special_text_END_5 = large_font.render('5', False, COLOUR_WHT)
	special_text_END_4 = large_font.render('4', False, COLOUR_WHT)
	special_text_END_3 = large_font.render('3', False, COLOUR_WHT)
	special_text_END_2 = large_font.render('2', False, COLOUR_WHT)
	special_text_END_1 = large_font.render('1', False, COLOUR_WHT)
	special_text_0_WIN = large_font.render(name_of_player_0 + " WINS", False, COLOUR_WHT)
	special_text_1_WIN = large_font.render(name_of_player_1 + " WINS", False, COLOUR_WHT)
	special_text_NOWIN = large_font.render("NO WINNER", False, COLOUR_WHT)
	global special_text_QMARK
	special_text_QMARK = large_font.render("HIDDEN", False, COLOUR_WHT)
	
	# create the clock
	clock = pygame.time.Clock()

	# create the window surface
	if switch_to_resize_display:
		window_surf = pygame.display.set_mode( (683, 384) )
	else:
		window_surf = pygame.display.set_mode(window_size)
	
	pygame.display.set_caption('glad AI tors')

	# load the game assets
	sprite_assets = pygame.image.load("Assets\sprite_asset.png").convert_alpha()
	splash_sprite.blit(sprite_assets, (0, 0), (0, 0, 1131, 369))
	player_sprite.blit(sprite_assets, (0, 0), (63, 371, 21, 21))
	column_sprite.blit(sprite_assets, (0, 0), (86, 371, 40, 40))
	hazard_sprite.blit(sprite_assets, (0, 0), (0, 371, 61, 61))
	weapon_sprite.blit(sprite_assets, (0, 0), (63, 394, 11, 11))
	onion1_sprite.blit(sprite_assets, (0, 0), (63, 407, 11, 11))
	onion2_sprite.blit(sprite_assets, (0, 0), (63, 421, 11, 11))

	# prepare the visual effect surfaces
	fx_fade_surf.fill(COLOUR_BLK)
	fx_fade_alpha = 255
	fx_fade_delta = -1
	
	# create the surfaces used for rendering
	backgd_surf = create_backgd_surface()
	foregd_surf = create_foregd_surface()
	camera_surf = pygame.Surface(arena_dimens)
	camera_surf.set_colorkey(pygame.Color('black'))
	visual_surf = pygame.Surface(window_size)	

	# initialize the game objects
	object_list = initialize_game_objects()

	# initialize the game state
	if switch_to_turn_off_title:
		game_state = STATE_MATCH
	else:
		game_state = STATE_TITLE

	# create a list (initially empty) to hold drawn debugging elements
	global debug_elements_to_draw
	debug_elements_to_draw = []	

	# keep track of the number of frames that have elapsed
	global current_match_duration
	current_match_duration = 0
	
	winner_of_the_match = -1
	
	# this is the main loop which can be terminated from the close button in the top corner
	closed_flag = False
	while not closed_flag:

		# this just checks if the close button was pressed
		for event in pygame.event.get():
			if event.type == QUIT:
				closed_flag = True

		if game_state == STATE_TITLE:
			
			fx_fade_alpha += (4 * fx_fade_delta)
			
			if fx_fade_alpha <= 0:
				fx_fade_delta = 1
				
			if fx_fade_alpha >= 255:
				game_state = STATE_START
				countdown_timer = 120
			
		else:
		
			if game_state == STATE_START:
				
				countdown_timer -= 1
				
				if countdown_timer <= 0:
				
					game_state = STATE_MATCH

			elif game_state == STATE_MATCH:
			
				for id in range(2):
				
					if (0.1 > object_list[PLAYER_LIST_INDEX][id].is_falling_into_hazard > -1) or object_list[PLAYER_LIST_INDEX][id].current_status <= 0:
						object_list[PLAYER_LIST_INDEX][id].current_status = 0
						winner_of_the_match = 1 - id
						game_state = STATE_FINAL
						countdown_timer = 120
					
					if object_list[PLAYER_LIST_INDEX][id].waiting_period > 0:
						
						object_list[PLAYER_LIST_INDEX][id].waiting_period -= 1

					else:

						# process the register dictionary (i.e., what actions they most recently selected) for this player 
						process_register_dictionary(object_list, id)				
						
						# update the "shared memory" wherein the data required by the agents is available
						update_compressed_environment_data(object_list, id)

						try:
						
							# call the function specified in the finite state machine and corresponding to the current behaviour of the player
							object_list[PLAYER_LIST_INDEX][id].function_state, object_list[PLAYER_LIST_INDEX][id].register_dictionary = getattr(globals().get("player_" + str(id) + "_controller"), object_list[PLAYER_LIST_INDEX][id].function_state)()

						except:
						
							object_list[PLAYER_LIST_INDEX][id].function_state = "start"
							
						# use the "shared memory" to check the cost that has been incurred
						object_list[PLAYER_LIST_INDEX][id].waiting_period = int (compressed_environment_data[48] / 180)
				
					
				# update the game objects
				object_list = update_game_arena(object_list)

			elif game_state == STATE_FINAL:
				
				countdown_timer -= 1
				
				# if countdown_timer <= 0:
				
					# print(name_of_player_0, name_of_player_1, "-1", round(object_list[PLAYER_LIST_INDEX][0].current_status, 1), round(object_list[PLAYER_LIST_INDEX][1].current_status, 1))
					# exit()

			# this could be improved dramatically but time is short
			
			# ==========
			if not switch_to_render_nothing:
					
				# render the game objects on the camera surface
				camera_surf = render_game_arena(camera_surf, object_list)	

				# draw all the debugging elements
				if not switch_to_turn_off_debug:
					for debug_element in debug_elements_to_draw:
						if len(debug_element) == 3:
							pygame.draw.circle(camera_surf, COLOUR_ERR, (debug_element[0], debug_element[1]), debug_element[2], 1)
						elif len(debug_element) == 4:
							pygame.draw.line(camera_surf, COLOUR_ERR, (debug_element[0], debug_element[1]), (debug_element[2], debug_element[3]))
							drew_something_test = True

				# if the game is in the starting state, display the "READY...FIGHT" as appropriate
				if game_state == STATE_START:
					if 30 < countdown_timer < 90:
						camera_surf.blit(special_text_READY, ((camera_surf.get_width() // 2) - (special_text_READY.get_width() // 2), (camera_surf.get_height() // 2) - (special_text_READY.get_height() // 2)))
					elif countdown_timer < 30:
						camera_surf.blit(special_text_FIGHT, ((camera_surf.get_width() // 2) - (special_text_FIGHT.get_width() // 2), (camera_surf.get_height() // 2) - (special_text_FIGHT.get_height() // 2)))

				# if the game is in the match state with 5 "seconds" or less remaining, display the counter
				elif game_state == STATE_MATCH:
					if (maximum_match_duration - current_match_duration) < 5 * frame_rate:
						if (maximum_match_duration - current_match_duration) < 0:
							game_state = STATE_FINAL
							countdown_timer = 120
						elif (maximum_match_duration - current_match_duration) < 1 * frame_rate:
							camera_surf.blit(special_text_END_1, ((camera_surf.get_width() // 2) - (special_text_END_1.get_width() // 2), (camera_surf.get_height() // 2) - (special_text_END_1.get_height() // 2)))
						elif (maximum_match_duration - current_match_duration) < 2 * frame_rate:
							camera_surf.blit(special_text_END_2, ((camera_surf.get_width() // 2) - (special_text_END_2.get_width() // 2), (camera_surf.get_height() // 2) - (special_text_END_2.get_height() // 2)))
						elif (maximum_match_duration - current_match_duration) < 3 * frame_rate:
							camera_surf.blit(special_text_END_3, ((camera_surf.get_width() // 2) - (special_text_END_3.get_width() // 2), (camera_surf.get_height() // 2) - (special_text_END_3.get_height() // 2)))
						elif (maximum_match_duration - current_match_duration) < 4 * frame_rate:
							camera_surf.blit(special_text_END_4, ((camera_surf.get_width() // 2) - (special_text_END_4.get_width() // 2), (camera_surf.get_height() // 2) - (special_text_END_4.get_height() // 2)))
						else:
							camera_surf.blit(special_text_END_5, ((camera_surf.get_width() // 2) - (special_text_END_5.get_width() // 2), (camera_surf.get_height() // 2) - (special_text_END_5.get_height() // 2)))
						
				# if the game is in the final state, display the information about the victor
				elif game_state == STATE_FINAL:
					if object_list[PLAYER_LIST_INDEX][0].current_status == object_list[PLAYER_LIST_INDEX][1].current_status:
						camera_surf.blit(special_text_NOWIN, ((camera_surf.get_width() // 2) - (special_text_NOWIN.get_width() // 2), (camera_surf.get_height() // 2) - (special_text_NOWIN.get_height() // 2)))
					else:
						if winner_of_the_match == -1:
							if object_list[PLAYER_LIST_INDEX][0].current_status > object_list[PLAYER_LIST_INDEX][1].current_status:
								winner_of_the_match = 0
							else:
								winner_of_the_match = 1
						if winner_of_the_match == 0:
							camera_surf.blit(special_text_0_WIN, ((camera_surf.get_width() // 2) - (special_text_0_WIN.get_width() // 2), (camera_surf.get_height() // 2) - (special_text_0_WIN.get_height() // 2)))
						else:
							camera_surf.blit(special_text_1_WIN, ((camera_surf.get_width() // 2) - (special_text_1_WIN.get_width() // 2), (camera_surf.get_height() // 2) - (special_text_1_WIN.get_height() // 2)))
						
				# blit the background, camera, and foreground to the window
				visual_surf.blit(backgd_surf, (0, 0))
				visual_surf.blit(camera_surf, arena_offset)
				visual_surf.blit(foregd_surf, (0, 0))

				# highlight the node of the finite state machine of each player that corresponds to their current state
				if not player_0_fsm_hidden:
					try:
						(fsm_highlight_x, fsm_highlight_y) = player_0_fsm_graph[1][object_list[PLAYER_LIST_INDEX][0].function_state]
						pygame.draw.circle(visual_surf, COLOUR_DIM, (fsm_highlight_x + upper_view_rect[0], fsm_highlight_y + upper_view_rect[1]), 10)
					except:
						pass
				
				if not player_1_fsm_hidden:
					try:
						(fsm_highlight_x, fsm_highlight_y) = player_1_fsm_graph[1][object_list[PLAYER_LIST_INDEX][1].function_state]
						pygame.draw.circle(visual_surf, COLOUR_DIM, (fsm_highlight_x + lower_view_rect[0], fsm_highlight_y + lower_view_rect[1]), 10)
					except:
						pass
			else:
					
				if game_state == STATE_MATCH:
					if (maximum_match_duration - current_match_duration) < 0:
						game_state = STATE_FINAL
						
				elif game_state == STATE_FINAL:
					if object_list[PLAYER_LIST_INDEX][0].current_status == object_list[PLAYER_LIST_INDEX][1].current_status:
						# summary for no winner
						print(name_of_player_0, name_of_player_1, -1, round(object_list[PLAYER_LIST_INDEX][0].current_status, 1), round(object_list[PLAYER_LIST_INDEX][1].current_status, 1))
						exit()
					else:
						if winner_of_the_match == -1:
							if object_list[PLAYER_LIST_INDEX][0].current_status > object_list[PLAYER_LIST_INDEX][1].current_status:
								winner_of_the_match = 0
							else:
								winner_of_the_match = 1
						if winner_of_the_match == 0:
							# summary for winner was 0
							print(name_of_player_0, name_of_player_1, name_of_player_0, round(object_list[PLAYER_LIST_INDEX][0].current_status, 1), round(object_list[PLAYER_LIST_INDEX][1].current_status, 1))
							exit()
						else:
							# summary for winner was 1
							print(name_of_player_0, name_of_player_1, name_of_player_1, round(object_list[PLAYER_LIST_INDEX][0].current_status, 1), round(object_list[PLAYER_LIST_INDEX][1].current_status, 1))
							exit()
							
			# ==========
			
			
		# this is where you choose whether or not to apply the visual effects

		if not switch_to_render_nothing:
		
			if game_state == STATE_TITLE:
			
				# blit the splash screen asset
				visual_surf.fill(COLOUR_BLK)
				visual_surf.blit(splash_sprite, (117, 199))
				
				# blit the "fade" visual effect surface
				fx_fade_surf.set_alpha(fx_fade_alpha)
				visual_surf.blit(fx_fade_surf, (117, 199))			
				
			else:
				if not switch_to_ignore_effects:
					visual_surf = apply_visual_fx(visual_surf)
				
			if switch_to_resize_display:
				window_surf.blit(pygame.transform.smoothscale(visual_surf, (683, 384)), (0, 0))
			else:
				window_surf.blit(visual_surf, (0, 0))
				
			# update the display
			pygame.display.update()
			
			# frame rate limiting is on
			clock.tick(frame_rate)
			

		# clear out the collection of debug elements to be drawn
		debug_elements_to_draw = []	
		
		# increment the duration counter
		current_match_duration += 1
		
		# if switch_to_render_nothing:
			# print("	", current_match_duration)
		
		

	
# ================================================================================

global switch_to_turn_off_title
switch_to_turn_off_title = False
global switch_to_resize_display
switch_to_resize_display = False
global switch_to_ignore_effects
switch_to_ignore_effects = False
global switch_to_turn_off_debug
switch_to_turn_off_debug = False

global switch_to_render_nothing   #
switch_to_render_nothing = False  #
		
global player_0_fsm_hidden		
player_0_fsm_hidden = False

global player_1_fsm_hidden		
player_1_fsm_hidden = False
		
if len(sys.argv) > 3:
	if "-t" in sys.argv[3:]:
		sys.argv.remove("-t")
		switch_to_turn_off_title = True
	if "-r" in sys.argv[3:]:
		sys.argv.remove("-r")
		switch_to_resize_display = True
	if "-f" in sys.argv[3:]:
		sys.argv.remove("-f")
		switch_to_ignore_effects = True
	if "-d" in sys.argv[3:]:
		sys.argv.remove("-d")
		switch_to_turn_off_debug = True	
	if "-n" in sys.argv[3:]:
		sys.argv.remove("-n")
		switch_to_render_nothing = True		
		

# a more sophisticated command-line argument interface is warranted...
if not (len(sys.argv) == 3):
	print("")
	print("NAME")
	print("")
	print("   glad_AI_tors - start a 'glad AI tors' match between two players")
	print("")
	print("SYNOPSIS")
	print("")
	print("   python glad_AI_tors.py FILE FILE [OPTIONS]")
	print("")
	print("DESCRIPTION")
	print("")
	print("   glad_AI_tors will open the two source FILEs (written with Python 3 with the")
	print("   format described by the specification) and performs the processing required")
	print("   to construct a finite state machine graph and import the functionality that")
	print("   is defined by each. The program then simulates a 'match' between the agents")
	print("   specified in these two files and renders to a window of size 1366 x 768.")
	print("")
	print("")
	print("OPTIONS")
	print("")
	print("   -t    Start the program without showing the title screen.")
	print("")
	print("   -r    Resize the display to 50% of its default size (i.e., 683 x 384).")
	print("")
	print("   -f    Run the program without the underglow or scanline special effects.")
	print("")
	print("   -d    Ignore print statements from the player source files provided and")
	print("         suppress any drawn elements (i.e., shapes drawn in red) that were")
	print("         specified using the 'DEBUGS' register in the return dictionary.")
	print("")
	exit()
else:
	name_of_source_file_for_player_0 = "Players/"+sys.argv[1]
	name_of_source_file_for_player_1 = "Players/"+sys.argv[2]

# remove the complete behaviour definition files if they exist (which they shouldn't)
if os.path.exists("complete_behaviour_definition_0.py"):
  os.remove("complete_behaviour_definition_0.py")
if os.path.exists("complete_behaviour_definition_1.py"):
  os.remove("complete_behaviour_definition_1.py")

# create a region of shared memory using what is quite possibly the worst thing I have ever written
compressed_environment_data = []
compressed_environment_data.append("SOM")
for i in range(49):
	compressed_environment_data.append(-1)
compressed_environment_data.append("EOM")

# get the memory address of the world
compressed_environment_data_address = id(compressed_environment_data)

# write the memory address along with the required function definitions to create a "function library"
function_library = "import ctypes" + "\n"
function_library += "from math import ceil, floor, log, pow, sqrt, acos, asin, atan, atan2, cos, sin, tan, degrees, radians, pi, exp" + "\n" # students are NOT allowed to make imports of their own
function_library += "from random import random, randint, choice, shuffle" + "\n"
function_library += "\n"
function_library += "compressed_environment_data_address_" + random_header + " = " + str(compressed_environment_data_address) + "\n"
function_library += "\n"
function_library += "def __environment_data():" + "\n"
function_library += "	return ctypes.cast(compressed_environment_data_address_" + random_header + ", ctypes.py_object).value[:]" + "\n"
function_library += "\n"
function_library += "def __incur_call_costs():" + "\n"
function_library += "	ctypes.cast(compressed_environment_data_address_" + random_header + ", ctypes.py_object).value[48] += 1" + "\n"
function_library += "\n"
function_library += "def get_position_tuple():" + "\n"
function_library += "	protected_data = __environment_data()" + "\n"
function_library += "	return (protected_data[1], protected_data[2])" + "\n"
function_library += "" + "\n"
function_library += "def get_velocity_tuple():" + "\n"
function_library += "	protected_data = __environment_data()" + "\n"
function_library += "	return (protected_data[3], protected_data[4])" + "\n"
function_library += "" + "\n"
function_library += "def get_current_status():" + "\n"
function_library += "	protected_data = __environment_data()" + "\n"
function_library += "	return protected_data[5]" + "\n"
function_library += "" + "\n"
function_library += "def get_if_have_weapon():" + "\n"
function_library += "	protected_data = __environment_data()" + "\n"
function_library += "	return (protected_data[6] != -1)" + "\n"
function_library += "" + "\n"
function_library += "def get_my_stored_data():" + "\n"
function_library += "	protected_data = __environment_data()" + "\n"
function_library += "	return protected_data[7]" + "\n"
function_library += "" + "\n"
function_library += "def get_throwing_angle():" + "\n"
function_library += "	protected_data = __environment_data()" + "\n"
function_library += "	return protected_data[8]" + "\n"
function_library += "" + "\n"
function_library += "def get_match_duration():" + "\n"
function_library += "	protected_data = __environment_data()" + "\n"
function_library += "	return protected_data[47]" + "\n"
function_library += "" + "\n"
function_library += "def get_the_radar_data(radar_angle):" + "\n"
function_library += "" + "\n"
function_library += "	__incur_call_costs()" + "\n"
function_library += "" + "\n"
function_library += "	protected_data = __environment_data()" + "\n"
function_library += "" + "\n"
function_library += "	# check if the first and last element are SOM and EOM respectively" + "\n"
function_library += "" + "\n"
function_library += "	u_sol_x = protected_data[1]" + "\n"
function_library += "	u_sol_y = protected_data[2]" + "\n"
function_library += "	u_eol_x = u_sol_x + cos(radians(radar_angle))" + "\n"
function_library += "	u_eol_y = u_sol_y + sin(radians(radar_angle))" + "\n"
function_library += "" + "\n"
function_library += "	detectables = []" + "\n"
function_library += "	detectables.append( ('player', (protected_data[9], protected_data[10], 10), (protected_data[11], (protected_data[12] > -1), protected_data[13])) )" + "\n" # 3rd component of 2nd tuple is PLAYER_RADIUS, 3rd tuple is player angle and whether or not player is holding weapon
function_library += "	for i in range(15, 23, 2):" + "\n"
function_library += "		detectables.append( ('column', (protected_data[i], protected_data[i+1], 21), ()) )" + "\n" # 3rd tuple component is COLUMN_RADIUS
function_library += "	for i in range(23, 29, 2):" + "\n"
function_library += "		detectables.append( ('hazard', (protected_data[i], protected_data[i+1], 30), ()) )" + "\n" # 3rd tuple component is HAZARD_RADIUS
function_library += "	for i in range(29, 45, 3):" + "\n"
function_library += "		detectables.append( ('weapon', (protected_data[i], protected_data[i+1], 5), (protected_data[i+2])) )" + "\n" # 3rd tuple component is WEAPON_RADIUS
function_library += "" + "\n"
function_library += "	nearest_of_every_detectable = None" + "\n"
function_library += "	squared_distance_to_nearest = 0" + "\n"
function_library += "	extra_data_for_nearest = ()" + "\n"
function_library += "" + "\n"
function_library += "	for detectable in detectables:" + "\n"
function_library += "" + "\n"
function_library += "		(v_ctr_x, v_ctr_y, v_rad) = detectable[1]" + "\n"
function_library += "" + "\n"
function_library += "		# the equation for all points on the line segment u can be considered u = u_sol + t * (u_eol - u_sol), for t in [0, 1]" + "\n"
function_library += "		# the center of the circle and the nearest point on the line segment (that which we are trying to find) define a line " + "\n"
function_library += "		# that is is perpendicular to the line segment u (i.e., the dot product will be 0); in other words, it suffices to take" + "\n"
function_library += "		# the equation v_ctr - (u_sol + t * (u_eol - u_sol)) · (u_evol - u_sol) and solve for t" + "\n"
function_library += "		t = ((v_ctr_x - u_sol_x) * (u_eol_x - u_sol_x) + (v_ctr_y - u_sol_y) * (u_eol_y - u_sol_y)) / ((u_eol_x - u_sol_x) ** 2 + (u_eol_y - u_sol_y) ** 2)" + "\n"
function_library += "" + "\n"
function_library += "		# this t can be used to find the nearest point w on the infinite line between u_sol and u_sol, but the line is actually " + "\n"
function_library += "		# a ray emitted in the direction the radar is pointed, so t must be nonnegative (i.e., the ray cannot go backward)" + "\n"
function_library += "		t = max(t, 0)" + "\n"
function_library += "" + "\n"
function_library += "		# so the nearest point on the line segment, w, is defined as" + "\n"
function_library += "		w_x = u_sol_x + t * (u_eol_x - u_sol_x)" + "\n"
function_library += "		w_y = u_sol_y + t * (u_eol_y - u_sol_y)" + "\n"
function_library += "" + "\n"
function_library += "		# measure the distance between u and w" + "\n"
function_library += "		squared_distance_from_u_to_w = (w_x - u_sol_x) ** 2 + (w_y - u_sol_y) ** 2" + "\n"
function_library += "" + "\n"
function_library += "		# if no nearest has been found yet or if the current detectable is nearest so far" + "\n"
function_library += "		if nearest_of_every_detectable == None or squared_distance_from_u_to_w < squared_distance_to_nearest:" + "\n"
function_library += "" + "\n"
function_library += "			# find the squared distance between w and v" + "\n"
function_library += "			squared_distance_from_w_to_v = (w_x - v_ctr_x) ** 2 + (w_y - v_ctr_y) ** 2" + "\n"
function_library += "" + "\n"
function_library += "			# if the Eucliean distance squared is less than the radius squared then the ray has collided with a detectable" + "\n"
function_library += "			if (squared_distance_from_w_to_v <= v_rad ** 2):" + "\n"
function_library += "" + "\n"
function_library += "				nearest_of_every_detectable = detectable[0]" + "\n"
function_library += "				squared_distance_to_nearest = squared_distance_from_u_to_w" + "\n"
function_library += "				extra_data_for_nearest = detectable[2]" + "\n"
function_library += "" + "\n"
function_library += "	return (nearest_of_every_detectable, sqrt(squared_distance_to_nearest), extra_data_for_nearest)" + "\n"
function_library += "" + "\n"
if switch_to_turn_off_debug:
	function_library += "def print(*objects, sep=None, end=None, file=None, flush=False):" + "\n"
	function_library += "	pass" + "\n"


# initialize pygame
pygame.init()

# initialize the font module
pygame.font.init()

# load the font and update the caption surfaces
small_font = pygame.font.Font('Assets/font_asset.ttf', 8)
large_font = pygame.font.Font('Assets/font_asset.ttf', 32)

# open the source file for the first player
try:
	file_hndl = open(name_of_source_file_for_player_0, "r")
except:
	print()
	print("ERROR: '", name_of_source_file_for_player_0,"' could not be opened.", sep="")
	exit()
file_data = file_hndl.read()
global name_of_player_0
name_of_player_0 = "UNTITLED"
for line in file_data.splitlines():
	if len(line) >= 6 and (line[0:5] == "# -> " or line[0:5] == "# -? "):
		name_of_player_0 = ((line[5:])[:14]).upper()
		if line[0:5] == "# -? ":
			player_0_fsm_hidden = True
		break	
if not player_0_fsm_hidden:		
	player_0_fsm_graph = create_an_fsm_graph(file_data)
file_data = function_library + file_data
file_hndl.close()

# append the function library and write a new source file
file_hndl = open("complete_behaviour_definition_0.py", "w")
file_hndl.write(file_data)
file_hndl.close()

# import the source file for the first player
import complete_behaviour_definition_0 as player_0_controller

# open the source file for the second player
try:
	file_hndl = open(name_of_source_file_for_player_1, "r")
except:
	print()
	print("ERROR: '", name_of_source_file_for_player_1,"' could not be opened.", sep="")
	if os.path.exists("complete_behaviour_definition_0.py"):
	  os.remove("complete_behaviour_definition_0.py")	
	exit()
file_data = file_hndl.read()
global name_of_player_1
name_of_player_1 = "UNTITLED"
for line in file_data.splitlines():
	if len(line) >= 6 and (line[0:5] == "# -> " or line[0:5] == "# -? "):
		name_of_player_1 = ((line[5:])[:14]).upper()
		if line[0:5] == "# -? ":
			player_1_fsm_hidden = True
		break	
if not player_1_fsm_hidden:		
		player_1_fsm_graph = create_an_fsm_graph(file_data)
file_data = function_library + file_data
file_hndl.close()

# append the function library and write a new source file
file_hndl = open("complete_behaviour_definition_1.py", "w")
file_hndl.write(file_data)
file_hndl.close()

# import the source file for the second player
import complete_behaviour_definition_1 as player_1_controller

# remove the complete behaviour definition files if they exist
if os.path.exists("complete_behaviour_definition_0.py"):
  os.remove("complete_behaviour_definition_0.py")
if os.path.exists("complete_behaviour_definition_1.py"):
  os.remove("complete_behaviour_definition_1.py")
  
# begin the program by calling the main method
if __name__ == "__main__":
	main()

