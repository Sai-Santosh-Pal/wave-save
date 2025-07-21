import pygame
import random
import sys
import math
import os

def get_asset_path():
    # Get the path to the assets folder
    if getattr(sys, 'frozen', False):
        # If the application is run as a bundle (exe)
        base_path = sys._MEIPASS
    else:
        # If running in development
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, 'assets')

# --- Constants ---
WIDTH, HEIGHT = 800, 600
FPS = 60

# Game states
LANDING_SCREEN = 0
GAME_RUNNING = 1
CREDITS_SCREEN = 2
INSTRUCTIONS_SCREEN = 3  # New state for instructions

# Current game state
game_state = LANDING_SCREEN

# Retro color palette
COLORS = {
    'background': (48, 56, 104),
    'text': (255, 255, 255),
    'button': (255, 192, 0),  # Golden yellow for buttons
    'button_hover': (255, 215, 0),  # Slightly lighter yellow for hover
    'button_text': (0, 0, 0)  # Black text on buttons
}

# --- UI Alignment Configuration ---
UI_CONFIG = {
    # Title configuration
    'TITLE': {
        'x_offset': 0,  # Adjust left/right (+/-)
        'y_percent': 0.1,  # Percentage from top of screen
        'scale':70.0  # Scale factor for the title
    },
    
    # Buttons configuration
    'BUTTONS': {
        'width': 250,  # Width of buttons
        'height': 60,  # Height of buttons
        'y_start_percent': 0.6,  # First button Y position (percentage from top)
        'spacing': 15,  # Spacing between buttons
        'x_offset': 0,  # Horizontal offset from center (+/-)
        'scale': 1.5  # Scale factor for buttons
    },
    
    # Surfer configuration
    'SURFER': {
        'x_percent': 0.75,  # Percentage from left of screen
        'y_percent': 0.35,  # Percentage from top of screen
        'bob_speed': 0.003,  # Speed of bobbing animation
        'bob_amount': 10,  # Amount of bobbing in pixels
        'scale': 1  # Scale factor for surfer
    },
    
    # Instructions configuration
    'INSTRUCTIONS': {
        'title_y_percent': 0.15,
        'text_start_y': 0.3,
        'line_spacing': 40,
        'text_size': 28
    }
}

ASSET_PATH = get_asset_path()

# --- Gap and Speed Scaling ---
INITIAL_GAP = 350  # Increased initial gap in pixels between obstacles
MIN_GAP = 200   # Increased minimum gap in pixels
GAP_DECREASE_RATE = 0.005 #How much the gap decreases per score unit
INITIAL_SCROLL_SPEED = 6
MAX_SCROLL_SPEED = 18
SPEED_INCREASE_RATE = 0.0055  # How much speed increases per score unit

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Wave Safe')
clock = pygame.time.Clock()

# --- Load Sprites ---
def load_sprite(name):
    path = os.path.join(ASSET_PATH, name)
    img = pygame.image.load(path).convert_alpha()
    return [img]

# Load UI elements first
heading_img = pygame.image.load(os.path.join(ASSET_PATH, 'heading.png')).convert_alpha()
start_btn_img = pygame.image.load(os.path.join(ASSET_PATH, 'start.png')).convert_alpha()
credits_btn_img = pygame.image.load(os.path.join(ASSET_PATH, 'credits.png')).convert_alpha()

# Scale buttons according to configuration
start_btn_img = pygame.transform.scale(start_btn_img, 
    (int(UI_CONFIG['BUTTONS']['width'] * UI_CONFIG['BUTTONS']['scale']),
     int(UI_CONFIG['BUTTONS']['height'] * UI_CONFIG['BUTTONS']['scale'])))
credits_btn_img = pygame.transform.scale(credits_btn_img,
    (int(UI_CONFIG['BUTTONS']['width'] * UI_CONFIG['BUTTONS']['scale']),
     int(UI_CONFIG['BUTTONS']['height'] * UI_CONFIG['BUTTONS']['scale'])))

# Load other game sprites
surfer_frames = load_sprite('surfer.png')
shark_frames = load_sprite('shark.png')
stone_frames = load_sprite('stone.png')
wood_frames = load_sprite('wood.png')
pirate_frames = load_sprite('pirate.png')

# --- Sprite Scaling ---
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
# Scale surfer according to configuration
surfer_img = pygame.transform.scale(surfer_img,
    (int(surfer_img.get_width() * UI_CONFIG['SURFER']['scale']),
     int(surfer_img.get_height() * UI_CONFIG['SURFER']['scale'])))

