#### ====================================================================================================================== ####
#############                                           IMPORTS                                                    #############
#### ====================================================================================================================== ####

import pygame
import time
import random
import sys
import math

#### ====================================================================================================================== ####
#############                                         INITIALIZE                                                   #############
#### ====================================================================================================================== ####

def initialize():
    ''' Central Initialize function. Calls helper functions to initialize Pygame and then the game_data dictionary.
    Input: None
    Output: game_data Dictionary
    '''
    screen = initialize_pygame()
    return initialize_data(screen)

#############                                           HELPERS                                                    #############
#### ---------------------------------------------------------------------------------------------------------------------- ####

def initialize_data(screen, num_cannon_balls=6, num_targets=1):
    ''' Initializes the game_data dictionary. Includes: Entity Data and Logistical Data (is_open).
    Input: pygame screen
    Output: game_data Dictionary
    '''
    # Initialize game_data Dictionary
    game_data = {"screen": screen,
                "background": pygame.transform.scale(pygame.image.load("resources/backgrounds/background.png").convert_alpha(), (1200, 800)),
                "entities": [],
                'is_open': True,
                "ammo": pygame.transform.scale(pygame.image.load("resources/cannonball/cannonball.png").convert_alpha(), (20,20)),
                "settings": {"max_targets": num_targets,
                             "max_cannon_balls": num_cannon_balls}}

    # Initialize Target Object(s)
    for _ in range(num_targets):
        game_data["entities"].append({"type": "target",
                                     "location": [random.randint(100, 400), random.randint(200, 600)],
                                     "size": (150, 150),
                                     "sprite": pygame.transform.scale(pygame.image.load("resources/targets/target_{}.png".format(random.randint(1, 4))).convert_alpha(), (150, 150)),
                                     "is_hit": False})

    # Initialize CannonBall Object(s)
    for _ in range(num_cannon_balls):
        game_data["entities"].append({"type": "cannonball",
                                     "location": [1100, 750],
                                     "velocity": None,
                                     "size": (25,25),
                                     "sprite": pygame.transform.scale(pygame.image.load("resources/cannonball/cannonball.png").convert_alpha(), (25,25)),
                                     "exists": False,
                                     "destroy": False})


    # Initialize Cannon Object(s)
    game_data["entities"].append({"type": "cannon",
                                 "location": [1100, 675], # Note: When rotating, you may need to adjust the location to (1300, 875) depending on your method
                                 "size": (200, 150),
                                 "sprite": pygame.transform.scale(pygame.image.load("resources/cannons/cannon_{}.png".format(random.randint(1, 4))).convert_alpha(), (200, 150)),
                                 "loaded": True,
                                 "is_firing": False,
                                 "angle": 45.00,
                                 "is_moving": False,
                                 "power": 10})

    # Initialize CrossHair Object
    game_data["entities"].append({"type": "crosshair",
                                 "location": pygame.mouse.get_pos(),
                                 "size": (100, 100),
                                 "has_moving": False,
                                 "sprite": pygame.transform.scale(pygame.image.load("resources/crosshairs/crosshair_{}.png".format(random.randint(1, 4))).convert_alpha(), (100, 100))})
    
    return game_data

def initialize_pygame():
    ''' Initializes Pygame.
    Input: None
    Output: pygame screen
    '''
    pygame.init()
    pygame.key.set_repeat(1, 1)
    return pygame.display.set_mode((1200, 800))

#### ====================================================================================================================== ####
#############                                           handle_input                                                    #############
#### ====================================================================================================================== ####

def handle_input(game_data):
    ''' Central handle_input function. Calls helper functions to handle various KEYDOWN events.
    Input: game_data Dictionary
    Output: None
    '''
    events = pygame.event.get()
    for event in events:
        
        # Handle [x] Press
        if event.type == pygame.QUIT:
            game_data['is_open'] = False
            
        # Handle Key Presses
        if event.type == pygame.KEYDOWN:
                
            # Handle 'Escape' Key
            if event.key == pygame.K_ESCAPE:
                handle_key_escape(game_data)

        # Handle Mouse Movement
        if event.type == pygame.MOUSEMOTION:
            handle_mouse_movement(game_data)

        # Handle Mouse Click
        if event.type == pygame.MOUSEBUTTONUP:
            handle_mouse_click(game_data)

#############                                           HANDLERS                                                   #############
#### ---------------------------------------------------------------------------------------------------------------------- ####

def handle_mouse_movement(game_data):
    for entity in game_data["entities"]:
        if entity["type"] == "cannon":
            entity["is_moving"] = True
        if entity["type"] == "crosshair":
            entity["has_moving"] = True
    return
        
def handle_mouse_click(game_data):
    for entity in game_data["entities"]:
        if entity["type"] == "cannon":
            entity["is_firing"] = True
        if entity["type"] == "cannonball":
            if entity["exists"] == False:
                entity["exists"] = True
                break
    return

def handle_key_escape(game_data):
    ''' Handles the Escape KEYDOWN event. Sets a flag for 'is_open' to 'False'.
    Input: game_data Dictionary
    Output: None
    '''
    game_data['is_open'] = False

#### ====================================================================================================================== ####
#############                                            UPDATE                                                    #############
#### ====================================================================================================================== ####
    
