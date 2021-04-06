import pygame
import random
import math
import time

from pygame.locals import *

FONTS = {}

SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 800

frame_rate = 60
delta_time = 1 / frame_rate

game_data = {}
game_data["starting_screen"] = True

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Enemies: # This has no purpose except for the fact I can do Enemies.waitSpawnEnemies timer.
    waitSpawnEnemies = pygame.USEREVENT + 0
    def __init__(self):
        super().__init__()

class Spaceship:
    WIDTH = 50
    HEIGHT = 70
    CURRENT_ACTION = "NA"
    VELOCITY = 400
    EntityType = "ship"
    def __init__(self, position):
        self.position = position
        self.shooting = False
        self.img = pygame.transform.scale(pygame.image.load("assets/Spaceship.png"), (Spaceship.WIDTH, Spaceship.HEIGHT))
        self.rect = self.img.get_rect(center = self.position)

    def render(self, screen):
        image = pygame.transform.rotate(self.img, 360) # rotating 360 degrees to show that I know how to rotate but it changes nothing
        screen.blit(image, self.position)
        self.rect = image.get_rect(center = self.position)

    def move(self, position):
        self.position = position
        self.rect = self.img.get_rect(center = self.position)

class Bullet:
    width = 3
    height = 3
    EntityType = "bullet"
    def __init__(self, position):
        self.position = position
        self.velocity = 900
    
    def render(self, screen):
        pygame.draw.rect(screen, (255, 0, 0), Rect(self.position[0], self.position[1], 3, 3))

class GameCircle:
    def __init__(self, position, radius, colour, health):
        self.position = position
        self.radius = radius
        if radius == 60:
            self.velocity = 288
            self.interest = 100 # This decreases by 1 every 1.5 seconds (unless 40 guards on screen) and will spawn 2-3 guards. The Sun can't be affected until it's minibosses and guards are dead.
        else:
            if radius == 40:
                if colour == (255, 0, 0):
                    self.velocity = (random.randint(200, 400), random.randint(-400, -200))
                if colour == (0, 255, 0):
                    self.velocity = (random.randint(-400, -200), random.randint(-400, -200))
                if colour == (0, 0, 255):
                    self.velocity = (random.randint(-400, -200), random.randint(-400, -200))
                if colour == (255, 255, 255):
                    self.velocity = (random.randint(-400, -200), random.randint(-400, -200))
            self.velocity = (random.randint(-400, 400), random.randint(-400, 400))
            self.interest = -1
        self.color = colour
        self.colour = colour #yes, there are 2 color checks, although color will remain the same throughout and colour will change as the circle is collided with.
        self.currentHealth = health
        self.Health = health

    def render(self, screen):
        pygame.draw.circle(screen, (self.color), self.position, self.radius)
        self.colour = self.color

class MovingLine:
    def __init__(self):
        self.segments = []
        self.reset = True
        self.y = 0

    def render(self, screen):
        for seg in self.segments:
            if self.y >= SCREEN_HEIGHT:
                self.y = 0
                self._update_line_segments()
            else:
                pygame.draw.aaline(screen, (255, 255, 255), (seg[0][0], self.y), (seg[1][0], self.y))

    def _update_line_segments(self): #man i really surprised myself with this

        self.reset == False

        self.segments = []

        first_start_x = random.randint(0, SCREEN_WIDTH - 100)
        hole_size = random.randint(0, 100) + 150
        if SCREEN_WIDTH - (first_start_x + hole_size) < 150:
            second_start_x = first_start_x + 150
        else:
            second_start_x = first_start_x + hole_size

        self.segments.append( ((0, 0), (first_start_x, 0)))
        self.segments.append( ((second_start_x, 0), (SCREEN_WIDTH, 0)))