# Scale wave image to desired height, keep original width
# wave_img = scale_to_height(wave_frames[0], WAVE_HEIGHT)
shark_img = scale_to_height(shark_frames[0], OBSTACLE_HEIGHT)
stone_img = scale_to_height(stone_frames[0], OBSTACLE_HEIGHT)
wood_img = scale_to_height(wood_frames[0], OBSTACLE_HEIGHT)
pirate_img = scale_to_height(pirate_frames[0], OBSTACLE_HEIGHT * 1.5)  # Make pirate ship a bit bigger

# --- Asset Dimension Checker ---
def print_asset_dimensions():
    asset_files = ['surfer.png', 'shark.png', 'stone.png', 'wood.png', 'normal_waves.png', 'rainy_waves.png', 'normal_clouds.png', 'rain_clouds.png']
    for fname in asset_files:
        path = os.path.join(ASSET_PATH, fname)
        try:
            img = pygame.image.load(path)
            print(f"{fname}: {img.get_width()} x {img.get_height()}")
        except Exception as e:
            print(f"{fname}: Error loading image - {e}")

# Print asset dimensions at startup
print_asset_dimensions()

# Load background and clouds
background_img = pygame.image.load(os.path.join(ASSET_PATH, 'background.png')).convert()
background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))
# Load rain background for rain level
rain_bg_img = pygame.image.load(os.path.join(ASSET_PATH, 'rain.png')).convert()
rain_bg_img = pygame.transform.scale(rain_bg_img, (WIDTH, HEIGHT))
# Load all cloud and wave images
normal_cloud_img = pygame.image.load(os.path.join(ASSET_PATH, 'normal_clouds.png')).convert_alpha()
normal_cloud_img = pygame.transform.scale(normal_cloud_img, (100, 40))
rain_cloud_img = pygame.image.load(os.path.join(ASSET_PATH, 'rain_clouds.png')).convert_alpha()
rain_cloud_img = pygame.transform.scale(rain_cloud_img, (100, 40))
normal_wave_img = pygame.image.load(os.path.join(ASSET_PATH, 'normal_waves.png')).convert_alpha()
normal_wave_img = scale_to_height(normal_wave_img, WAVE_HEIGHT)
rainy_wave_img = pygame.image.load(os.path.join(ASSET_PATH, 'rainy_waves.png')).convert_alpha()
rainy_wave_img = scale_to_height(rainy_wave_img, WAVE_HEIGHT)

# Set initial images
cloud_img = normal_cloud_img
wave_img = normal_wave_img
current_bg = background_img

clouds = [
    {'x': random.randint(0, WIDTH), 'y': random.randint(20, 120), 'speed': 1.5},
    {'x': random.randint(0, WIDTH), 'y': random.randint(60, 180), 'speed': 1.0},
    {'x': random.randint(0, WIDTH), 'y': random.randint(100, 200), 'speed': 0.7},
]
fading = False
fade_alpha = 0
fade_direction = 1  # 1 for fade out, -1 for fade in
fade_target_bg = None

# Add background offset for parallax
bg_offset = 0
bg_speed = 0.5  # Parallax speed

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
        elif kind == 'pirate':
            self.image = pirate_img
        else:
            self.image = pygame.Surface((40,40), pygame.SRCALPHA)
        self.kind = kind
        self.rect = self.image.get_rect(midbottom=(x, y))
    def update(self):
        self.rect.x -= SCROLL_SPEED
    def draw(self, surface):
        # Removed shadow
        surface.blit(self.image, self.rect)
    def get_mask(self):
        return pygame.mask.from_surface(self.image)

