import sys, pygame, csv

pygame.init()

size = 800, 600

#specifying the file that will be the sprite's image
MOBLIN_IMAGE = "bear.png"
GOBLIN_IMAGE = "monkey.png"

def read_csv(file_name):
    return (list(csv.reader(open(file_name, "r"))))

#getting tiles and color
tiles = read_csv("tiles.csv")

for i in range(1, len(tiles)):
    if tiles[i][1] == "Grass":
        tile_color = tiles[i][3].split(",")
        grass = tuple((int(tile_color[0]), int(tile_color[1]), int(tile_color[2])))
    elif tiles[i][1] == "Dirt":
        tile_color = tiles[i][3].split(",")
        dirt = tuple((int(tile_color[0]), int(tile_color[1]), int(tile_color[2])))

white = 255, 255, 255
#creating a sprite group
all_sprites = pygame.sprite.Group()

#class for making Moblin sprites
class Moblin(pygame.sprite.Sprite):

    def __init__(self, color):
        super().__init__()

        self.image = pygame.image.load(MOBLIN_IMAGE).convert_alpha()

        self.image.set_colorkey(white)
        self.image = pygame.transform.scale(self.image, (40, 40))

        self.rect = self.image.get_rect()

#class for making Goblin sprites
class Goblin(pygame.sprite.Sprite):

    def __init__(self, color):
        super().__init__()

        self.image = pygame.image.load(GOBLIN_IMAGE).convert_alpha()

        self.image.set_colorkey(white)
        self.image = pygame.transform.scale(self.image, (40, 40))

        self.rect = self.image.get_rect()

#rendering all of the entities
def renderEntities(entity_file, screen): #0 name, 1 color, 2 speed, 3 row, 4 col
    for i in range(1, len(entity_file)):
        for i2 in range(len(entity_file[i])):
            if entity_file[0][i2] == "Name":
                name = entity_file[i][i2]
            elif entity_file[0][i2] == "colour":
                color_split = entity_file[i][i2].split(",")
                color = tuple((int(color_split[0]), int(color_split[1]), int(color_split[2])))
            elif entity_file[0][i2] == "speed":
                speed = float(entity_file[i][i2])
            elif entity_file[0][i2] == "row":
                row = int(entity_file[i][i2])
            elif entity_file[0][i2] == "col":
                col = int(entity_file[i][i2])
        if name == "Moblin":
            moblin = Moblin(color)
            moblin.rect.x = (row * 40) - 40
            moblin.rect.y = (col * 40) - 40
            all_sprites.add(moblin)
        if name == "Goblin":
            goblin = Goblin(color)
            goblin.rect.x = (row * 40) - 40
            goblin.rect.y = (col * 40) - 40
            all_sprites.add(goblin)
        #updating sprite list and drawing
        all_sprites.update()
        all_sprites.draw(screen)

#rendering tiles, mapping out everything
def renderTiles(map_file, screen):
    for y in range(len(map_file)):
        for x in range(len(map_file[y])):
            if map_file[y][x] == "g":
                pygame.draw.rect(screen, grass, (x*40,y*40,40,40))
            elif map_file[y][x] == "d":
                pygame.draw.rect(screen, dirt, (x*40,y*40,40,40))
    renderEntities(entities, screen)
    pygame.display.flip()

screen = pygame.display.set_mode(size)
map_file = read_csv("map.csv")
entities = read_csv("entities.csv")

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

    renderTiles(map_file, screen)


