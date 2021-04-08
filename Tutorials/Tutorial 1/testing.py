import csv, pygame

from pygame.locals import *

def read_csv(file_name):
    return (list(csv.reader(open(file_name, "r"))))

def renderTiles(map_file, screen):
    for row in range(len(map_file)):
        for letter in range(len(map_file[row])):
            if map_file[row][letter] == "g":
                print("Row: " + str(row) + " & Block: GRASS & Color: " + tiles_file[1][3])
            else:
                print("Row: " + str(row) + " & Block: DIRT & Color: " + tiles_file[2][3])


pygame.init()
screen = pygame.display.set_mode((1024, 800))
map_file = read_csv("map.csv")
tiles_file = read_csv("tiles.csv")
renderTiles(map_file, screen)

pygame.draw.rect(screen, (100, 200, 250), Rect(0, 0, 1024, 800))