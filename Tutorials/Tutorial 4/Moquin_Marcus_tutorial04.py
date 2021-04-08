import pygame
import time
import sys
import random

from pygame.locals import *

class Asteroids:
    def __init__(self, position, size):
        self.position = position
        self.size = (size, size)
        self.velocity = (random.randint(100, 160), random.randint(100, 160))
        self.img = pygame.transform.scale(pygame.image.load("assets/Asteroid_{}.png".format(random.randint(1, 4))).convert_alpha(), (self.size[0], self.size[1]))
        self.rect = self.img.get_rect()

    def render(self, screen):
        screen.blit(self.img, self.position)

class Ship:
    width = 15
    height = 35
    velocity = 200
    angle = 0
    is_moving = False
    def __init__(self, position):
        self.position = position
        self.img = pygame.transform.scale(pygame.image.load("assets/Spaceship.png").convert_alpha(), (self.width, self.height))
        self.rect = self.img.get_rect()

    def render(self, screen):
        image = pygame.transform.rotate(self.img, self.angle)
        screen.blit(image, self.position)

    def rotate(self, screen, angle):
        if angle == "left":
            if self.angle == 0:
                self.angle = 90
            elif self.angle == 90:
                self.angle = 180
            elif self.angle == 180:
                self.angle = 270
            else:
                self.angle = 0
        elif angle == "right":
            if self.angle == 0:
                self.angle = 270
            elif self.angle == 270:
                self.angle = 180
            elif self.angle == 180:
                self.angle = 90
            else:
                self.angle = 0
        rotated = pygame.transform.rotate(self.img, self.angle)
        screen.blit(rotated, self.position)

# Initializing #

def initialize():
    screen = initialize_pygame()
    return initialize_data(screen)

def initialize_pygame():
    pygame.init()
    pygame.key.set_repeat(1000)
    pygame.display.set_caption("Asteroids")
    return pygame.display.set_mode((1200, 800))

def initialize_data(screen):
    game_data = {"screen": screen,
    "asteroids": [],
    "ship": [],
    "is_running": True}

    locations = [(50, 50), (50, 400), (50, 750), (1150, 50), (1150, 400), (1150, 750), (600, 50), (600, 750)]
    for i in range(8):
        loc = random.choice(locations)
        locations.remove(loc)
        game_data["asteroids"].append( Asteroids(loc, random.randint(30, 50)) )
    
    game_data["ship"].append( Ship((600, 400)) )

    return game_data

# Handling Inputs #

def handle_input(game_data):
    for event in pygame.event.get():
        for ship in game_data["ship"]:
            if event.type == KEYDOWN:
                if event.key == K_LEFT:
                    ship.rotate(game_data["screen"], "left")
                if event.key == K_RIGHT:
                    ship.rotate(game_data["screen"], "right")
                if event.key == K_UP:
                    ship.is_moving = True

# Update/Render #

def render(game_data):

    game_data["screen"].fill((0, 0, 0))

    for asteroid in game_data["asteroids"]:
        asteroid.render(game_data["screen"])
    
    for ship in game_data["ship"]:
        ship.render(game_data["screen"])

def update(game_data):

    delta = 1 / 60
    
    for asteroid in game_data["asteroids"]:
        handle_asteroid_collisions(game_data, asteroid)
        (x, y) = asteroid.position
        (velx, vely) = asteroid.velocity

        x += velx*delta

        if (x < 0) or (x > game_data["screen"].get_width() - asteroid.size[0]):
            velx *= -1
        
        y += vely*delta

        if (y < 0) or (y > game_data["screen"].get_height() - asteroid.size[1]):
            vely *= -1
        
        asteroid.position = (x, y)
        asteroid.velocity = (velx, vely)
    
    for ship in game_data["ship"]:
        if ship.is_moving:
            (x, y) = ship.position
            angle = ship.angle

            if angle == 0:
                y = y - ship.velocity*delta
            if angle == 90:
                x = x - ship.velocity*delta
            if angle == 180:
                y += ship.velocity*delta
            if angle == 270:
                x += ship.velocity*delta
            
            if (x < ship.width*-1):
                x += game_data["screen"].get_width()
            if (x > game_data["screen"].get_width()):
                x = 0
            if (y < ship.height*-1):
                y += game_data["screen"].get_height()
            if (y > game_data["screen"].get_height()):
                y = 0

            ship.position = (x, y)

    pygame.display.flip()

# Others #

def handle_asteroid_collisions(game_data, asteroid):
    for ship in game_data["ship"]:
        (x, y) = ship.position
        if (ship.angle == 0) or (ship.angle == 180):
            (br_x, br_y) = (x + ship.width, y + ship.height)
        if (ship.angle == 90) or (ship.angle == 270):
            (br_x, br_y) = (x + ship.height, y + ship.width)
        (a_x, a_y) = asteroid.position
        (br_ax, br_ay) = (a_x + asteroid.size[0], a_y + asteroid.size[1])

        if (x > a_x) and (x < br_ax):
            if (y > a_y) and (y < br_ay):
                game_data["is_running"] = False

def spawnAsteroids(game_data):
    locations = [(50, 50), (50, 400), (50, 750), (1150, 50), (1150, 400), (1150, 750), (600, 50), (600, 750)]
    for i in range(2, 4):
        loc = random.choice(locations)
        locations.remove(loc)
        game_data["asteroids"].append( Asteroids(loc, random.randint(30, 50)) )

# Main Function #

def main():

    game_data = initialize()
    spawnTime = 0

    clock = pygame.time.Clock()

    while game_data["is_running"]:
        handle_input(game_data)
        update(game_data)
        render(game_data)
        clock.tick(60)
        spawnTime += 0.01
        if spawnTime > 2:
            spawnAsteroids(game_data)
            spawnTime = 0
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()