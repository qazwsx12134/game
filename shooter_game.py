import pygame
import random

pygame.init()

WIDTH = 800
HEIGHT = 600
TICKRATE = 60

GREEN = (0, 255, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)

window = pygame.display.set_mode((WIDTH, HEIGHT))

clock = pygame.time.Clock()

background = pygame.image.load("background.jpg")
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

class SpaceShip(pygame.sprite.Sprite):

    def __init__(self, image, x, y, speed, shoot_cd = TICKRATE):
        super().__init__()
        self.image = pygame.image.load(image)
        self.rect = self.image.get_rect(center = (x, y))
        self.speed = speed
        self.shoot_cd = Cooldown(shoot_cd)

    def draw(self):
        window.blit(self.image, self.rect)

class Laser(pygame.sprite.Sprite):
    def __init__(self, x, y, color, speed):
        super().__init__()
        self.image = pygame.Surface((3, 15))
        self.image.fill(color)
        self.rect = self.image.get_rect(center = (x, y))
        self.speed = speed

    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0 or self.rect.top > HEIGHT:
            self.kill()


class PlayerShip(SpaceShip):
    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.rect.y -= self.speed
        if keys[pygame.K_s]:
            self.rect.y += self.speed
        if keys[pygame.K_a]:
            self.rect.x -= self.speed
        if keys[pygame.K_d]:
            self.rect.x += self.speed
        if self.shoot_cd.done(False):
            if keys[pygame.K_SPACE]:
                game.player_lasers.add(
                    Laser(self.rect.left, self.rect.top, GREEN, -5)
                )
                game.player_lasers.add(
                    Laser(self.rect.right, self.rect.top, GREEN, -5)
                )      
                self.shoot_cd.reset()  

        collides = pygame.sprite.spritecollideany(
            self,
            game.enemies_lasers
        ) 
        if collides:
            game.state = 'lose'   

        collides = pygame.sprite.spritecollideany(
            self,
            game.enemies
        ) 
        if collides:
            game.state = 'lose'              

class EnemyShip(SpaceShip):
    def __init__(self, image, x, y, speed):
        super().__init__(image, x, y, speed, TICKRATE * 2)
        self.image = pygame.transform.flip(self.image, False, True) 

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()
        collided = pygame.sprite.spritecollideany(self, game.player_lasers)
        if collided:
            self.kill()
            game.score += 1
            game.hud.score.update(f'Scores: {game.score}')
            collided.kill()
        if self.shoot_cd.done():
            game.enemies_lasers.add(
                Laser(self.rect.centerx, self.rect.
                bottom, RED,5)
            )
            self.shoot_cd.reset()    
        


class Cooldown():

    def __init__(self, ticks):
        self.ticks = ticks
        self.current = ticks


    def reset(self):
        self.current = self.ticks

    def done(self, need_reset = True):
        if self.current == 0:
            if need_reset:
                self.reset()
            return True
        else:
            self.current -= 1
            return False

class Label():
    def __init__(self, text, x, y, size = 30):
        self.font = pygame.font.Font('pixel.ttf', size)
        self.image = self.font.render(text, True, WHITE)
        self.rect = self.image.get_rect(center=(x, y))

    def draw(self):
        window.blit(self.image, self.rect)

    def update(self, text):
        self.image = self.font.render(text, True, WHITE)


class HUD():
    def __init__(self):
        self.score = Label('Score: 0', 70, 20)
        self.lose = Label('GAME OVER', WIDTH / 2, HEIGHT / 2, 70)
        self.restart = Label('Press ENTER to restart', WIDTH / 2, HEIGHT / 2 + 50, 40)

    def draw_play(self):
        self.score.draw()

    def draw_lose(self):
        self.lose.draw()
        self.restart.draw()


class GameManegr():

    def __init__(self):
        self.state = 'play'
        self.score = 0
        self.player = PlayerShip("player.png", WIDTH / 2, HEIGHT / 2, 5, TICKRATE // 4)
        self.player_lasers = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.enemies_lasers = pygame.sprite.Group()
        self.enemy_spawn_cd = Cooldown(TICKRATE)
        self.hud = HUD()

    def restart(self):
        self.player_lasers.empty()
        self.enemies_lasers.empty()
        self.enemies.empty()
        self.state = 'play'
        self.score = 0
        self.hud.score.update(f'Score {self.score}')
        self.player.rect.center = (WIDTH / 2, HEIGHT / 2)

    def update(self):
        if self.state == 'play':
            self.player.update()
            self.player_lasers.update()
            self.enemies.update()
            self.enemies_lasers.update()
            if self.enemy_spawn_cd.done():
                self.enemies.add(
                    EnemyShip("enemy.png", random.randint(50, WIDTH - 50), - 100, 2)
                )
            pygame.sprite.groupcollide(
                self.player_lasers,
                self.enemies_lasers,
                True,
                True
            )

    def draw(self):
        window.blit(background, (0, 0))
        if self.state == 'play':
            self.player.draw()
            self.player_lasers.draw(window)
            self.enemies.draw(window)
            self.enemies_lasers.draw(window)
            self.hud.draw_play()
        elif self.state == 'lose':
            self.hud.draw_lose()
game = GameManegr()

while True:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            quit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN and game.state == 'lose':
                game.restart()
    game.update()

    game.draw()


    pygame.display.flip()
    clock.tick(TICKRATE)
