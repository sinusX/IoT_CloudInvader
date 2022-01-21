from datetime import datetime
import sys, pygame
from time import sleep
import random
import os
from pynput.keyboard import Key, Listener
import asyncio
import time
from azure.eventhub.aio import EventHubConsumerClient


size = width, height = 1500, 750

class Bullet:
    bullet_speed = 15

    def __init__(self, centerX, centerY) -> None:
        self.surface = pygame.image.load("Bullet.jpg")
        self.rect = self.surface.get_rect()
        self.rect.centerx = centerX
        self.rect.centery = centerY
    
    def move(self):
        self.rect = self.rect.move(0 , -Bullet.bullet_speed)

    def get_surface(self) -> pygame.Surface:
        return self.surface

    def get_rect(self) -> pygame.Rect:
        return self.rect

class Spaceship:

    def __init__(self, screen_width, screen_height) -> None:

        self.screen_width = screen_width
        self.screen_hight = screen_height

        self.surface = pygame.image.load("CloudInvader.png")
        self.rect = self.surface.get_rect()
        self.rect = self.rect.move(screen_width/2 - self.rect.width/2,
            screen_height - self.rect.height)

        self.t_lastshot = datetime.now()

    def move(self, x, y) -> None:
        self.rect = self.rect.move(x, y)
        # Clamp position to stay on screen
        if(self.rect.x + self.rect.width/2 < 0):
            self.rect.x = -self.rect.width/2
        
        if(self.rect.x + self.rect.width/2 > self.screen_width):
            self.rect.x = self.screen_width - self.rect.width/2

    def shoot(self) -> Bullet:
        t_since_lastshot = datetime.now() - self.t_lastshot
        if (t_since_lastshot.total_seconds() * 1000) > 200:
            self.t_lastshot = datetime.now()
            return Bullet(self.rect.centerx, self.rect.centery)

    def get_surface(self) -> pygame.Surface:
        return self.surface

    def get_rect(self) -> pygame.Rect:
        return self.rect

class Enemy:
    imgages = ["meta.png", "azure.png", "AWS.png", "GoogleCloud.png"]
    speed = 3
    
    def __init__(self,) -> None:
        self.surface = pygame.image.load(random.choice(Enemy.imgages))
        self.rect = self.surface.get_rect()
        self.rect.centery = 0
        xpos = random.randint(self.rect.centerx, width - self.rect.centerx)
        self.rect.centerx = xpos
        
    def move(self):
        self.rect = self.rect.move(0 , Enemy.speed)

    def get_surface(self) -> pygame.Surface:
        return self.surface

    def get_rect(self) -> pygame.Rect:
        return self.rect

class EnemyFactory:

    def __init__(self) -> None:
        pass
        
    def span(self, chance) -> Enemy:
        x = random.randint(0,100*1000)
        if x <= int(chance*1000):
            return Enemy()
        else:
            return None

class ControlKeyboard:

    def __init__(self) -> None:
        self.left_arrow = False
        self.right_arrow = False

    async def start(self):
        listener = Listener(
                on_press=self.on_press,
                on_release=self.on_release)
        listener.start()

    def get_right_arrow(self):
        return self.right_arrow

    def get_left_arrow(self):
        return self.left_arrow
        
    def on_press(self, key):

        if key == Key.right:
            self.right_arrow = True
        elif key == Key.left:
            self.left_arrow = True

    def on_release(self, key):
        
        if key == Key.right:
            self.right_arrow = False
        elif key == Key.left:
            self.left_arrow = False

class ControlIoT:
    def __init__(self) -> None:
        self.left_arrow = False
        self.right_arrow = False

        self.connection_str = os.getenv("EVENTHUB_CONNECTION_STRING")
        self.consumer_group = "$Default"
        self.startup_time = time.time()*1000

    async def start(self):
        print("Start controller",flush=True)
        client = EventHubConsumerClient.from_connection_string(self.connection_str, self.consumer_group)
        async with client:
            await client.receive(
                on_event=self.on_event,
                starting_position="-1",  # "-1" is from the beginning of the partition.
            )

    async def on_event(self, partition_context, event):
        if event.system_properties[b'iothub-enqueuedtime'] > self.startup_time:
            recv_msg = event.body_as_json(encoding='UTF-8')
            if "buttonA" in recv_msg:
                if recv_msg["buttonA"] == 1:
                    self.left_arrow = True
                    print("left arrow is pressed",flush=True)
                else: 
                    self.left_arrow = False
                    print("left arrow is released",flush=True)
            if "buttonB" in recv_msg:
                if recv_msg["buttonB"] == 1:
                    self.right_arrow = True
                    print("right arrow is pressed",flush=True)
                else: 
                    self.right_arrow = False
                    print("right arrow is released",flush=True)

    def get_right_arrow(self):
        return self.right_arrow

    def get_left_arrow(self):
        return self.left_arrow

async def mainLoop(control):
    print("Start",flush=True)
    pygame.init()
    background = 255, 255, 255

    screen = pygame.display.set_mode(size)
    spaceship = Spaceship(width, height)
    bullets = []
    enemies = []
    enemies.append(Enemy())

    enemy_factory = EnemyFactory()

    while 1: 

        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                sys.exit()

        # New Enemy
        new_enemy = enemy_factory.span(1.5)
        if new_enemy is not None:
            enemies.append(new_enemy)

        # spaceship movement
        if control.get_right_arrow():
            spaceship.move(20, 0)
        if control.get_left_arrow():
            spaceship.move(-20, 0)
        if (control.get_right_arrow() and control.get_left_arrow()):
            new_shot = spaceship.shoot()
            if new_shot:
                bullets.insert(-1, new_shot)
        

        # bullet movement
        for bullet in bullets:
            bullet.move()
            if not bullet.get_rect().colliderect(screen.get_rect()):
                bullets.remove(bullet)

        # enemy movement
        for enemy in enemies:
            enemy.move()
            if not enemy.get_rect().colliderect(screen.get_rect()):
                enemies.remove(enemy)
        
        # check if a bullet has hit an enemy
        for enemy in enemies:
            for bullet in bullets:
                if enemy.get_rect().colliderect(bullet.get_rect()):
                    enemies.remove(enemy)
                    bullets.remove(bullet)
        
        # render
        screen.fill(background)
        for bullet in bullets:
            screen.blit(bullet.get_surface(), bullet.get_rect())

        for enemy in enemies:
            screen.blit(enemy.get_surface(), enemy.get_rect())

        screen.blit(spaceship.get_surface(), spaceship.get_rect())
        pygame.display.flip()
        await asyncio.sleep(0.020)

    return True

async def multiple_tasks(control):
    input_coroutines = [control.start(), mainLoop(control)]
    res = await asyncio.gather(*input_coroutines, return_exceptions=True)
    return res

if __name__ == "__main__":
    #Choose controller ToDo: selction over CLI argument
    control = ControlIoT()
    #control = ControlKeyboard()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(multiple_tasks(control))

    # asyncio.run(main())