def main():
    # initialize pygame
    pygame.init()

    # create the window and set the caption of the window
    screen = pygame.display.set_mode( (SCREEN_WIDTH, SCREEN_HEIGHT) )
    pygame.display.set_caption('Scuffed Space Invaders')

    # create a clock
    clock = pygame.time.Clock()

    initialize()

    # the game loop is a postcondition loop controlled using a Boolean flag
    while not game_data["quit_game"]:
        handle_inputs()
        update(delta_time) 
        render(screen)
            
        # enforce the minimum frame rate
        clock.tick(frame_rate)
        game_data["FPS"] = math.floor(clock.get_fps())

def initialize():
    # Setup all of our initial data for the game
    game_data["won_game"] = False
    game_data["quit_game"] = False
    game_data["lost_game"] = False
    game_data["lines"] = []
    game_data["circles"] = []
    game_data["spaceship"] = []
    game_data["destroyed"] = 0
    game_data["bullets"] = []
    game_data["FPS"] = 0

    FONTS["gameover"] = pygame.font.SysFont("Arial", 72)
    FONTS["gameover_text"] = pygame.font.SysFont("Arial", 20)
    FONTS["mainhealth"] = pygame.font.SysFont("Calibri", 20)
    FONTS["Arial"] = pygame.font.SysFont("Arial", 30)
    FONTS["sArial"] = pygame.font.SysFont("Arial", 20)

    game_data["lines"].append(MovingLine())
    game_data["circles"].append( GameCircle( (SCREEN_WIDTH // 2, 65), 60, (255, 255, 0), 50000) ) # main circle
    pygame.time.set_timer(Enemies.waitSpawnEnemies, 500) # setting a timer for new enemies to spawn when interest level is above -1

    game_data["spaceship"].append( Spaceship( ((SCREEN_WIDTH // 2) - 25, 650) ))

def reset():
    global game_data
    game_data = {}
    initialize()
    game_data["starting_screen"] = False

def handle_inputs():
    # look in the event queue for the quit event
    for event in pygame.event.get():
        if event.type == Enemies.waitSpawnEnemies:
            for circle in game_data["circles"]:
                if circle.interest > 0:
                    if len(game_data["circles"]) < 40:
                        circle.interest = circle.interest - 1
                        for i in range(random.randint(2, 3)):
                            game_data["circles"].append( GameCircle( (SCREEN_WIDTH // 2, SCREEN_HEIGHT - SCREEN_HEIGHT + 35), 10, (255, 255, 255), 5000))
                        pygame.time.set_timer(Enemies.waitSpawnEnemies, 1500)
                if circle.interest == 0:
                    if len(game_data["circles"]) == 1:
                        circle.interest = circle.interest - 1 # This stops all spawning - This will also spawn the minibosses (which also can't be hit until everything else is dead.)
                        for i in range(4):
                            if i == 0:
                                game_data["circles"].append( GameCircle((50, 50), 40, (255, 0, 0), 10000) )
                            if i == 1:
                                game_data["circles"].append( GameCircle((50, 350), 40, (0, 255, 0), 10000))
                            if i == 2:
                                game_data["circles"].append( GameCircle((SCREEN_WIDTH - 50, 50), 40, (0, 0, 255), 10000))
                            if i == 3:
                                game_data["circles"].append( GameCircle((SCREEN_WIDTH - 50, 350), 40, (255, 255, 255), 10000))
                        circle.currentHealth = circle.Health
        if event.type == QUIT:
            game_data["quit_game"] = True
        if event.type == KEYDOWN:
            if game_data["starting_screen"] or game_data["won_game"]:
                if not event.key == K_ESCAPE:
                    reset()
                else:
                    game_data["won_game"] = False
                    game_data["starting_screen"] = False
                    game_data["quit_game"] = True
            if event.key == K_ESCAPE:
                game_data["quit_game"] = True
            if event.key == K_r:
                reset()
            for ship in game_data["spaceship"]:
                if event.key == K_LEFT:
                    ship.CURRENT_ACTION = "L"
                if event.key == K_RIGHT:
                    ship.CURRENT_ACTION = "R"
                if event.key == K_SPACE:
                    ship.shooting = True
        if event.type == KEYUP:
            for ship in game_data["spaceship"]:
                if ship.CURRENT_ACTION == "L":
                    if event.key == K_LEFT:
                        ship.CURRENT_ACTION = "NA"
                elif ship.CURRENT_ACTION == "R":
                    if event.key == K_RIGHT:
                        ship.CURRENT_ACTION = "NA"
                if ship.shooting == True:
                    if event.key == K_SPACE:
                        ship.shooting = False
    pygame.mouse.set_visible(False)

########### DATA UPDATES ###########    
def update(delta):

    reset = False
    # Rotate each line, and see if they reset at all
    #for line in game_data["lines"]:
    #    line_did_reset = line.rotate()
    if not game_data["lost_game"]:
        for line in game_data["lines"]:
            if line.reset:
                line._update_line_segments()
                reset = False
            if not line.reset:
                y = line.y
                if (game_data["destroyed"] == 0) or (game_data["destroyed"] <= 75):
                    y += 200*delta
                elif game_data["destroyed"] <= 110 and game_data["destroyed"] > 75:
                    y += 300*delta
                else:
                    y += 400*delta
                if (y > SCREEN_HEIGHT):
                    reset = True
                line.y = y
            line.reset = reset

    for circle in game_data["circles"]:
        update_bullet_collision(circle)

        if circle.radius == 60: #main circle, it shifts
            (x, y) = circle.position
            vel = circle.velocity

            x += vel*delta

            if (x <= circle.radius) or (x >= pygame.display.get_surface().get_width() - circle.radius):
                vel *= -1
            
            circle.position = (x, y)
            circle.velocity = vel
        else:
            (x, y) = circle.position
            (velx, vely) = circle.velocity

            x += velx*delta

            if (x <= circle.radius) or (x >= pygame.display.get_surface().get_width() - circle.radius):
                velx *= -1

            y += vely*delta
            
            if (y <= circle.radius) or (y >= 400 - circle.radius):
                vely *= -1

            circle.position = (x, y)
            circle.velocity = (velx, vely)

    for ship in game_data["spaceship"]:
        update_ship_collisions(ship)

        (x, y) = ship.position
        
        if ship.CURRENT_ACTION == 'NA':
            ship.position = ship.position
        elif ship.CURRENT_ACTION == 'R':
            if x + ship.VELOCITY*delta > pygame.display.get_surface().get_width() - ship.WIDTH:
                x += 0
            else:
                x += ship.VELOCITY*delta

        elif ship.CURRENT_ACTION == 'L':
            if x + ((ship.VELOCITY*delta) * -1) < 0:
                x += 0
            else:
                x += (ship.VELOCITY*delta) * -1

        ship.move((x, y))
        if ship.shooting == True:
            fire_Bullet(ship)

    for bullet in game_data["bullets"]:

        (x, y) = bullet.position

        y = y - bullet.velocity*delta + 1
        
        if (y <= 0):
            game_data["bullets"].remove(bullet)

        bullet.position = (x, y)

def update_ship_collisions(spaceship):
    if not game_data["won_game"]:
        for line in game_data["lines"]:
            for segment in line.segments:
                if detect_collision_line_rect(segment, spaceship):
                    game_data["lost_game"] = True
                    break
        return

def update_bullet_collision(circle):
    if not game_data["won_game"]:
        for bullet in game_data["bullets"]:
            if detect_collision_bullet_circ(bullet, circle):
                if circle.radius == 60:
                    if len(game_data["circles"]) == 1:
                        circle.currentHealth = circle.currentHealth - 25
                        if circle.currentHealth <= 0:
                            game_data["destroyed"] += 1
                            if circle in game_data["circles"]:
                                game_data["circles"].remove(circle)
                            game_data["won_game"] = True
                elif circle.radius == 40:
                    if len(game_data["circles"]) <= 5:
                        circle.currentHealth = circle.currentHealth - 25
                        if circle.currentHealth <= 0:
                            game_data["destroyed"] += 1
                            if circle in game_data["circles"]:
                                game_data["circles"].remove(circle)
                else:
                    circle.currentHealth = circle.currentHealth - 75
                    if circle.currentHealth <= 0:
                        game_data["destroyed"] += 1
                        if circle in game_data["circles"]:
                            game_data["circles"].remove(circle)

########### RENDERING ###########

def render_WinningScreen(screen):
    wormhole_img = pygame.transform.scale(pygame.image.load("assets/wormhole.png"), (SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.blit(wormhole_img, (0, 0))

    title = pygame.font.SysFont("Arial", 75).render("Scuffed Space Invaders", True, (255, 255, 0))
    screen.blit(title, ((SCREEN_WIDTH // 2) - 320, 10))

    congrats = pygame.font.SysFont("Arial", 35).render("CONGRATULATIONS!", True, (255, 0, 0))
    screen.blit(congrats, ((SCREEN_WIDTH // 2) - 130, 100))

    youwon = FONTS["gameover"].render("You Won!", True, (255, 0, 0)) # ignore the fact i'm using the gameover font, no need to create another font when i have this one :)
    screen.blit(youwon, ((SCREEN_WIDTH // 2 - 120), (SCREEN_HEIGHT // 2 - 100)))

    winner_text_1 = FONTS["gameover_text"].render("You beat the Sun and you can now return home!", True, (255, 255, 255))
    winner_text_2 = FONTS["gameover_text"].render("You killed {} enemies!".format(game_data["destroyed"]), True, (255, 255, 255))

    screen.blit(winner_text_1, ((SCREEN_WIDTH // 2 - 170), (SCREEN_HEIGHT // 2 )))
    screen.blit(winner_text_2, ((SCREEN_WIDTH // 2 - 70), (SCREEN_HEIGHT // 2 + 50)))

    play_again = pygame.font.SysFont("Arial", 50).render("Want to play again?", True, (255, 255, 255))
    play_again_2 = pygame.font.SysFont("Arial", 30).render("Press any key to restart", True, (255, 255, 255))

    screen.blit(play_again, ((SCREEN_WIDTH // 2 - 170), (SCREEN_HEIGHT // 2 + 200)))
    screen.blit(play_again_2, ((SCREEN_WIDTH // 2 - 120), (SCREEN_HEIGHT // 2 + 260)))

def render_InfoScreen(screen):
    pygame.draw.rect(screen, (0, 0, 0), Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))

    Font = pygame.font.SysFont("Arial", 20)

    title = pygame.font.SysFont("Arial", 75).render("Scuffed Space Invaders", True, (255, 255, 0))
    screen.blit(title, ((SCREEN_WIDTH // 2) - 320, 10))
    
    instructions = pygame.font.SysFont("Arial", 35).render("INSTRUCTIONS", True, (255, 0, 0))
    screen.blit(instructions, ((SCREEN_WIDTH // 2) - 115, 90))

    instruct_1 = pygame.font.SysFont("Arial", 20).render("Welcome to Scuffed Space Invaders! This is a game based off of Space Invaders, meaning it still has shooting targets and enemies", False, (255, 255, 255))
    instruct_2 = pygame.font.SysFont("Arial", 20).render("and stuff but it's just genuinely scuffed and looks nothing like the actual game itself. In this game, you start out as a rocket", False, (255, 255, 255))
    instruct_3 = pygame.font.SysFont("Arial", 20).render("against 1 enemy, the Sun. Your mission is to destroy the Sun before it destroys you with it's ability to ripple space and cause deathly", False, (255, 255, 255))
    instruct_4 = pygame.font.SysFont("Arial", 20).render("waves! The Sun didn't come alone however. The Sun starts out by having an interest level of 100%, and this decreases every 1.5 seconds.", False, (255, 255, 255))
    instruct_5 = pygame.font.SysFont("Arial", 20).render("An exception is when there are 40+ guards protecting the Sun. When the interest level increases, the Sun summons guards to protect", False, (255, 255, 255))
    instruct_6 = pygame.font.SysFont("Arial", 20).render("itself from your bullets. Once the interest level reaches 0, you must fight his mini-bosses. These are 4 guards that have significantly", False, (255, 255, 255))
    instruct_7 = pygame.font.SysFont("Arial", 20).render("more health than others and cannot be destroyed until all other guards are destroyed, just like the Sun. Once the Sun dies, you win!", False, (255, 255, 255))

    screen.blit(instruct_1, (10, 200))
    screen.blit(instruct_2, (10, 220))
    screen.blit(instruct_3, (10, 240))
    screen.blit(instruct_4, (10, 260))
    screen.blit(instruct_5, (10, 280))
    screen.blit(instruct_6, (10, 300))
    screen.blit(instruct_7, (10, 320))

    controls_1 = pygame.font.SysFont("Arial", 30).render("Here are your controls:", True, (255, 0, 0))
    controls_2 = pygame.font.SysFont("Arial", 20).render("LEFT_ARROW_KEY: Move Rocket Left                       RIGHT_ARROW_KEY: Move Rocket Right", False, (255, 255, 255))
    controls_3 = pygame.font.SysFont("Arial", 20).render("SPACE_BAR: Shoot                       R: Reset                       ESC: Quit", False, (255, 255, 255))

    screen.blit(controls_1, (SCREEN_WIDTH // 2 - 130, 400))
    screen.blit(controls_2, (150, 450))
    screen.blit(controls_3, (200, 500))

    ready = pygame.font.SysFont("Arial", 60).render("Are you ready?", True, (0, 190, 0))
    ready_2 = pygame.font.SysFont("Arial", 40).render("Press any key to begin!", True, (255, 255, 255))

    screen.blit(ready, (SCREEN_WIDTH // 2 - 170, 600))
    screen.blit(ready_2, (SCREEN_WIDTH // 2 - 175, 675))

def render_LostScreen(screen):
    pygame.draw.rect(screen, (0, 0, 0), Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))

    title = pygame.font.SysFont("Arial", 75).render("Scuffed Space Invaders", True, (255, 255, 0))
    screen.blit(title, ((SCREEN_WIDTH // 2) - 320, 10))

    gameover = FONTS["gameover"].render("Game Over", True, (255, 255, 255))
    gameover_text = FONTS["gameover_text"].render("Press 'r' to restart.", False, (255, 255, 255))

    text_img = gameover
    text_img_2 = gameover_text

    text_img_rect = text_img.get_rect(center = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
    text_img_rect_2 = text_img.get_rect(center = (SCREEN_WIDTH/2+90, SCREEN_HEIGHT/2+75))

    screen.blit(text_img, text_img_rect)
    screen.blit(text_img_2, text_img_rect_2)

def render_Health(screen, circle):
    health = (circle.currentHealth / circle.Health) * 100
    health_text = FONTS["mainhealth"].render(str(int(health)) + "%", True, (0, 0, 0))

    text_img = health_text

    if circle.radius == 60: #main circle, code the others later when you get there.
        if int(health) == 100:
            screen.blit(text_img, (circle.position[0] - 20, circle.position[1] - 10))
        elif int(health) <= 99 and int(health) >= 10:
            screen.blit(text_img, (circle.position[0] - 15, circle.position[1] - 10))
        elif int(health) <= 9:
            screen.blit(text_img, (circle.position[0] - 11, circle.position[1] - 10))
    elif circle.radius == 40:
        if int(health) == 100:
            screen.blit(text_img, (circle.position[0] - 20, circle.position[1] - 10))
        elif int(health) <= 99 and int(health) >= 10:
            screen.blit(text_img, (circle.position[0] - 15, circle.position[1] - 10))
        elif int(health) <= 9:
            screen.blit(text_img, (circle.position[0] - 11, circle.position[1] - 10))

def render(screen):
    screen.fill( (0,0,0) )
    
    if game_data["starting_screen"]:
        render_InfoScreen(screen)
    elif game_data["lost_game"]:
        render_LostScreen(screen)
    elif game_data["won_game"]:
        render_WinningScreen(screen)
    else:
        # Draw the line(s)
        for line in game_data["lines"]:
            line.render(screen)

        # Draw the circle(s)
        for circle in game_data["circles"]:
            if circle.currentHealth > 0: #don't render the circle if it's been destroyed.
                circle.render(screen)
                render_Health(screen, circle)

        for ship in game_data["spaceship"]:
            ship.render(screen)

        for bullet in game_data["bullets"]:
            bullet.render(screen)
    
        DrawInterestBar(screen, (200, 750), (600, 40))
        DrawStats(screen, (810, 745))
        DrawFPS(screen, (5, SCREEN_HEIGHT - 25))
    
    # update the display
    pygame.display.update()        

def DrawFPS(screen, pos):
    if game_data["FPS"] >= 60:
        fps = FONTS["sArial"].render(str(game_data["FPS"]), False, (0, 127, 0))
    elif game_data["FPS"] > 40 and game_data["FPS"] < 60:
        fps = FONTS["sArial"].render(str(game_data["FPS"]), False, (0, 255, 0))
    elif game_data["FPS"] > 20 and game_data["FPS"] < 40:
        fps = FONTS["sArial"].render(str(game_data["FPS"]), False, (255, 126, 0))
    else:
        fps = FONTS["sArial"].render(str(game_data["FPS"]), False, (255, 0, 0))
    
    screen.blit(fps, pos)

def DrawStats(screen, pos):
    enemies_text = FONTS["sArial"].render("Enemies Remaining: " + str(len(game_data["circles"])), False, (255, 255, 255))
    stat_text = FONTS["sArial"].render("Destroyed:" + str(game_data["destroyed"]), False, (255, 255, 255))
    
    screen.blit(enemies_text, pos)
    screen.blit(stat_text, (pos[0], pos[1] + 20))

def DrawInterestBar(screen, pos, size):
    for circle in game_data["circles"]:
        if circle.interest > 0:
            pygame.draw.rect(screen, (255, 255, 255), (*pos, *size), 1)
            innerPos = (pos[0]+3, pos[1]+3)
            progress = circle.interest/100
            innerSize = ((size[0]-6) * progress, size[1]-6)
            pygame.draw.rect(screen, (255, 0, 0), (*innerPos, *innerSize))

            interest_text = FONTS["Arial"].render("The Sun's Interest: " + str(circle.interest) + "%", True, (255, 255, 255))
            text_img = interest_text

            screen.blit(text_img, (375, 750))
        else:
            pygame.draw.rect(screen, (0, 0, 0), (*pos, *size), 1)

############## CODE HELPERS ################
def detect_collision_line_rect(line_points, rect):

    # I won't lie, I hate my life.
    # This took me 2 hours in one go and 3 days in total to figure out.
    # It was all so simple SadChamp

    (u_sol, u_eol) = line_points

    (u_sol_x, u_eol_x) = u_sol[0], u_eol[0]

    for line in game_data["lines"]:
        y = int(round(line.y))

    locations = { "center": rect.position, 
    "topleft": ((rect.position[0] - rect.WIDTH), (rect.position[1])), 
    "topright": ((rect.position[0] + rect.WIDTH), (rect.position[1])),
    "bottomleft": ((rect.position[0] - rect.WIDTH), (rect.position[1] + rect.HEIGHT)),
    "bottomright": ((rect.position[0] + rect.WIDTH), (rect.position[1] + rect.HEIGHT))
    }

    y_values_in_area = (int(rect.position[1]), int(rect.position[1] + rect.HEIGHT))
    x_values_in_area = (int(rect.position[0] - rect.WIDTH + 10), int(rect.position[0] + rect.WIDTH))

    for x in range(0, SCREEN_WIDTH):
        if (x < u_eol_x - 36) and (x > u_sol_x): # I was having issues with u_eol_x colliding a little far out of where it should be so I just reduced it a tad bit and it works fine.
            if x in range(x_values_in_area[0], x_values_in_area[1]):
                if y in range(y_values_in_area[0], y_values_in_area[1]):
                    return True
    return False

def detect_collision_bullet_circ(bullet, circle):

    bullet_center = ((bullet.position[0] + bullet.width), (bullet.position[1] - bullet.height))
    circle_center = ((circle.position[0]), (circle.position[1]))

    testX = circle_center[0]
    testY = circle_center[1]

    if (circle_center[0] < bullet_center[0]):
        testX = bullet_center[0]
    elif (circle_center[0] > bullet_center[0] + bullet.width):
        testX = bullet_center[0] + bullet.width
    
    if (circle_center[1] < bullet_center[1]):
        testY = bullet_center[1]
    elif (circle_center[1] > bullet_center[1] + bullet.height):
        testY = bullet_center[1] + bullet.height

    distX = circle_center[0] - testX
    distY = circle_center[1] - testY
    distance = math.sqrt( (distX*distX) + (distY*distY) )

    if (distance <= circle.radius):
        return True
    return False

def fire_Bullet(ship):
    game_data["bullets"].append( Bullet((ship.position[0] + 25, ship.position[1] - 30)) )

if __name__ == "__main__":
    main()


#### ---------------------------------------------------------------------------------------------------------------------- ####
############                                           CHANGELOG                                                    ############
#### ---------------------------------------------------------------------------------------------------------------------- ####

# 29/01/2021
#  - Start of game coding
#  - Added Spaceship Sprite
#  - Added event handlers for moving the ship left and right
#  - Added an event handler for resetting the game after game over
#  - Created a lost screen, added it to render func
#  - Created a function to check for ship collisions with the line
#  - Created a reset for the game

# 30/01/2021 (Start: 12:20pm - End: 4:05pm)
#  - Added Health and Health Display
#  - Made the main circle move back and forth to make it more difficult for shooting
#  - Added Line going from top to bottom (different speeds depending on # destroyed)
#  - Modified Collision Detection (sorta works?)
#  - Made it so the moving line does not interact with the targets

# 31/01/2021 (Start: 2:45am - End: 4:50am)
#  - OH MAN OH MAN I ADDED MY VERY OWN COLLISION DETECTION

# 31/01/2021 (Start: 11:55am - End: 1:07pm)
#  - Added Enemies and Minibosses with No Functionality

# 31/01/2021 (Start: 9:47pm - End: (01/02/2021) 1:58am)
#  - Added Functionality to Enemies and Minibosses
#  - Added Shooting
#  - Modified Collision Detection Function For Lines/Ship to Function with Lines/Bullets
#  - Added Bullet Collision
#  - Added Interest Bar at Bottom of Screen
#  - Added Statistics (Enemies Remaining/Destroyed) to Screen
#  - Added Health Display to Minibosses
#  - Added Health Functionality
#  - Added Information Screen (Pregame Screen)
#  - Added FPS counter
#  - Removed Interest Bar When Interest hits 0%
#  - Increased Size of Sun and Mini-Bosses
#  - Added Win Screen and Call for Win

# 01/02/2021
#  - End of Game Coding

#### ---------------------------------------------------------------------------------------------------------------------- ####
############                                           CHANGELOG                                                    ############
#### ---------------------------------------------------------------------------------------------------------------------- ####