# --- Wave Staircase Obstacle ---
class WaveStaircaseObstacle(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.kind = 'wave_staircase'
        self.x = x
        self.y = y
        
        # Define wave layout
        self.num_rows = 3
        self.waves_per_row = [2, 4, 6]  # Number of waves in each row (top to bottom)
        
        # Calculate size
        self.width = max(self.waves_per_row) * TILE_WIDTH
        self.height = self.num_rows * (WAVE_HEIGHT)  # No extra spacing
        
        # Create surface
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.bottomright = (x, y + 20)  # Move bottom wave down by 20 pixels
        
        # Store wave positions for collision checking
        self.wave_positions = []
        
    def update(self):
        self.x -= SCROLL_SPEED
        self.rect.bottomright = (self.x, self.y + 20)  # Keep bottom wave lower
        
        # Update wave positions
        self.wave_positions = []
        for row in range(self.num_rows):
            # No extra spacing between rows
            row_y = GROUND_Y + 20 - (WAVE_HEIGHT) * (self.num_rows - row)
            for wave in range(self.waves_per_row[row]):
                wave_x = self.rect.right - (wave + 1) * TILE_WIDTH
                
                # Define collision areas for each wave
                wave_rect = pygame.Rect(wave_x, row_y, TILE_WIDTH, WAVE_HEIGHT)
                
                # Create platform area covering the entire wave surface with extra margin
                platform_y = GROUND_Y + 20 - (WAVE_HEIGHT) * (self.num_rows - row) - 15 # Start higher above the wave
                platform_area = pygame.Rect(wave_x - 5, platform_y, TILE_WIDTH + 10, WAVE_HEIGHT)  # Full wave height plus margins
                
                self.wave_positions.append({
                    'rect': wave_rect,
                    'platform_area': platform_area,
                    'row': row,
                    'y': platform_y
                })
        
    def draw(self, surface):
        # Draw each wave
        for wave in self.wave_positions:
            surface.blit(wave_img, wave['rect'])
            
            # Debug visualization - show platform areas
            pygame.draw.rect(surface, (0, 255, 0), wave['platform_area'], 1)

    def check_collision(self, player):
        # First check if player is in any safe zone
        for wave in self.wave_positions:
            platform = wave['platform_area']
            
            # If player is anywhere in the platform area, they're safe
            if platform.colliderect(player.rect):
                # Ensure player stays on the platform
                if player.vel_y >= 0:  # When falling or standing
                    player.rect.bottom = min(player.rect.bottom, platform.bottom)
                    player.vel_y = 0
                    player.is_jumping = False
                    player.on_ground = True
                    player.standing_on_wave = True
                return False  # Always safe in platform area
                
        # If not in any safe zone, check for side collisions
        for wave in self.wave_positions:
            wave_rect = wave['rect']
            if wave_rect.colliderect(player.rect):
                # Only count as collision if clearly not above the wave
                if player.rect.bottom > wave_rect.top + 5:
                    return True
                    
        return False

    def get_mask(self):
        mask_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        for wave in self.wave_positions:
            mask_surface.blit(wave_img, (wave['rect'].x - self.rect.x, wave['rect'].y - self.rect.y))
        return pygame.mask.from_surface(mask_surface)

# --- Player ---
class Player:
    def __init__(self):
        self.image = surfer_img
        self.rect = self.image.get_rect(midbottom=(120, GROUND_Y))
        self.vel_y = 0
        self.is_jumping = False
        self.on_ground = True
        self.standing_on_wave = False  # Track if standing on wave
        self.stretch_timer = 0
        self.stretched = False
        self.normal_img = surfer_img
        # Precompute a stretched version (squished vertically by 2px)
        w, h = self.normal_img.get_width(), self.normal_img.get_height()
        self.stretched_img = pygame.transform.scale(self.normal_img, (w, max(1, h-2)))
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
        # --- Surfer Stretch Animation ---
        if self.on_ground:
            self.stretch_timer += 1
            if self.stretch_timer >= FPS // 2:  # 0.5s at 60 FPS
                self.stretch_timer = 0
                self.stretched = not self.stretched
                if self.stretched:
                    self.image = self.stretched_img
                else:
                    self.image = self.normal_img
                # Keep feet on ground
                self.rect = self.image.get_rect(midbottom=self.rect.midbottom)
        else:
            # Reset to normal image when not surfing
            self.image = self.normal_img
            self.stretched = False
            self.stretch_timer = 0
            self.rect = self.image.get_rect(midbottom=self.rect.midbottom)
    def draw(self, surface):
        # Removed shadow
        surface.blit(self.image, self.rect)
    def get_mask(self):
        return pygame.mask.from_surface(self.image)

# --- Wave Projectile ---
class WaveProjectile(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = wave_img
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 15

    def update(self):
        self.rect.x += self.speed

    def draw(self, surface):
        surface.blit(self.image, self.rect)

# --- UI Elements ---
class ImageButton:
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        
    def draw(self, surface):
        surface.blit(self.image, self.rect)
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        return False

# Calculate button positions using configuration
buttons_x = WIDTH//2 - start_btn_img.get_width()//2 + UI_CONFIG['BUTTONS']['x_offset']
first_button_y = HEIGHT * UI_CONFIG['BUTTONS']['y_start_percent']

# Create buttons using images
start_button = ImageButton(
    buttons_x,
    first_button_y,
    start_btn_img
)
credits_button = ImageButton(
    buttons_x,
    first_button_y + start_btn_img.get_height() + UI_CONFIG['BUTTONS']['spacing'],
    credits_btn_img
)

# --- Main Game Loop ---
player = Player()
waves = []  # No ground wave tiles
obstacles = pygame.sprite.Group()
projectiles = pygame.sprite.Group()  # Group for wave projectiles

# Gap logic
current_gap = INITIAL_GAP
last_obstacle_x = WIDTH

MIN_OBSTACLE_GAP = 120  # Minimum horizontal gap between obstacles

gap_timer = 0
obstacle_timer = 0
score = 0
game_over = False

font = pygame.font.SysFont('Consolas', 32)

# --- Level System ---
level = 1
obstacles_passed = 0
rain_drops = []
RAIN_COLOR = (180, 220, 255)
RAIN_DROP_COUNT = 60
RAIN_DROP_LENGTH = 15
RAIN_DROP_SPEED = 12

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
            
        if game_state == LANDING_SCREEN:
            if start_button.handle_event(event):
                game_state = INSTRUCTIONS_SCREEN  # Go to instructions first
            elif credits_button.handle_event(event):
                game_state = CREDITS_SCREEN
                
        elif game_state == INSTRUCTIONS_SCREEN:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:  # Press SPACE to start game
                    game_state = GAME_RUNNING
                    # Reset game state
                    player = Player()
                    waves = []
                    obstacles.empty()
                    projectiles.empty()
                    score = 0
                    game_over = False
                    current_gap = INITIAL_GAP
                    last_obstacle_x = WIDTH
                    SCROLL_SPEED = INITIAL_SCROLL_SPEED
                    level = 1
                    obstacles_passed = 0
                elif event.key == pygame.K_ESCAPE:
                    game_state = LANDING_SCREEN
                    
        elif game_state == GAME_RUNNING:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_x and not game_over:
                    # Create a new wave projectile from player's position
                    projectile = WaveProjectile(player.rect.centerx, player.rect.centery)
                    projectiles.add(projectile)
                elif event.key == pygame.K_r and game_over:
                    # Reset game state
                    player = Player()
                    waves = []
                    obstacles.empty()
                    projectiles.empty()
                    score = 0
                    game_over = False
                    current_gap = INITIAL_GAP
                    last_obstacle_x = WIDTH
                    SCROLL_SPEED = INITIAL_SCROLL_SPEED
                    level = 1
                    obstacles_passed = 0
                    # Reset weather effects
                    cloud_img = normal_cloud_img
                    wave_img = normal_wave_img
                    current_bg = background_img
                    fading = False
                    fade_alpha = 0
                    rain_drops = []

    # Clear screen
    screen.fill(COLORS['background'])

    if game_state == LANDING_SCREEN:
        # Draw background
        screen.blit(current_bg, (0, 0))
        
        # Draw heading using configuration
        heading_x = WIDTH//2 - heading_img.get_width()//2 + UI_CONFIG['TITLE']['x_offset']
        heading_y = HEIGHT * UI_CONFIG['TITLE']['y_percent']
        screen.blit(heading_img, (heading_x, heading_y))
        
        # Draw buttons
        start_button.draw(screen)
        credits_button.draw(screen)
        
    elif game_state == INSTRUCTIONS_SCREEN:
        # Draw background
        screen.blit(current_bg, (0, 0))
        
        # Create a semi-transparent overlay
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.fill((48, 56, 104))  # Same as COLORS['background']
        overlay.set_alpha(230)  # Almost solid (255 is fully opaque)
        screen.blit(overlay, (0, 0))
        
        # Draw title
        title_font = pygame.font.SysFont('Consolas', 48, bold=True)
        instruction_font = pygame.font.SysFont('Consolas', UI_CONFIG['INSTRUCTIONS']['text_size'])
        
        title = title_font.render("HOW TO PLAY", True, COLORS['button'])
        title_rect = title.get_rect(centerx=WIDTH//2, 
                                  y=HEIGHT * UI_CONFIG['INSTRUCTIONS']['title_y_percent'])
        
        # Add a decorative underline
        pygame.draw.line(screen, COLORS['button'],
                        (title_rect.left, title_rect.bottom + 5),
                        (title_rect.right, title_rect.bottom + 5), 3)
        
        screen.blit(title, title_rect)
        
        # Instructions text
        instructions = [
            "CONTROLS:",
            "SPACE - Jump over obstacles",
            "X - Shoot waves at pirates",
            "ESC - Return to menu",
            "",
            "GAMEPLAY:",
            "- Surf and avoid obstacles",
            "- Shoot pirates to earn bonus points",
            "- Stay on waves to survive",
            "- Watch out for sharks and rocks!",
            "",
            "Press SPACE to start"
        ]
        
        y_pos = HEIGHT * UI_CONFIG['INSTRUCTIONS']['text_start_y']
        for line in instructions:
            if line == "":  # Add extra spacing for empty lines
                y_pos += UI_CONFIG['INSTRUCTIONS']['line_spacing'] // 2
                continue
                
            # Highlight important keys in yellow
            if "SPACE" in line or "X" in line or "ESC" in line:
                parts = line.split(" - ")
                if len(parts) == 2:
                    # Render key in yellow
                    key_text = instruction_font.render(parts[0], True, COLORS['button'])
                    screen.blit(key_text, (WIDTH//4, y_pos))
                    # Render description in white
                    desc_text = instruction_font.render("- " + parts[1], True, COLORS['text'])
                    screen.blit(desc_text, (WIDTH//4 + key_text.get_width(), y_pos))
                else:
                    text = instruction_font.render(line, True, COLORS['button'])
                    text_rect = text.get_rect(x=WIDTH//4, y=y_pos)
                    screen.blit(text, text_rect)
            else:
                text = instruction_font.render(line, True, COLORS['text'])
                text_rect = text.get_rect(x=WIDTH//4, y=y_pos)
                screen.blit(text, text_rect)
            
            y_pos += UI_CONFIG['INSTRUCTIONS']['line_spacing']
            
        # Add a hint at the bottom
        hint_font = pygame.font.SysFont('Consolas', 24)
        hint_text = hint_font.render("Press ESC to return to menu", True, (200, 200, 200))
        hint_rect = hint_text.get_rect(centerx=WIDTH//2, bottom=HEIGHT - 30)
        screen.blit(hint_text, hint_rect)

    elif game_state == GAME_RUNNING:
        if not game_over:
            # Update game elements
            projectiles.update()
            
            # Check for projectile collisions with pirates
            for projectile in projectiles:
                for obstacle in obstacles:
                    if obstacle.kind == 'pirate' and projectile.rect.colliderect(obstacle.rect):
                        obstacle.kill()
                        projectile.kill()
                        score += 50
                
                # Remove projectiles that go off screen
                if projectile.rect.left > WIDTH:
                    projectile.kill()

            # Update game state
            if not fading:
                # Move background for parallax effect
                bg_offset = (bg_offset - bg_speed) % WIDTH
                
                # Update speed and gap
                SCROLL_SPEED = min(INITIAL_SCROLL_SPEED + int(score * SPEED_INCREASE_RATE), MAX_SCROLL_SPEED)
                current_gap = max(INITIAL_GAP - int(score * GAP_DECREASE_RATE), MIN_GAP)
                
                # Update clouds
                for cloud in clouds:
                    cloud['x'] -= cloud['speed']
                    if cloud['x'] < -100:
                        cloud['x'] = WIDTH + random.randint(0, 100)
                        cloud['y'] = random.randint(20, 200)
                
                # Spawn obstacles
                can_spawn = False
                if len(obstacles) == 0:
                    can_spawn = True
                else:
                    last_obs = obstacles.sprites()[-1]
                    if last_obs.rect.x < WIDTH - current_gap:
                        can_spawn = True
                
                if can_spawn:
                    kind = random.choice(['shark', 'stone', 'wood', 'pirate'])
                    obs_y = GROUND_Y
                    obs_x = WIDTH + TILE_WIDTH
                    obstacles.add(Obstacle(kind, obs_x, obs_y))
                    obstacles_passed += 1
                
                # Update obstacles and player
                obstacles.update()
                player.update([], obstacles)
                
                # Check collisions
                for obs in obstacles:
                    if obs.kind != 'wave' and obs.kind != 'pirate':
                        offset = (obs.rect.x - player.rect.x, obs.rect.y - player.rect.y)
                        if player.get_mask().overlap(obs.get_mask(), offset):
                            game_over = True
                    elif obs.kind == 'wave_staircase':
                        if obs.check_collision(player):
                            game_over = True
                    elif obs.kind == 'pirate':
                        if obs.rect.colliderect(player.rect):
                            game_over = True
                
                if not player.on_ground and player.rect.bottom >= HEIGHT:
                    game_over = True
                
                score += 1
                
                # Level progression
                if obstacles_passed // 10 + 1 > level:
                    level += 1
                    if level == 2:
                        rain_drops = [[random.randint(0, WIDTH), random.randint(0, HEIGHT)] 
                                    for _ in range(RAIN_DROP_COUNT)]
                        fading = True
                        fade_alpha = 0
                        fade_direction = 1
                        fade_target_bg = rain_bg_img
                        cloud_img = rain_cloud_img
                        wave_img = rainy_wave_img
                
                if level < 2:
                    cloud_img = normal_cloud_img
                    wave_img = normal_wave_img

        elif game_state == GAME_RUNNING:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_x and not game_over:
                    # Create a new wave projectile from player's position
                    projectile = WaveProjectile(player.rect.centerx, player.rect.centery)
                    projectiles.add(projectile)
                elif event.key == pygame.K_r and game_over:
                    # Reset game state
                    player = Player()
                    waves = []
                    obstacles.empty()
                    projectiles.empty()
                    score = 0
                    game_over = False
                    current_gap = INITIAL_GAP
                    last_obstacle_x = WIDTH
                    SCROLL_SPEED = INITIAL_SCROLL_SPEED
                    level = 1
                    obstacles_passed = 0
                    # Reset weather effects
                    cloud_img = normal_cloud_img
                    wave_img = normal_wave_img
                    current_bg = background_img
                    fading = False
                    fade_alpha = 0
                    rain_drops = []

        # Draw game elements
        screen.blit(current_bg, (int(bg_offset), 0))
        screen.blit(current_bg, (int(bg_offset) - WIDTH, 0))
        
        for cloud in clouds:
            screen.blit(cloud_img, (cloud['x'], cloud['y']))
        
        obstacles.draw(screen)
        for obs in obstacles:
            obs.draw(screen)
        for projectile in projectiles:
            projectile.draw(screen)
        
        player.draw(screen)
        
        if level >= 2:
            for drop in rain_drops:
                pygame.draw.line(screen, RAIN_COLOR, (drop[0], drop[1]), 
                               (drop[0], drop[1]+RAIN_DROP_LENGTH), 2)
                drop[1] += RAIN_DROP_SPEED
                if drop[1] > HEIGHT:
                    drop[0] = random.randint(0, WIDTH)
                    drop[1] = random.randint(-20, 0)
        
        if fading:
            fade_surface = pygame.Surface((WIDTH, HEIGHT))
            fade_surface.fill((0,0,0))
            if fade_direction == 1:
                fade_alpha += 10
                if fade_alpha >= 255:
                    fade_alpha = 255
                    fade_direction = -1
                    current_bg = fade_target_bg
            else:
                fade_alpha -= 10
                if fade_alpha <= 0:
                    fade_alpha = 0
                    fading = False
            fade_surface.set_alpha(fade_alpha)
            screen.blit(fade_surface, (0,0))
        
        text = font.render(f'Score: {score//10}', True, (255,255,255))
        screen.blit(text, (20, 20))
        level_text = font.render(f'Level: {level}', True, (255,255,0))
        screen.blit(level_text, (20, 60))
        
        if game_over:
            over_text = font.render('GAME OVER! Press R to Restart', True, (255,255,255))
            screen.blit(over_text, (WIDTH//2 - over_text.get_width()//2, HEIGHT//2))
            
    elif game_state == CREDITS_SCREEN:
        credits_font = pygame.font.SysFont('Consolas', 32)
        credits_text = [
            "CREDITS",
            "",
            "Game Design & Programming:",
            "Sai Santosh Pal - assistance from AI",
            "",
            "Art & Assets:",
            "AI Generated",
            "",
            "Press ESC to return"
        ]
        
        y_pos = 100
        for line in credits_text:
            text_surface = credits_font.render(line, True, COLORS['text'])
            text_rect = text_surface.get_rect(centerx=WIDTH//2, y=y_pos)
            screen.blit(text_surface, text_rect)
            y_pos += 50

    pygame.display.flip()
    clock.tick(FPS) 