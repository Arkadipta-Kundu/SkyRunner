from typing import Any
import pygame
from pygame.locals import *
from pygame import mixer
import pickle
from os import path

pygame.mixer.pre_init(44100, -16, 2, 512)
mixer.init()
pygame.init()

clock = pygame.time.Clock()
fps = 60

screen_width = 800
screen_height = 800

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Skyrunner")


# define font
font = pygame.font.SysFont("Bauhaus 93", 70)
font_score = pygame.font.SysFont("Bauhaus 93", 30)


# define colours
white = (255, 255, 255)
blue = (0, 0, 255)
red = (255, 0, 0) 

# define game variables
tile_size = 40
game_over = 0
main_menu = True
level = 0
max_levels = 8
score = 0
# text_col = white


# load images
sun_img = pygame.image.load("img/sun.png")
bg_img = pygame.image.load("img/sky.png")
restart_img = pygame.image.load("img/restart_btn.png")
start_img = pygame.image.load("img/start_btn.png")
exit_img = pygame.image.load("img/exit_btn.png")


# load sounds
pygame.mixer.music.load("img/music.wav")
pygame.mixer.music.play(-1, 0.0, 5000)  # normalize the audio
coin_fx = pygame.mixer.Sound("img/coin.wav")
# coin_fx.set_volume(0.5)
jump_fx = pygame.mixer.Sound("img/jump.wav")
# jump_fx.set_volume(0.5)
game_over_fx = pygame.mixer.Sound("img/game_over.wav")
# game_over_fx.set_volume(0.5)


# function for adding text
def draw_text(text, font, color, x, y):
    img = font.render(text, True, color)
    screen.blit(img, (x, y))


# function for reset level
def reset_level(level):
    Player.reset(100, screen_height - 91)
    blob_group.empty()
    platform_group.empty()
    lava_group.empty()
    coin_group.empty()
    exit_group.empty()

    # load in level data and create wirld
    if path.exists(f"level{level}_data"):
        pickled_data = open(f"level{level}_data", "rb")
        world_data = pickle.load(pickled_data)
    world = World(world_data)

    return world


class Button:
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.clicked = False

    def draw(self):
        action = False  # buttion clicked ?

        # Get mouse position (check if button is clicked or not)
        mouse_pos = pygame.mouse.get_pos()

        # Check mouseover and clicked conditions
        if self.rect.collidepoint(mouse_pos):
            if pygame.mouse.get_pressed()[0] == 1 and not self.clicked:
                # print("Clicked")
                self.clicked = True
                action = True

        if pygame.mouse.get_pressed()[0] == 0:  # reseting the mouse button
            self.clicked = False

        # Draw button
        screen.blit(self.image, self.rect)

        return action


