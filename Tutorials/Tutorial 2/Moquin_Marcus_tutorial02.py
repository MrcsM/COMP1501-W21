#### ====================================================================================================================== ####
#############                                           IMPORTS                                                    #############
#### ====================================================================================================================== ####

import pygame
import time
import random
import sys

from pygame.locals import *

#### ====================================================================================================================== ####
#############                                         INITIALIZE                                                   #############
#### ====================================================================================================================== ####

def initialize():
    ''' Central Initialize function. Calls helper functions to initialize Pygame and then the game_data dictionary.
    handle_input: None
    Output: game_data Dictionary
    '''
    screen = initialize_pygame()
    return initialize_data(screen)

#############                                           HELPERS                                                    #############
#### ---------------------------------------------------------------------------------------------------------------------- ####

def initialize_data(screen):
    ''' Initializes the game_data dictionary. Includes: Entity Data and Logistical Data (is_open).
    Input: pygame screen
    Output: game_data Dictionary
    '''
    # Initialize game_data Dictionary
    game_data = {"screen": screen,
                "entities":[],
                'is_open': True}
    entities = []
    
    # Generate 'Ball' Entities
    for i in range(random.randint(3, 6)):
        entities.append({'type': 'ball',
                         'location': [random.randint(10, 790), random.randint(10, 790)],
                         'velocity': [random.randint(5, 15), random.randint(5, 15)]})
        
    # Generate 'Paddle' Entity
    entities.append({'type': 'paddle',
                     'location': [300, 780],
                     'velocity': 9,
                     'size': [200, 20],
                     'color': (255, 0, 0),
                     'current_action': 'NA'})
    game_data["entities"] = entities
    return game_data

def initialize_pygame():
    ''' Initializes Pygame.
    Input: None
    Output: pygame screen
    '''
    pygame.init()
    pygame.key.set_repeat(1, 1)
    return pygame.display.set_mode((800, 800))

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
            pressed = pygame.key.get_pressed()
            if pressed[pygame.K_ESCAPE]:
                handle_key_escape(game_data)
            elif pressed[pygame.K_LEFT] or pressed[pygame.K_a]:
                handle_key_left(game_data)
            elif pressed[pygame.K_RIGHT] or pressed[pygame.K_d]:
                handle_key_right(game_data)
            pass
    
        #added in to check for setting current action back to NA to stop it from moving by itself after a key press
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT or pygame.K_a or pygame.K_RIGHT or pygame.K_d:
                for entity in game_data['entities']:
                    if entity['type'] == "paddle":
                        entity['current_action'] = "NA"

#############                                           HANDLERS                                                   #############
#### ---------------------------------------------------------------------------------------------------------------------- ####

def handle_key_left(game_data):
    for entity in game_data['entities']:
        if entity['type'] == "paddle":
            entity['current_action'] = "L"
    return

def handle_key_right(game_data):
    for entity in game_data['entities']:
        if entity['type'] == "paddle":
            entity['current_action'] = "R"
    return

def handle_key_escape(game_data):
    game_data['is_open'] = False
    return
    
#### ====================================================================================================================== ####
#############                                            UPDATE                                                    #############
#### ====================================================================================================================== ####
    
def update(game_data):
    ''' Central Update function. Calls helper functions to update various types of Entities [ball, paddle].
    Input: game_data Dictionary
    Output: None
    '''
    for entity in game_data["entities"]:
        
        # Handle 'Ball' Entity
        if entity['type'] == 'ball':
            update_ball(entity, game_data)
            
        # Handle 'Paddle' Entity
        elif entity['type'] == 'paddle':
            update_paddle(entity)

#############                                           HELPERS                                                    #############
#### ---------------------------------------------------------------------------------------------------------------------- ####

def update_ball(entity, game_data):
    (x, y) = entity['location']
    (velx, vely) = entity['velocity']
    circles = []
    circles.append(pygame.draw.circle(pygame.display.get_surface(), (0, 0, 0), (x, y), 10))

    x += velx

    if (x < 0) or (x > pygame.display.get_surface().get_width()):
        velx *= -1
    
    y += vely

    if (y < 0) or (y > pygame.display.get_surface().get_height()):
        vely *= -1

    for ball in circles:
        for paddle in game_data['entities']:
            if paddle['type'] == "paddle":
                loc = paddle['location']
        if ((ball.collidepoint(loc))):
            print(entity['location'])
            entity['location'] = (x, y+5)
            entity['velocity'] = (velx, vely * -1)
            print("hit apparently: " + str(entity['location'])) #broken collision detection?

    entity['location'] = (x, y)
    entity['velocity'] = (velx, vely)

    pygame.draw.circle(pygame.display.get_surface(), (0, 255, 0), (x, y), 10)

    return

def update_paddle(entity):
    ''' Updates the location of a given 'Paddle' Entity based on 'current_action' flag.
    Input: entity Dictionary
    Output: None
    '''
    (x, y) = entity['location']
    (w, h) = entity['size']

    pygame.draw.rect(pygame.display.get_surface(), (0, 0, 0), (x, y, w, h))

    # Handle No Movement
    if entity['current_action'] == 'NA':
        entity['location'] = entity['location']
    elif entity['current_action'] == 'R':
        #bonus task 5 - boundary checking for paddle
        if x + entity['velocity'] > pygame.display.get_surface().get_width() - w:
            x += 0
        else:
            x += entity['velocity']

    elif entity['current_action'] == 'L':
        #bonus task 5 - boundary checking for paddle
        if x + (entity['velocity'] * -1) < 0:
            x += 0
        else:
            x += entity['velocity'] * -1

    entity['location'] = (x, y)

    pygame.draw.rect(pygame.display.get_surface(), entity['color'], (x, y, w, h))

    return

#### ====================================================================================================================== ####
#############                                            RENDER                                                    #############
#### ====================================================================================================================== ####

def render(game_data):
    ''' Central Render function. Calls helper functions to render various views.
    Input: game_data Dictionary
    Output: None
    '''
    render_raw_data(game_data)
    render_pygame(game_data)

#############                                           HELPERS                                                    #############
#### ---------------------------------------------------------------------------------------------------------------------- ####

def render_raw_data(game_data):
    balls = 0
    locations = []
    for entity in game_data['entities']:
        if entity['type'] == "ball":
            balls += 1
            locations.append(entity['type'] + "_" + str(balls) + ": " + str(entity['location']))
        else:
            locations.append(entity['type'] + ": " + str(entity['location']))
    #print("; ".join(locations))
    return

def render_pygame(game_data):
    game_data['screen'].fill((0, 0, 0))

    for entity in game_data['entities']:
        if entity['type'] == "ball":
            (x, y) = entity['location']
            pygame.draw.circle(game_data['screen'], (0, 255, 0), (x, y), 10)
        else:
            (x, y) = entity['location']
            (w, h) = entity['size']
            pygame.draw.rect(pygame.display.get_surface(), entity['color'], (x, y, w, h))

    pygame.display.update()
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
