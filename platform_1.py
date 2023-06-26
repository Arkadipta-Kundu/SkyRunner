from typing import Any
import pygame
from pygame.locals import *

pygame.init()

clock = pygame.time.Clock()
fps = 60

screen_width = 800
screen_height = 800

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Platformer")

# define game variables
tile_size = 40

# load images
sun_img = pygame.image.load("img/sun.png")
bg_img = pygame.image.load("img/sky.png")


# def draw_grid():
#     for line in range(0, 20):
#         pygame.draw.line(screen, (255, 255, 255), (0, line * tile_size), (screen_width, line * tile_size))
#         pygame.draw.line(screen, (255, 255, 255), (line * tile_size, 0), (line * tile_size, screen_height))

# grid lines are created for positioning reference


class Player:
    def __init__(self, x, y):  # graphics constructor
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
        self.image = self.images_right[self.index]
        self.rect = self.image.get_rect()  # coordinates
        self.rect.x = x
        self.rect.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.val_y = 0
        self.jumped = False
        self.diarection = 0

    def update(self):
        dx = 0
        dy = 0
        walk_cooldown = 5
        # getting keypresses
        key = pygame.key.get_pressed()
        if key[pygame.K_SPACE] and self.jumped == False:
            self.val_y = -12.9  # length of jump
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

        # check for collision
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

        # update player coordinates
        self.rect.x += dx
        self.rect.y += dy

        if self.rect.bottom > screen_height:
            self.rect.bottom = screen_height
            dy = 0
        # draw the player on the screen
        screen.blit(self.image, self.rect)


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
                col_count += 1
            row_count += 1

    def draw(self):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])
            pygame.draw.rect(screen, (255, 255, 255), tile[1], 2)


class Enemy(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load('img/blob.png')
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
		self.move_direction = 1
		self.move_counter = 0

	def update(self):
		self.rect.x += self.move_direction
		self.move_counter += 1
		if abs(self.move_counter) > 40:
			self.move_direction *= -1     #flip diarection
			self.move_counter *= -1       #flip distence

world_data = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 1],
    [1, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 7, 0, 0, 0, 0, 0, 2, 2, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 0, 7, 0, 5, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 2, 2, 0, 0, 0, 0, 0, 1],
    [1, 7, 0, 0, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 0, 0, 7, 0, 0, 0, 0, 1],
    [1, 0, 2, 0, 0, 7, 0, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 2, 0, 0, 4, 0, 0, 0, 0, 3, 0, 0, 3, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 2, 2, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 0, 7, 0, 0, 0, 0, 2, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 2, 0, 2, 2, 2, 2, 2, 1],
    [1, 0, 0, 0, 0, 0, 2, 2, 2, 6, 6, 6, 6, 6, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
]

Player = Player(100, screen_height - 91)

blob_group = pygame.sprite.Group()

world = World(world_data)

run = True
while run:
    clock.tick(fps)
    screen.blit(bg_img, (0, 0))
    screen.blit(sun_img, (100, 100))

    world.draw()

    blob_group.update()

    blob_group.draw(screen)

    Player.update()

    # draw_grid()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()

pygame.quit()
