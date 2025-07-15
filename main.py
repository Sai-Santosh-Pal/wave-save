import pygame
import random
import sys
import math
import os

# --- Constants ---
WIDTH, HEIGHT = 800, 600
FPS = 60

# Retro color palette
COLORS = {
    'background': (48, 56, 104),
    'text': (255, 255, 255)
}

ASSET_PATH = 'assets'

# --- Gap and Speed Scaling ---
INITIAL_GAP = 250  # Initial gap in pixels between obstacles
MIN_GAP = 80       # Minimum gap in pixels
GAP_DECREASE_RATE = 0.05  # How much the gap decreases per score unit
INITIAL_SCROLL_SPEED = 6
MAX_SCROLL_SPEED = 18
SPEED_INCREASE_RATE = 0.01  # How much speed increases per score unit

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Wave Safe')
clock = pygame.time.Clock()

# --- Load Sprites ---
def load_sprite(name):
    path = os.path.join(ASSET_PATH, name)
    img = pygame.image.load(path).convert_alpha()
    return [img]

# Surfer: static
surfer_frames = load_sprite('surfer.png')
# Wave: static
wave_frames = load_sprite('wave.png')
# Obstacles: static
shark_frames = load_sprite('shark.png')
stone_frames = load_sprite('stone.png')
wood_frames = load_sprite('wood.png')

# --- Sprite Scaling ---
# --- Endless Runner Dino-Style Platformer ---

SURFER_HEIGHT = 120
WAVE_HEIGHT = 60
OBSTACLE_HEIGHT = 60
WATERLINE = HEIGHT - 40
GROUND_Y = WATERLINE
TILE_WIDTH = 60
SCROLL_SPEED = INITIAL_SCROLL_SPEED

from pygame.transform import scale

def scale_to_height(img, target_height):
    w, h = img.get_width(), img.get_height()
    scale_factor = target_height / h
    return scale(img, (int(w * scale_factor), target_height))

surfer_img = scale_to_height(surfer_frames[0], SURFER_HEIGHT)
# Scale wave image to desired height, keep original width
wave_img = scale_to_height(wave_frames[0], WAVE_HEIGHT)
shark_img = scale_to_height(shark_frames[0], OBSTACLE_HEIGHT)
stone_img = scale_to_height(stone_frames[0], OBSTACLE_HEIGHT)
wood_img = scale_to_height(wood_frames[0], OBSTACLE_HEIGHT)

# --- Asset Dimension Checker ---
def print_asset_dimensions():
    asset_files = ['surfer.png', 'wave.png', 'shark.png', 'stone.png', 'wood.png']
    for fname in asset_files:
        path = os.path.join(ASSET_PATH, fname)
        try:
            img = pygame.image.load(path)
            print(f"{fname}: {img.get_width()} x {img.get_height()}")
        except Exception as e:
            print(f"{fname}: Error loading image - {e}")

# Print asset dimensions at startup
print_asset_dimensions()

# Load background
background_img = pygame.image.load(os.path.join(ASSET_PATH, 'background.png')).convert()
background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))

# --- Wave Tiles (Ground) ---
class WaveTile:
    def __init__(self, x):
        self.image = wave_img
        self.rect = self.image.get_rect(topleft=(x, GROUND_Y - WAVE_HEIGHT))
    def update(self):
        self.rect.x -= SCROLL_SPEED
    def draw(self, surface):
        surface.blit(self.image, self.rect)

# --- Obstacles ---
class Obstacle(pygame.sprite.Sprite):
    def __init__(self, kind, x, y):
        super().__init__()
        if kind == 'shark':
            self.image = shark_img
        elif kind == 'stone':
            self.image = stone_img
        elif kind == 'wood':
            self.image = wood_img
        elif kind == 'wave':
            self.image = wave_img
        else:
            self.image = pygame.Surface((40,40), pygame.SRCALPHA)
        self.kind = kind
        self.rect = self.image.get_rect(midbottom=(x, y))
    def update(self):
        self.rect.x -= SCROLL_SPEED
    def draw(self, surface):
        # Removed shadow
        surface.blit(self.image, self.rect)

