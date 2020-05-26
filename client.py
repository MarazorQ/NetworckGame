import pickle
import select
import socket
import sys
from random import randint

import pygame

WIDTH = 500
HEIGHT = 500
FPS = 60
BUFFER_SIZE = 2048

# Color
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Connect to the server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('127.0.0.1', 4323))

# Create game and window
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("better then gta5")
clock = pygame.time.Clock()


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, player_id):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((80, 80))
        if player_id == 2:
            self.image.fill(GREEN)
        else:
            self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed_y = 0
        self.id = player_id
        self.shoots = False
        self.score = 0

    def update(self):
        self.speed_y = 0
        keystate = pygame.key.get_pressed()
        if self.id == user_id:
            if keystate[pygame.K_UP]:
                self.speed_y = -8
            if keystate[pygame.K_DOWN]:
                self.speed_y = 8
            self.rect.y += self.speed_y
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom >= HEIGHT:
            self.rect.bottom = HEIGHT

    def shoot(self):
        if not len(bullets.spritedict):
            bullet = Bullet(self.rect.centery, self.rect.right, self.id)
            bullets.add(bullet)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, user_shoot):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((10, 20))
        if user_shoot == 2:
            self.image.fill(GREEN)
        else:
            self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        if user_shoot == 2:
            self.rect.right = y
        else:
            self.rect.right = y-90
        self.rect.centery = x
        self.user_shoot = user_shoot
        self.speed_x = 11

    def update(self):
        if self.user_shoot == 2:
            self.rect.x += self.speed_x
        else:
            self.rect.x -= self.speed_x

        # Kill the bullet
        if self.rect.left > WIDTH:
            self.kill()
        if self.rect.left > WIDTH:
            self.kill()
        if self.rect.left < 0:
            self.kill()


bullets = pygame.sprite.Group()
user_sprites = pygame.sprite.Group()

#init 
user_id = 0
player = None
player_2 = None

while True:
    ins, outs, ex = select.select([s], [], [], 0)
    for inm in ins:
        gameEvent = pickle.loads(inm.recv(BUFFER_SIZE))
        if gameEvent[0] == 'create connection':
            user_id = gameEvent[1]
            if user_id == 2:
                player = Player(0, randint(0, HEIGHT), user_id)
            else:
                player = Player(WIDTH - 80, randint(0, HEIGHT), user_id)
            user_sprites.add(player)
        if gameEvent[0] == 'player locations':
            gameEvent.pop(0)
            if len(gameEvent) == 1:
                user_sprites.remove(player_2)
            for _ in gameEvent:
                if len(user_sprites.spritedict) != 2:
                    if _[2] != user_id:
                        player_2 = Player(_[0], _[1], _[2])
                        user_sprites.add(player_2)
                else:
                    if _[2] != user_id:
                        player_2.rect.x = _[0]
                        player_2.rect.y = _[1]
                        player_2.id = _[2]
                        player_2.score = _[4]
                if _[3]:
                    if _[2] == player.id:
                        player.shoot()
                    else:
                        player_2.shoot()
    # Cycle speed
    clock.tick(FPS)

    # Event input
    for event in pygame.event.get():
        # Window closing
        if event.type == pygame.QUIT:
            ge = ['close', player.rect.x, player.rect.y, user_id, None, None]
            s.send(pickle.dumps(ge))
            s.close()
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.shoots = True

    # Update
    user_sprites.update()
    bullets.update()

    # Render
    screen.fill(BLACK)
    user_sprites.draw(screen)
    bullets.draw(screen)
    if player_2:
        hits_1 = pygame.sprite.spritecollide(player_2, bullets, True)
        if hits_1:
            player.score += 1
        hits = pygame.sprite.spritecollide(player, bullets, True)

    # Score
    f2 = pygame.font.SysFont('serif', 48)
    if player_2 and player.id == 2:
        text2 = f2.render('{}:{}'.format(player.score,player_2.score), 0, (0, 180, 0))
    elif player_2 and player.id == 1:
        text2 = f2.render('{}:{}'.format(player_2.score,player.score), 0, (0, 180, 0))
    else:
        text2 = f2.render('0:0', 0, (0, 180, 0))
    screen.blit(text2, (220, 0))

    # Flip display
    pygame.display.flip()

    # Sending message to the server
    ge = ['position update', player.rect.x, player.rect.y, user_id, player.shoots, player.score]
    player.shoots = False
    s.send(pickle.dumps(ge))
