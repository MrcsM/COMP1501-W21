#### ====================================================================================================================== ####
#############                                           IMPORTS                                                    #############
#### ====================================================================================================================== ####

from helper_functions import *
from map import *
import pygame

#### ====================================================================================================================== ####
#############                                         ENEMY_CLASS                                                  #############
#### ====================================================================================================================== ####

class Enemy:
    ''' Enemy Class - represents a single Enemy Object. '''
    # Represents common data for all enemies - only loaded once, not per new Enemy (Class Variable)
    enemy_data = {}
    for enemy in csv_loader("data/enemies.csv"):
        enemy_data[enemy[0]] = { "sprite": enemy[1], "health": int(enemy[2]), "speed": int(enemy[3]), "worth": int(enemy[4]) }
    def __init__(self, enemy_type, location):
        ''' Initialization for Enemy.
        Input: enemy type (string), location (tuple of ints)
        Output: An Enemy Object
        '''
        self.size = 40
        self.name = enemy_type
        self.sprite = pygame.transform.scale(pygame.image.load(Enemy.enemy_data[enemy_type]["sprite"]).convert_alpha(), (self.size, self.size))
        self.health = Enemy.enemy_data[enemy_type]["health"]
        self.speed = Enemy.enemy_data[enemy_type]["speed"]
        self.location = location
        self.direction = "Down"
        self.visited = set()
        self.worth = Enemy.enemy_data[enemy_type]["worth"]
        self.spawn_time = 500
        

#### ====================================================================================================================== ####
#############                                       ENEMY_FUNCTIONS                                                #############
#### ====================================================================================================================== ####

def update_enemy(enemy, map, direction=None, damage=0):
    x, y, val = tileLoc(enemy.location)
    enemy.visited.add((x, y))
    for adjacent_delta in ((0, -1), (0, 1), (1, 0), (-1, 0)):
        adjacent = (x + adjacent_delta[0], y + adjacent_delta[1])
        if adjacent not in map.map_data or adjacent in enemy.visited: continue
        val = map.map_data[adjacent]["value"]
        if val in ("R", "E"):
            enemy.vel = adjacent_delta
    enemy.location = enemy.location[0] + enemy.vel[0], enemy.location[1] + enemy.vel[1]

    if enemy.vel[0] == 0:
        enemy.location = (enemy.location[0] // 40) * 40 + 20, enemy.location[1]
    if enemy.vel[1] == 0:
        enemy.location = enemy.location[0], (enemy.location[1] // 40) * 40 + 20

    if damage != 0:
        enemy.health = enemy.health - damage

    return 0

def render_enemy(enemy, screen, settings):
    ''' Helper function that renders a single provided Enemy.
    Input: Enemy Object, screen (pygame display), Settings Object
    Output: None
    '''
    rect = enemy.sprite.get_rect(center=enemy.location)
    screen.blit(enemy.sprite, rect)