def update(game_data):
    """Central Update function. Calls helper functions to update various types of Entities [crosshair, target, cannon, cannonball].
    Input: game_data Dictionary
    Output: None
    """
    for entity in game_data["entities"]:
        if entity["type"] == "crosshair" and entity["has_moving"] == True:
            update_cross_hair(entity)
        if entity["type"] == "cannon" and (entity["is_moving"] or entity["is_firing"]):
            update_cannon(entity, game_data["entities"])
        if entity["type"] == "cannonball" and entity["exists"] == True:
            cannon_entity = None
            target_entity = None
            for more_entities in game_data["entities"]:
                if more_entities["type"] == "target":
                    target_entity = more_entities
                elif more_entities["type"] == "cannon":
                    cannon_entity = more_entities
            update_cannon_ball(entity, cannon_entity, target_entity)
        if entity["type"] == "target":
            update_target(entity)
            

#############                                           HELPERS                                                    #############
#### ---------------------------------------------------------------------------------------------------------------------- ####

def update_cross_hair(entity):
    if entity["has_moving"]:
        (x, y) = pygame.mouse.get_pos()
        x = x - entity["size"][0] // 2
        y = y - entity["size"][1] // 2
        entity["location"] = (x, y)
    return

def update_cannon(entity, all_entities):
    new_angle = - (math.atan2(entity["location"][1] - pygame.mouse.get_pos()[1], entity["location"][0] - pygame.mouse.get_pos()[0])) * 180/math.pi + 270
    entity["angle"] = new_angle
    return

def update_cannon_ball(entity, cannon_entity, target_entity):
    if entity["destroy"]:
        entity["location"] = (1100, 750)
        entity["velocity"] = None
        entity["exists"] = False
        entity["destroy"] = False
    else:
        if entity["velocity"] == None:
            new_angle = math.atan2(pygame.display.get_surface().get_height() - pygame.mouse.get_pos()[1], pygame.display.get_surface().get_width() - pygame.mouse.get_pos()[0])
            (x, y) = math.cos(new_angle), math.sin(new_angle)
            entity["velocity"] = (x, y)
        else:
            (x, y) = entity["location"]
            (velx, vely) = entity["velocity"]

            x += 1 - velx * 10

            if (x < 0) or (x > pygame.display.get_surface().get_width()):
                entity["destroy"] = True
            
            y += 0.5 - vely * 10

            if (y < 0) or (y > pygame.display.get_surface().get_height()):
                entity["destroy"] = True

            entity['location'] = (x, y)

            # Start of collision detection
            (ball_x, ball_y) = entity["location"]
            (target_x, target_y) = target_entity["location"] #top left
            (target_brx, target_bry) = target_entity["location"][0] + target_entity["size"][0], target_entity["location"][1] + target_entity["size"][1] #bottom right

            if (ball_x > target_x) and (ball_x < target_brx):
                if (ball_y > target_y) and (ball_y < target_bry):
                    target_entity["is_hit"] = True
                    entity["destroy"] = True
    return


def update_target(entity):
    if entity["is_hit"]:
        entity["is_hit"] = False
        entity["location"] = [random.randint(100, 400), random.randint(200, 600)]
    return

#### ====================================================================================================================== ####
#############                                            RENDER                                                    #############
#### ====================================================================================================================== ####

def render(game_data):
    ''' Central Render function. Calls helper functions to render various views.
    Input: game_data Dictionary
    Output: None
    '''
    game_data["screen"].blit(game_data["background"], (0, 0))
    
    for entity in game_data["entities"]:
        if entity['type'] == 'cannon':
            render_cannon(game_data, entity)
        elif entity['type'] == 'cannonball':
            render_cannon_ball(game_data, entity)
        elif entity['type'] == 'target':
            render_target(game_data, entity)
        elif entity['type'] == 'crosshair':
            render_crosshair(game_data, entity)
            
    pygame.display.flip()

#############                                           HELPERS                                                    #############
#### ---------------------------------------------------------------------------------------------------------------------- ####

def render_target(game_data, entity):
    game_data["screen"].blit(entity["sprite"], entity["location"])
    return

def render_crosshair(game_data, entity):
    pygame.mouse.set_visible(False)
    (x, y) = entity["location"]
    x = x - entity["size"][0] // 2
    y = y - entity["size"][1] // 2
    entity["location"] = (x, y)
    game_data["screen"].blit(entity["sprite"], entity["location"])
    return

def render_cannon(game_data, entity):
    rotated = pygame.transform.rotate(entity["sprite"], entity["angle"])
    game_data["screen"].blit(rotated, entity["location"])
    return

def render_cannon_ball(game_data, entity):
    if entity["exists"]:
        game_data["screen"].blit(entity["sprite"], entity["location"])
    return

def render_ammo(game_data, ammo_list):
    ''' Replace this and the return statement with your code '''
    return

#### ====================================================================================================================== ####
#############                                             MAIN                                                     #############
#### ====================================================================================================================== ####

def main():
    ''' Main function of script - calls all central functions above via a Game Loop code structure.
    Input: None
    Output: None
    '''
    # Initialize Data and Pygame
    game_data = initialize()
    
    # Begin Central Game Loop
    while game_data['is_open']:
        handle_input(game_data)
        update(game_data)
        render(game_data)
        time.sleep(0.01) # Small Time delay to slow down frames per second
        
    # Exit Pygame and Python
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