# --- Player ---
class Player:
    def __init__(self):
        self.image = surfer_img
        self.rect = self.image.get_rect(midbottom=(120, GROUND_Y))
        self.vel_y = 0
        self.is_jumping = False
        self.on_ground = True
        self.standing_on_wave = False  # Track if standing on wave
    def update(self, wave_tiles, obstacles):
        keys = pygame.key.get_pressed()
        if not self.is_jumping and self.on_ground and keys[pygame.K_SPACE]:
            self.vel_y = -18
            self.is_jumping = True
            self.on_ground = False
        self.vel_y += 1
        self.rect.y += self.vel_y
        # Check for ground (wave tile) collision
        self.on_ground = False
        self.standing_on_wave = False
        # Stand on wave obstacles
        for obs in obstacles:
            if hasattr(obs, 'kind') and obs.kind == 'wave':
                if self.rect.colliderect(obs.rect) and self.vel_y >= 0:
                    if self.rect.bottom - self.vel_y <= obs.rect.top + 10:
                        self.rect.bottom = obs.rect.top + 1
                        self.vel_y = 0
                        self.is_jumping = False
                        self.on_ground = True
                        self.standing_on_wave = True
        # No wave obstacles: use invisible ground at GROUND_Y
        if not self.on_ground and self.rect.bottom >= GROUND_Y:
            self.rect.bottom = GROUND_Y
            self.vel_y = 0
            self.is_jumping = False
            self.on_ground = True
            self.standing_on_wave = False
        # Floor (if no tile)
        if self.rect.bottom >= HEIGHT:
            self.rect.bottom = HEIGHT
            self.vel_y = 0
            self.is_jumping = False
            self.on_ground = False
            self.standing_on_wave = False
    def draw(self, surface):
        # Removed shadow
        surface.blit(self.image, self.rect)

# --- Game Setup ---
player = Player()
waves = []  # No ground wave tiles
obstacles = pygame.sprite.Group()

# Gap logic
current_gap = INITIAL_GAP
last_obstacle_x = WIDTH

gap_timer = 0
obstacle_timer = 0
score = 0
game_over = False

font = pygame.font.SysFont('Consolas', 32)

# --- Main Game Loop ---
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN and game_over:
            if event.key == pygame.K_r:
                # Reset game
                player = Player()
                waves = []  # No ground wave tiles
                obstacles.empty()
                score = 0
                game_over = False
                current_gap = INITIAL_GAP
                last_obstacle_x = WIDTH
                SCROLL_SPEED = INITIAL_SCROLL_SPEED

    if not game_over:
        # --- Update speed and gap ---
        SCROLL_SPEED = min(INITIAL_SCROLL_SPEED + int(score * SPEED_INCREASE_RATE), MAX_SCROLL_SPEED)
        current_gap = max(INITIAL_GAP - int(score * GAP_DECREASE_RATE), MIN_GAP)

        # --- Update obstacles ---
        obstacles.update()
        # Spawn obstacles at ground level, with increasing frequency
        if len(obstacles) == 0 or (obstacles.sprites()[-1].rect.x < WIDTH - current_gap):
            kind = random.choice(['shark', 'stone', 'wood', 'wave'])
            obs_y = GROUND_Y
            obs_x = WIDTH + TILE_WIDTH
            obstacles.add(Obstacle(kind, obs_x, obs_y))

        # --- Update player ---
        player.update([], obstacles)
        # --- Collision detection ---
        for obs in obstacles:
            if obs.kind != 'wave' and player.rect.colliderect(obs.rect):
                game_over = True
            # If colliding with wave but not standing on top, game over
            if obs.kind == 'wave' and player.rect.colliderect(obs.rect) and not player.standing_on_wave:
                game_over = True
        # --- Check for falling into gap ---
        if not player.on_ground and player.rect.bottom >= HEIGHT:
            game_over = True
        # --- Score ---
        score += 1

    # --- Drawing ---
    screen.blit(background_img, (0,0))
    obstacles.draw(screen)
    for obs in obstacles:
        obs.draw(screen)
    player.draw(screen)
    text = font.render(f'Score: {score//10}', True, (255,255,255))
    screen.blit(text, (20, 20))
    if game_over:
        over_text = font.render('GAME OVER! Press R to Restart', True, (255,255,255))
        screen.blit(over_text, (WIDTH//2 - over_text.get_width()//2, HEIGHT//2))
    pygame.display.flip()
    clock.tick(FPS) 