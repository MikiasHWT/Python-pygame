import pygame
from pygame.locals import *
import random

# Initialize pygame
pygame.init()

# Frame rate and screen setup
clock = pygame.time.Clock()
fps = 60
screen_width = 864
screen_height = 936
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('TLR Evade')

# Define font and color
font = pygame.font.SysFont('Bauhaus 93', 60)
white = (255, 255, 255)

# Game variables
ground_scroll = 0
scroll_speed = 4
flying = False
game_over = False
tlr_gap = 150
tlr_frequency = 2500  # milliseconds
last_tlr = pygame.time.get_ticks() - tlr_frequency
score = 0
pass_tlr = False
my_start = -200
patient_x = my_start

# Load images
bg = pygame.image.load('images/New_veinbg.png')
ground_img = pygame.image.load('images/ground.png')
button_img = pygame.image.load('images/restart.png')
patient_img = pygame.image.load('images/Sneeze_me5.png').convert_alpha()

# Function to draw text
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

# Function to reset game
def reset_game():
    tlr_group.empty()
    virus.rect.x = 100
    virus.rect.y = int(screen_height / 2)
    score = 0
    ground_scroll = 0
    flying = False
    return score

# Virus particle class 
class Virus(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = [pygame.image.load(f'images/coronavirus-green-attack_{i}.png') for i in range(3)]
        self.jump_img = pygame.image.load('images/coronavirus-green-attack_4.png')
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.vel = 0
        self.clicked = False

    def update(self):
        if flying:
            # Apply gravity
            self.vel += 0.5
            if self.vel > 8:
                self.vel = 8
            if self.rect.bottom < 768:
                self.rect.y += int(self.vel)
        
        # Handle jump and animation
        if game_over == False:
            if pygame.key.get_pressed()[K_SPACE] and not self.clicked:
                self.clicked = True
                self.vel = -10
                self.image = self.jump_img
            if not pygame.key.get_pressed()[K_SPACE]:
                self.clicked = False
                self.image = self.images[0]
            # self.image = pygame.transform.rotate(self.image, self.vel * -2)

# TLR class
class TLR(pygame.sprite.Sprite):
    def __init__(self, x, y, position):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('images/MacroTLR2.png').convert_alpha()
        self.rect = self.image.get_rect()
        if position == 1:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x, y - int(tlr_gap / 1.5)]
        else:
            self.rect.topleft = [x, y + int(tlr_gap / 1.5)]

    def update(self):
        self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill()

# Button class for restarting game
class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def draw(self):
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos) and pygame.mouse.get_pressed()[0]:
            return True
        screen.blit(self.image, (self.rect.x, self.rect.y))
        return False

# Create sprite groups
virus_group = pygame.sprite.Group()
tlr_group = pygame.sprite.Group()

# Create virus (main object)
virus = Virus(100, int(screen_height / 2))
virus_group.add(virus)

# Create restart button
button = Button(screen_width // 2 - 50, screen_height // 2 - 100, button_img)

# Main game loop
run = True
while run:

    clock.tick(fps)
    screen.blit(bg, (0, 0))

    # Draw virus and TLR's
    virus_group.draw(screen)
    virus_group.update()
    tlr_group.draw(screen)

    # Draw ground and patient character
    screen.blit(ground_img, (ground_scroll, 768))
    screen.blit(patient_img, (patient_x, 0))

    # Move patient if game is in progress
    if flying:
        patient_x += -10

    # Scoring logic
    if len(tlr_group) > 0:
        if virus.rect.left > tlr_group.sprites()[0].rect.left and virus.rect.right < tlr_group.sprites()[0].rect.right and not pass_tlr:
            pass_tlr = True
        if pass_tlr and virus.rect.left > tlr_group.sprites()[0].rect.right:
            score += 1
            pass_tlr = False

    draw_text(str(score), font, white, int(screen_width / 2), 20)

    # Collision detection
    if pygame.sprite.groupcollide(virus_group, tlr_group, False, False) or virus.rect.top < 0:
        game_over = True
    if virus.rect.bottom >= 768:
        game_over = True
        flying = False

    # Generate new TLR's and scroll ground
    if not game_over and flying:
        time_now = pygame.time.get_ticks()
        if time_now - last_tlr > tlr_frequency:
            tlr_height = random.randint(-150, 150)
            btm_tlr = TLR(screen_width, int(screen_height / 2) + tlr_height, -1)
            top_tlr = TLR(screen_width, int(screen_height / 2) + tlr_height, 1)
            tlr_group.add(btm_tlr)
            tlr_group.add(top_tlr)
            last_tlr = time_now
        ground_scroll -= scroll_speed
        if abs(ground_scroll) > 35:
            ground_scroll = 0
        tlr_group.update()

    # Game over logic and restart
    if game_over:
        if button.draw():
            game_over = False
            score = reset_game()
        patient_x = my_start

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN and not flying and not game_over:
            flying = True
            patient_x += (ground_scroll / 2)

    pygame.display.update()

pygame.quit()
