import pygame
from pygame.locals import *
import random

pygame.init()

score = 0
clock = pygame.time.Clock()
fps = 60
screen_width = 864
screen_height = 936
ground_scroll = 0
scroll_speed = 4
flying = False
game_over = False
pipe_gap = 200
pipe_frequency = 1500 #ms
over_pipe = False
font = pygame.font.SysFont('Bauhaus 93', 60)
white = (255, 255, 255)
last_pipe = pygame.time.get_ticks() - pipe_frequency
level_up = False
gap_shrink_by_level = 10

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Flappy Bird')

# Load images
bg = pygame.image.load('img/bg.png')
ground_img = pygame.image.load('img/ground.png')
btn_img = pygame.image.load('img/restart.png')

def draw_text(text, font, color, x, y):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    screen.blit(text_surface, text_rect)

class Bird(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        self.index = 0
        self.counter = 0
        for num in range(1, 4):
            img = pygame.image.load(f'img/bird{num}.png')
            self.images.append(img)
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.velocity = 0
        self.pressed = False

    def update(self):
        if not flying:
            return

        self.velocity += 0.5

        if self.velocity > 8:
            self.velocity = 8

        if self.rect.bottom > 768:
            self.rect.bottom = 768

        if self.rect.top < 0:
            self.rect.top = 0        
        
        if self.rect.bottom <= 768 and self.rect.top >= 0:
            self.rect.y += int(self.velocity)

        
        keys = pygame.key.get_pressed()

        self.counter += 1
        flap_cooldown = 5

        if self.counter > flap_cooldown:
            self.counter = 0
            self.index += 1
            self.index = self.index % len(self.images)

        self.image = self.images[self.index]

class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, position):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('img/pipe.png')
        self.rect = self.image.get_rect()

        if position == 1:  
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x, y  - int(pipe_gap/2)]
        if position == -1:
            self.rect.topleft = [x, y + int(pipe_gap/2)]

    def update(self):
        self.rect.x -= scroll_speed
        
        if self.rect.right < 0:
            self.kill()

class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def draw(self):
        action = False

        pos = pygame.mouse.get_pos()



        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1:
                action = True

        screen.blit(self.image, (self.rect.x, self.rect.y))    

        return action

bird_group = pygame.sprite.Group()        
pipe_group = pygame.sprite.Group()

flappy = Bird(100, int(screen_height/2))

button = Button(screen_width/2, screen_height/2, btn_img)

bird_group.add(flappy)

run = True

def reset_game():
    pipe_group.empty()
    flappy.rect.x = 100
    flappy.rect.y = int(screen_height/2)
    
    global score
    score = 0

while run: 
    clock.tick(fps)

    screen.blit(bg, (0, 0))
    
    bird_group.draw(screen)
    pipe_group.draw(screen)

    if game_over:
        if button.draw():
            game_over = False
            reset_game()

    
    screen.blit(ground_img, (ground_scroll, 768))

    draw_text(f'Score: {str(score)}', font, white, screen_width/2, 30)

    if score > 0 and score % 5 == 0 and level_up == False:
        level_up = True
        pipe_gap -= gap_shrink_by_level

    if score > 0 and score % 5 == 1 and level_up:    
        level_up = False

    if len(pipe_group.sprites()) > 0:
        if flappy.rect.right > pipe_group.sprites()[0].rect.left and flappy.rect.left < pipe_group.sprites()[0].rect.left :
            over_pipe = True
        if over_pipe == True and flappy.rect.left > pipe_group.sprites()[0].rect.right:
            over_pipe = False
            score += 1

    if pygame.sprite.groupcollide(bird_group, pipe_group, False, False):
        game_over = True
        flying = False


    if flappy.rect.bottom > 768:
        game_over = True
        flying = False
    
    if game_over == False and flying == True:
        time_now = pygame.time.get_ticks()
        if time_now - last_pipe > pipe_frequency:
            last_pipe = time_now

            pipe_height = random.randint(-100, 100)
            btm_pipe = Pipe(screen_width, int(screen_height/2) + pipe_height, 1)
            top_pipe = Pipe(screen_width, int(screen_height/2) + pipe_height, -1)
            pipe_group.add(btm_pipe)
            pipe_group.add(top_pipe)

        ground_scroll -= scroll_speed
        if abs(ground_scroll) > 35:
            ground_scroll = 0

        bird_group.update()
        pipe_group.update()    

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if game_over and  event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            game_over = False
            reset_game()
        if event.type == pygame.KEYDOWN and flying == False and game_over == False:
            flying = True    
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and (not flappy.pressed):
            flappy.pressed = True    
            flappy.velocity = -10    
        if event.type == pygame.KEYUP and event.key == pygame.K_SPACE:
            flappy.pressed = False    

    pygame.display.update()        

pygame.quit()