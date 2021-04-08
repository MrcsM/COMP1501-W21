#### ====================================================================================================================== ####
#############                                           IMPORTS                                                    #############
#### ====================================================================================================================== ####

from helper_functions import *
import pygame
import math
from enemy import *
import time

#### ====================================================================================================================== ####
#############                                         TOWER_CLASS                                                  #############
#### ====================================================================================================================== ####

class Tower:
    ''' Tower Class - represents a single Tower Object. '''
    # Represents common data for all towers - only loaded once, not per new Tower (Class Variable)
    tower_data = {}
    for tower in csv_loader("data/towers.csv"):
        tower_data[tower[0]] = { "sprite": tower[1], "damage": int(tower[2]), "rate_of_fire": int(tower[3]), "radius": int(tower[4]) }
    def __init__(self, tower_type, location, radius_sprite):
        ''' Initialization for Tower.
        Input: tower_type (string), location (tuple), radius_sprite (pygame.Surface)
        Output: A Tower Object
        '''
        self.name = tower_type
        self.sprite = pygame.image.load(Tower.tower_data[tower_type]["sprite"]).convert_alpha()
        self.radius_sprite = radius_sprite
        self.radius = Tower.tower_data[tower_type]["radius"]
        self.damage = Tower.tower_data[tower_type]["damage"]
        self.rate_of_fire = Tower.tower_data[tower_type]["rate_of_fire"]
        self.location = location
        self.isClicked = False
        self.attacking = None
        self.rotation = 0.0
        self.last_fire = 0

#### ====================================================================================================================== ####
#############                                       TOWER_FUNCTIONS                                                #############
#### ====================================================================================================================== ####

def update_tower(tower, map):
    if tower.attacking != None:
        if tower.last_fire > tower.rate_of_fire * 1000:
            tower.last_fire = 0

def render_tower(tower, screen, settings):
    ''' Helper function that renders a single provided Tower.
    Input: Tower Object, screen (pygame display), Settings Object
    Output: None
    '''
    rect = tower.sprite.get_rect(center=tower.location)
    if tower.rotation == 0.0:
        screen.blit(tower.sprite, rect)
    else:
        sprite = pygame.transform.rotate(tower.sprite, tower.rotation)
        screen.blit(sprite, rect)