#### ====================================================================================================================== ####
#############                                           IMPORTS                                                    #############
#### ====================================================================================================================== ####

from helper_functions import *
from settings import *
from shop import *
from tower import *
from enemy import *
from map import *
import pygame
import sys
import random
import math

#### ====================================================================================================================== ####
#############                                         INITIALIZE                                                   #############
#### ====================================================================================================================== ####

def initialize():
    ''' Initialization function - initializes various aspects of the game including settings, shop, and more.
    Input: None
    Output: game_data dictionary
    '''
    # Initialize Pygame
    pygame.init()
    pygame.display.set_caption("COMP 1501 - Tutorial 7: Tower Defense (TD) Base Code")

    # Initialize the Settings Object
    settings = Settings()

    # Initialize game_data and return it
    game_data = { "screen": pygame.display.set_mode(settings.window_size),
                  "current_currency": settings.starting_currency,
                  #"current_corruption": settings.corruption,
                  "current_wave": 1,
                  "wave_started": False,
                  "stay_open": True,
                  "selected_tower": None,
                  "clicked": False,
                  "settings": settings,
                  "towers": [],
                  "enemies": [],
                  "bullets": [],
                  "shop": Shop("Space", settings),
                  "map": Map(settings),
                  "clock": 0, 
                  "health": 1000,
                  "enemies_spawned": 0,
                  "max_spawn": 0}

    set_map(game_data["map"])

    return game_data

#### ====================================================================================================================== ####
#############                                           PROCESS                                                    #############
#### ====================================================================================================================== ####

def process(game_data):
    ''' Processing function - handles all form of user input. Raises flags to trigger certain actions in Update().
    Input: game_data dictionary
    Output: None
    '''
    for event in pygame.event.get():

        # Handle [X] press
        if event.type == pygame.QUIT:
            game_data["stay_open"] = False

        # Handle Mouse Button Down
        if event.type == pygame.MOUSEBUTTONDOWN:
            game_data["clicked"] = True

        # Handle Mouse Button Up
        if event.type == pygame.MOUSEBUTTONUP:
            game_data["clicked"] = False


#### ====================================================================================================================== ####
#############                                            UPDATE                                                    #############
#### ====================================================================================================================== ####

def update(game_data):
    ''' Updating function - handles all the modifications to the game_data objects (other than boolean flags).
    Input: game_data
    Output: None
    '''
    update_shop(game_data["shop"], game_data["current_currency"], game_data["settings"])
    game_data["tick"] = game_data["clock"].tick()

    if not game_data["wave_started"]:
        game_data["max_spawn"] = (game_data["current_wave"] * 5) + 25

    if game_data["shop"].clicked_item:
        if not game_data["clicked"]:
            x, y = pygame.mouse.get_pos()
            if check_location(game_data["map"], game_data["settings"], (x, y)):
                if x < 800:
                    tower = Tower(game_data["shop"].clicked_item, (x, y), None)
                    game_data["towers"].append(tower)
                    game_data["current_currency"] -= game_data["shop"].shop_data[game_data["shop"].clicked_item]["cost"]
                    game_data["shop"].clicked_item = None

    if not random.randrange(60):
        if game_data["enemies_spawned"] != game_data["max_spawn"]:
            types = list(Enemy.enemy_data.keys())
            chosen = random.choice(types)
            enemy = Enemy(chosen, (60, 20))
            if not game_data["wave_started"]:
                for i in range(2):
                    game_data["enemies"].append(enemy)
                    game_data["enemies_spawned"] = game_data["enemies_spawned"] + 2
            else:
                game_data["enemies"].append(enemy)
                game_data["enemies_spawned"] = game_data["enemies_spawned"] + 1
            game_data["wave_started"] = True
        
    for e in game_data["enemies"]:
        update_enemy(e, game_data["map"])
        if e.health <= 0:
            game_data["enemies"].remove(e)
            game_data["current_currency"] += e.enemy_data[e.name]["worth"]
        x, y, val = tileLoc(e.location)
        if val == "E":
            game_data["enemies"].remove(e)
            game_data["health"] -= 10

    for tower in game_data["towers"]:
        update_tower(tower, game_data["map"])
        tower.last_fire += game_data["tick"]

    if game_data["wave_started"] and (len(game_data["enemies"]) == 0):
        game_data["current_wave"] = game_data["current_wave"] + 1
        b4mines = game_data["current_currency"]
        for tower in game_data["towers"]:
            if tower.name == "Mine Lv. 1":
                game_data["current_currency"] += tower.tower_data[tower.name]["damage"]
        print("Mine(s) gave a total of: " + str(game_data["current_currency"] - b4mines) + " coins.")
        print("WAVE #" + str(game_data["current_wave"]) + " STARTING NOW!")
        game_data["enemies_spawned"] = 0
        game_data["wave_started"] = False

#### ====================================================================================================================== ####
#############                                            RENDER                                                    #############
#### ====================================================================================================================== ####

def DrawHealthBar(game_data, screen, pos, size):
    if game_data["health"] > 0:
        pygame.draw.rect(screen, (255, 255, 255), (*pos, *size), 1)
        innerPos = (pos[0]+3, pos[1]+3)
        progress = game_data["health"]/100
        innerSize = ((size[0]-6) * progress, size[1]-6)
        pygame.draw.rect(screen, (255, 0, 0), (*innerPos, *innerSize))

        interest_text = pygame.font.SysFont("Arial", 25).render("Health", True, (0, 0, 0))
        text_img = interest_text

        screen.blit(text_img, (280, 710))
    else:
        pygame.draw.rect(screen, (0, 0, 0), (*pos, *size), 1)

def render(game_data):
    ''' Rendering function - displays all objects to screen.
    Input: game_data
    Output: None
    '''
    render_map(game_data["map"], game_data["screen"], game_data["settings"])
    render_shop(game_data["shop"], game_data["screen"], game_data["settings"], game_data["current_currency"])
    for enemy in game_data["enemies"]:
        render_enemy(enemy, game_data["screen"], game_data["settings"])
    for tower in game_data["towers"]:
        render_tower(tower, game_data["screen"], game_data["settings"])

    for tower in game_data["towers"]:
        for enemy in game_data["enemies"]:
            delta = (tower.location[0] - enemy.location[0], tower.location[1] - enemy.location[1])
            norm = math.sqrt(delta[0] ** 2 + delta[1] ** 2)
            if norm < tower.radius:
                pygame.draw.line(pygame.display.get_surface(), (255, 0, 0), tower.location, enemy.location)
                if tower.last_fire > tower.rate_of_fire * 1000:
                    update_enemy(enemy, game_data["map"], None, tower.tower_data[tower.name]["damage"])
                    tower.last_fire = 0

                rads = math.atan2(delta[1], delta[0])
                degs = abs(((rads * 180) / math.pi)) + 90
                tower.rotation = degs

                break

    DrawHealthBar(game_data, game_data["screen"], (100, 700), (50, 40))
    pygame.display.update()

#### ====================================================================================================================== ####
#############                                             MAIN                                                     #############
#### ====================================================================================================================== ####

def main():
    ''' Main function - initializes everything and then enters the primary game loop.
    Input: None
    Output: None
    '''
    # Initialize all required variables and objects
    game_data = initialize()
    game_data["clock"] = pygame.time.Clock()

    # Begin Central Game Loop
    while game_data["stay_open"]:
        process(game_data)
        update(game_data)
        render(game_data)

    # Exit pygame and Python
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()