class Player:
    def __init__(self, x, y):  # graphics constructor
        self.reset(x, y)

    def update(self, game_over):
        dx = 0
        dy = 0
        walk_cooldown = 5
        col_thresh = 20

        if game_over == 0:
            # getting keypresses
            key = pygame.key.get_pressed()
            if key[pygame.K_SPACE] and self.jumped == False and self.in_air == False:
                jump_fx.play()
                self.val_y = -14  # length of jump
                self.jumped = True
            if key[pygame.K_SPACE] == False:
                self.jumped = False
            if key[pygame.K_a]:
                dx -= 5
                self.counter += 1  # animation(image iteration)
                self.diarection = -1
            if key[pygame.K_d]:
                dx += 5
                self.counter += 1  # animation(image iteration)
                self.diarection = 1
            if (
                key[pygame.K_a] == False and key[pygame.K_d] == False
            ):  # reset char to standby
                self.counter = 0
                self.index = 0
                if self.diarection == 1:
                    self.image = self.images_right[self.index]
                if self.diarection == -1:
                    self.image = self.images_left[self.index]

            # handle animation
            # self.counter += 1
            if self.counter > walk_cooldown:  # to slow dawn and normalize the animation
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images_right):
                    self.index = 0
                if self.diarection == 1:
                    self.image = self.images_right[self.index]
                if self.diarection == -1:
                    self.image = self.images_left[self.index]
            # adding gravity
            self.val_y += 1
            if self.val_y > 7:
                self.val_y = 7  # power of gravity
            dy += self.val_y

            # check for collision with the world
            self.in_air = True
            for tile in world.tile_list:
                # check for collision in x direction
                if tile[1].colliderect(
                    self.rect.x + dx, self.rect.y, self.width, self.height
                ):
                    dx = 0
                # check for collision in y direction
                if tile[1].colliderect(
                    self.rect.x, self.rect.y + dy, self.width, self.height
                ):
                    # check if below the ground i.e. jumping
                    if self.val_y < 0:
                        dy = tile[1].bottom - self.rect.top
                        self.val_y = 0

                    # check if above the ground i.e. falling
                    elif self.val_y >= 0:
                        dy = tile[1].top - self.rect.bottom
                        self.val_y = 0
                        self.in_air = False

            # check for collision with enemy
            if pygame.sprite.spritecollide(self, blob_group, False):
                game_over = -1
                game_over_fx.play()
            # check for collision with lava
            if pygame.sprite.spritecollide(self, lava_group, False):
                game_over = -1
                game_over_fx.play()
                # print(game_over)
            # check for collision with exit
            if pygame.sprite.spritecollide(self, exit_group, False):
                game_over = +1

            # check for collision with platforms
            for platform in platform_group:
                # collision in the x direction
                if platform.rect.colliderect(
                    self.rect.x + dx, self.rect.y, self.width, self.height
                ):
                    dx = 0

                # collision in the y direction
                if platform.rect.colliderect(
                    self.rect.x, self.rect.y + dy, self.width, self.height
                ):
                    # check if below platform
                    if abs((self.rect.top + dy) - platform.rect.bottom) < col_thresh:
                        self.vel_y = 0
                        dy = platform.rect.bottom - self.rect.top
                    # check if above platform
                    elif abs((self.rect.bottom + dy) - platform.rect.top) < col_thresh:
                        self.rect.bottom = platform.rect.top - 1
                        self.in_air = False
                        dy = 0

                    # move sideways with platform
                    if platform.move_x != 0:
                        self.rect.x += platform.move_direction

            # update player coordinates
            self.rect.x += dx
            self.rect.y += dy

        elif game_over == -1:
            self.image = self.dead_image
            if self.rect.y > 200:
                self.rect.y -= 5
                draw_text(
                    "GAME OVER !",
                    font,
                    red,
                    (screen_width // 2) - 112,
                    screen_height // 2,
                )
            # if self.rect.bottom > screen_height:
            #     self.rect.bottom = screen_height
            #     dy = 0
        # draw the player on the screen
        screen.blit(self.image, self.rect)
        # pygame.draw.rect(screen,(255,255,255),self.rect,2)

        return game_over

    def reset(self, x, y):  # reset method
        self.images_right = []
        self.images_left = []
        self.index = 0
        self.counter = 0
        for num in range(1, 5):
            img_right = pygame.image.load(f"img/guy{num}.png")
            img_right = pygame.transform.scale(img_right, (32, 64))
            image_left = pygame.transform.flip(
                img_right, True, False
            )  # not for yaxis false
            self.images_right.append(img_right)
            self.images_left.append(image_left)
        self.dead_image = pygame.image.load("img/ghost.png")
        self.image = self.images_right[self.index]
        self.rect = self.image.get_rect()  # coordinates
        self.rect.x = x
        self.rect.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.val_y = 0
        self.jumped = False
        self.diarection = 0
        self.in_air = True


class World:
    def __init__(self, data):
        self.tile_list = []

        # load images
        dirt_img = pygame.image.load("img/dirt.png")
        grass_img = pygame.image.load("img/grass.png")

        row_count = 0
        for row in data:
            col_count = 0
            for tile in row:
                if tile == 1:
                    img = pygame.transform.scale(dirt_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 2:
                    img = pygame.transform.scale(grass_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 3:
                    blob = Enemy(col_count * tile_size, row_count * tile_size + 5)
                    blob_group.add(blob)
                if tile == 4:
                    platform = Platform(
                        col_count * tile_size, row_count * tile_size, 1, 0
                    )
                    platform_group.add(platform)
                if tile == 5:
                    platform = Platform(
                        col_count * tile_size, row_count * tile_size, 0, 1
                    )
                    platform_group.add(platform)
                if tile == 6:
                    lava = Lava(
                        col_count * tile_size, row_count * tile_size + (tile_size // 2)
                    )
                    lava_group.add(lava)
                if tile == 7:
                    coin = Coin(
                        col_count * tile_size + (tile_size // 2),
                        row_count * tile_size + (tile_size // 2),
                    )
                    coin_group.add(coin)
                if tile == 8:
                    exit = Exit(
                        col_count * tile_size, row_count * tile_size - (tile_size // 2)
                    )
                    exit_group.add(exit)
                col_count += 1
            row_count += 1

    def draw(self):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])
            # pygame.draw.rect(screen, (255, 255, 255), tile[1], 2)


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/blob.png")
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_direction = 1
        self.move_counter = 0

    def update(self):
        self.rect.x += self.move_direction
        self.move_counter += 1
        if abs(self.move_counter) > 30:  # movement length of the enemy
            self.move_direction *= -1  # flip diarection
            self.move_counter *= -1  # flip distence


class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, move_x, move_y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/platform.png")
        self.image = pygame.transform.scale(self.image, (tile_size, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_counter = 0
        self.move_direction = 1
        self.move_x = move_x
        self.move_y = move_y

    def update(self):
        self.rect.x += self.move_direction * self.move_x
        self.rect.y += self.move_direction * self.move_y
        self.move_counter += 1
        if abs(self.move_counter) > 30:  # movement length of the enemy
            self.move_direction *= -1  # flip diarection
            self.move_counter *= -1


class Lava(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/lava.png")
        self.image = pygame.transform.scale(self.image, (tile_size, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load("img/coin.png")
        self.image = pygame.transform.scale(img, (tile_size // 2, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)


class Exit(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/exit.png")
        self.image = pygame.transform.scale(
            self.image, (tile_size, int(tile_size * 1.5))
        )
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


# world_data = [
#     [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
#     [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
#     [1, 0, 0, 0, 0, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 1],
#     [1, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 7, 0, 0, 0, 0, 0, 2, 2, 1],
#     [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 0, 7, 0, 5, 0, 0, 0, 1],
#     [1, 0, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 2, 2, 0, 0, 0, 0, 0, 1],
#     [1, 7, 0, 0, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
#     [1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
#     [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 0, 0, 7, 0, 0, 0, 0, 1],
#     [1, 0, 2, 0, 0, 7, 0, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
#     [1, 0, 0, 2, 0, 0, 4, 0, 0, 0, 0, 3, 0, 0, 3, 0, 0, 0, 0, 1],
#     [1, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 2, 2, 0, 0, 0, 1],
#     [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
#     [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 0, 7, 0, 0, 0, 0, 2, 0, 1],
#     [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
#     [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 2, 0, 2, 2, 2, 2, 2, 1],
#     [1, 0, 0, 0, 0, 0, 2, 2, 2, 6, 6, 6, 6, 6, 1, 1, 1, 1, 1, 1],
#     [1, 0, 0, 0, 0, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
#     [1, 0, 0, 0, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
#     [1, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
# ]


# main part and loop of the game where everything comes together

Player = Player(100, screen_height - 91)


blob_group = pygame.sprite.Group()
platform_group = pygame.sprite.Group()
lava_group = pygame.sprite.Group()
coin_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()

# dummy coin
score_coin = Coin(tile_size // 2 + 5, tile_size // 2 +2) 
coin_group.add(score_coin)


# load in level data and create wirld
if path.exists(f"level{level}_data"):
    pickled_data = open(f"level{level}_data", "rb")
    world_data = pickle.load(pickled_data)
world = World(world_data)


# create button
restart_button = Button(screen_width // 2 - 50, screen_height // 2 + 100, restart_img)
start_button = Button(screen_width // 2 - 150, screen_height // 2 + 50, start_img)
exit_button = Button(screen_width // 2 - 130, screen_height // 2 - 150, exit_img)

# the main loop
run = True
while run:
    clock.tick(fps)
    screen.blit(bg_img, (0, 0))
    screen.blit(sun_img, (100, 100))

    if main_menu == True:
        if exit_button.draw():
            run = False  # fuctionality to exit button
        if start_button.draw():
            main_menu = False  # fuctionality to start button
    else:
        world.draw()
        if game_over == 0:
            blob_group.update()
            platform_group.update()
            # update score
            # check if a coin has been collected
            if pygame.sprite.spritecollide(Player, coin_group, True):
                score += 1
                coin_fx.play()
            draw_text("X " + str(score), font_score, white, tile_size - 2, 5)
            draw_text("Level " + str(level), font_score, white, tile_size + 640, 5)

        # drawing things onto screen
        blob_group.draw(screen)
        platform_group.draw(screen)
        lava_group.draw(screen)
        coin_group.draw(screen)
        exit_group.draw(screen)

        game_over = Player.update(game_over)

        # if player died
        if game_over == -1:
            if restart_button.draw():  # if game over the restart buttton
                # print("restart")
                world_data = []
                world = reset_level(level)
                game_over = 0
                score = 0

        # if player passed
        if game_over == 1:
            # reset game go to next level
            level += 1
            # fps += 10
            if level <= max_levels:
                # reset level
                world_data = []
                world = reset_level(
                    level
                )  # clear all data and return the new world data and store in world
                game_over = 0
                # draw_text("Level " + str(level), font_score, white, tile_size - 10, 10)
            else:
                # restart if player compleate all levels
                draw_text(
                    "YOU WIN !",
                    font,
                    blue,
                    (screen_width // 2) - 112,
                    screen_height // 2,
                )
                if restart_button.draw():
                    level = 0
                    world_data = []
                    world = reset_level(
                        level
                    )  # clear all data and return the new world data and store in world
                    game_over = 0
                    score = 0

    # draw_grid()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()

pygame.quit()
