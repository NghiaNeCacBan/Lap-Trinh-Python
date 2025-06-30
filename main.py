import pygame
import random
import os
import math

# --- Khởi tạo Pygame ---
pygame.init()
pygame.mixer.init()

# --- Cài đặt cơ bản ---
WIDTH, HEIGHT = 800, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invaders: The Enhanced Edition")
CLOCK = pygame.time.Clock()
FPS = 60 # Tăng FPS để hoạt ảnh mượt mà hơn

# --- Màu sắc ---
RED = (255, 0, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
GREY = (100, 100, 100)

# --- Kích thước đối tượng ---
SHIP_WIDTH, SHIP_HEIGHT = 64, 64
ENEMY_SIZE = 64
BOSS_SIZE = 128
BULLET_WIDTH, BULLET_HEIGHT = 16, 40
UPGRADE_ITEM_SIZE = 32

# --- Đường dẫn tài nguyên ---
BASE_DIR = os.path.dirname(__file__)
IMG_DIR = os.path.join(BASE_DIR, "assets", "images")
SND_DIR = os.path.join(BASE_DIR, "assets", "sound")
FONT_DIR = os.path.join(BASE_DIR, "assets", "fonts") # Thư mục fonts mới

# --- Load hình ảnh ---
def load_image(filename, size=None, alpha=True):
    path = os.path.join(IMG_DIR, filename)
    try:
        if alpha:
            img = pygame.image.load(path).convert_alpha()
        else:
            img = pygame.image.load(path).convert()
        if size:
            img = pygame.transform.scale(img, size)
        return img
    except pygame.error as e:
        print(f"Error loading image {filename}: {e}")
        # Trả về một bề mặt trống nếu không tìm thấy ảnh để tránh crash
        return pygame.Surface(size if size else (50, 50), pygame.SRCALPHA)

spaceship_img = load_image("spaceship.png", (SHIP_WIDTH, SHIP_HEIGHT))
enemy_img = load_image("enemy.png", (ENEMY_SIZE, ENEMY_SIZE))
enemy2_img = load_image("enemy2.png", (ENEMY_SIZE, ENEMY_SIZE))
boss_img = load_image("boss.png", (BOSS_SIZE, BOSS_SIZE))
boss2_img = load_image("boss2.png", (BOSS_SIZE, BOSS_SIZE))
bullet_img = load_image("bullet.png", (BULLET_WIDTH, BULLET_HEIGHT))
special_bullet_img = load_image("special_bullet.png", (BULLET_WIDTH, BULLET_HEIGHT))
enemy_bullet_img = load_image("enemy_bullet.png", (BULLET_WIDTH, BULLET_HEIGHT))
background_img = load_image("background.jpg", (WIDTH, HEIGHT)) # Nền chính
# Có thể thêm background_menu.jpg nếu bạn muốn nền riêng cho menu

upgrade_imgs = {
    "weapon": load_image("upgrade_weapon.png", (UPGRADE_ITEM_SIZE, UPGRADE_ITEM_SIZE)),
    "speed": load_image("upgrade_speed.png", (UPGRADE_ITEM_SIZE, UPGRADE_ITEM_SIZE)),
    "life": load_image("upgrade_life.png", (UPGRADE_ITEM_SIZE, UPGRADE_ITEM_SIZE))
}
heart_icon_img = load_image("heart_icon.png", (30, 30)) # Biểu tượng trái tim cho mạng sống
hit_effect_img = load_image("hit_effect.png", (20, 20)) # Hiệu ứng khi đạn trúng

# --- Load âm thanh ---
def load_sound(filename):
    path = os.path.join(SND_DIR, filename)
    try:
        return pygame.mixer.Sound(path)
    except pygame.error as e:
        print(f"Error loading sound {filename}: {e}")
        return None # Trả về None nếu không load được

pygame.mixer.music.load(os.path.join(SND_DIR, "background_music.wav"))
pygame.mixer.music.set_volume(0.4) # Giảm âm lượng nhạc nền một chút

SHOOT_SOUND = load_sound("shoot.wav")
EXPLOSION_SOUND = load_sound("explosion.wav")
HIT_SOUND = load_sound("hit.wav")
POWERUP_SOUND = load_sound("powerup.wav") # Âm thanh nhặt item

# --- Fonts ---
def load_font(filename, size):
    path = os.path.join(FONT_DIR, filename)
    try:
        return pygame.font.Font(path, size)
    except FileNotFoundError:
        print(f"Warning: Custom font '{filename}' not found. Using default Pygame font.")
        return pygame.font.Font(None, size)

# Nên tải font 'PressStart2P-Regular.ttf' từ Google Fonts hoặc Dafont
# và đặt vào thư mục assets/fonts/
FONT = load_font("PressStart2P-Regular.ttf", 24)
LARGE_FONT = load_font("PressStart2P-Regular.ttf", 48)
MEDIUM_FONT = load_font("PressStart2P-Regular.ttf", 36)
SMALL_FONT = load_font("PressStart2P-Regular.ttf", 18)


# --- Các lớp game (giữ nguyên hoặc đã cải tiến) ---
class Spaceship:
    def __init__(self):
        self.x = WIDTH // 2 - SHIP_WIDTH // 2
        self.y = HEIGHT - SHIP_HEIGHT - 10
        self.speed = 6
        self.lives = 3
        self.weapon_level = 1
        self.rect = pygame.Rect(self.x, self.y, SHIP_WIDTH, SHIP_HEIGHT)

    def draw(self):
        WIN.blit(spaceship_img, (self.x, self.y))
        self.rect.topleft = (self.x, self.y) # Cập nhật rect

    def move(self, keys):
        if keys[pygame.K_LEFT] and self.x > 0:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] and self.x < WIDTH - SHIP_WIDTH:
            self.x += self.speed
        if keys[pygame.K_UP] and self.y > 0:
            self.y -= self.speed
        if keys[pygame.K_DOWN] and self.y < HEIGHT - SHIP_HEIGHT:
            self.y += self.speed

class Enemy:
    def __init__(self, x, y, speed_scale=1, stage=1):
        self.x = x
        self.y = y
        self.speed_x = random.choice([-1, 1]) * random.uniform(0.5, 1.5) * speed_scale
        self.speed_y = random.uniform(0.2, 0.6) * speed_scale
        self.stage = stage
        self.rect = pygame.Rect(self.x, self.y, ENEMY_SIZE, ENEMY_SIZE)

    def move(self):
        self.x += self.speed_x
        self.y += self.speed_y
        if self.x <= -ENEMY_SIZE or self.x >= WIDTH:
            self.x = random.choice([-ENEMY_SIZE, WIDTH])
            self.y = random.randint(20, 150)
        self.rect.topleft = (self.x, self.y)

    def draw(self):
        img = enemy_img if self.stage == 1 else enemy2_img
        WIN.blit(img, (self.x, self.y))

class Boss:
    def __init__(self):
        self.x = WIDTH // 2 - BOSS_SIZE // 2
        self.y = 30
        self.speed_x = random.choice([-1, 1]) * 2
        self.speed_y = random.choice([-1, 1]) * 1.5
        self.health = 20
        self.max_health = 20
        self.rect = pygame.Rect(self.x, self.y, BOSS_SIZE, BOSS_SIZE)

    def move(self):
        self.x += self.speed_x
        self.y += self.speed_y
        if self.x <= 0 or self.x >= WIDTH - BOSS_SIZE:
            self.speed_x *= -1
        if self.y <= 0 or self.y >= HEIGHT // 2:
            self.speed_y *= -1
        self.rect.topleft = (self.x, self.y)

    def draw(self):
        WIN.blit(boss_img, (self.x, self.y))
        # Vẽ thanh máu
        pygame.draw.rect(WIN, RED, (self.x, self.y - 10, BOSS_SIZE, 5))
        pygame.draw.rect(WIN, GREEN, (self.x, self.y - 10, BOSS_SIZE * (self.health / self.max_health), 5))

class Boss2(Boss):
    def __init__(self):
        super().__init__()
        self.health = 40
        self.max_health = 40
        self.speed_x = 3
        self.speed_y = 2

    def draw(self):
        WIN.blit(boss2_img, (self.x, self.y))
        # Vẽ thanh máu
        pygame.draw.rect(WIN, RED, (self.x, self.y - 10, BOSS_SIZE, 5))
        pygame.draw.rect(WIN, GREEN, (self.x, self.y - 10, BOSS_SIZE * (self.health / self.max_health), 5))

    def special_attack(self):
        bullets = []
        for angle in range(0, 360, 20):
            rad = math.radians(angle)
            dx = 5 * math.cos(rad)
            dy = 5 * math.sin(rad)
            bullets.append({"x": self.x + BOSS_SIZE//2, "y": self.y + BOSS_SIZE//2, "dx": dx, "dy": dy})
        return bullets

class Bullet:
    def __init__(self, x, y, speed, special=False, is_enemy=False):
        self.x = x
        self.y = y
        self.speed = speed
        self.special = special
        self.is_enemy = is_enemy
        self.dx = 0
        self.dy = speed
        self.rect = pygame.Rect(self.x, self.y, BULLET_WIDTH, BULLET_HEIGHT)

    def draw(self):
        img = enemy_bullet_img if self.is_enemy else (special_bullet_img if self.special else bullet_img)
        WIN.blit(img, (self.x, self.y))

    def move(self):
        self.x += self.dx
        self.y += self.dy
        self.rect.topleft = (self.x, self.y)

class UpgradeItem:
    def __init__(self, x, y, upgrade_type):
        self.x = x
        self.y = y
        self.speed = 2
        self.type = upgrade_type
        self.rect = pygame.Rect(self.x, self.y, UPGRADE_ITEM_SIZE, UPGRADE_ITEM_SIZE)

    def move(self):
        self.y += self.speed
        self.rect.topleft = (self.x, self.y)

    def draw(self):
        WIN.blit(upgrade_imgs[self.type], (self.x, self.y))

class Explosion:
    def __init__(self, x, y, size=64):
        self.frames = [load_image(os.path.join("explosions", f"explosion{i}.png"), (size, size)) for i in range(1, 5)]
        self.index = 0
        self.x = x
        self.y = y
        self.done = False

    def draw(self):
        if self.index < len(self.frames):
            WIN.blit(self.frames[self.index], (self.x, self.y))
            self.index += 1
        else:
            self.done = True

class HitEffect:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.timer = 10 # Hiển thị trong 10 frame
        self.alpha = 255 # Độ trong suốt ban đầu

    def draw(self):
        if self.timer > 0:
            # Tạo một bản sao của ảnh và điều chỉnh alpha
            effect_surface = hit_effect_img.copy()
            effect_surface.set_alpha(self.alpha)
            WIN.blit(effect_surface, (self.x - hit_effect_img.get_width() // 2, self.y - hit_effect_img.get_height() // 2))
            self.timer -= 1
            self.alpha = int(255 * (self.timer / 10)) # Giảm alpha dần dần

# --- Biến trạng thái Game toàn cục ---
# Sẽ được khởi tạo trong reset_game_state()
spaceship = None
stage = 1
waves = 1
wave_enemy_count = 0
enemies = []
player_bullets = []
enemy_bullets = []
upgrade_items = []
explosions = []
hit_effects = [] # Thêm list cho hiệu ứng va chạm
boss_death_explosions_pending = []
explosion_spawn_counter = 0
score = 0
game_over = False
boss = None
background_y = 0 # Vị trí Y cho hiệu ứng cuộn nền

# --- Hàm khởi tạo lại trạng thái game ---
def reset_game_state():
    global spaceship, stage, waves, wave_enemy_count, enemies, player_bullets, enemy_bullets, upgrade_items, explosions, hit_effects, boss_death_explosions_pending, explosion_spawn_counter, score, game_over, boss, background_y

    spaceship = Spaceship()
    stage = 1
    waves = 1
    wave_enemy_count = 10
    enemies = [Enemy(random.choice([-ENEMY_SIZE, WIDTH]), random.randint(20, 150), waves, stage) for _ in range(wave_enemy_count)]
    player_bullets = []
    enemy_bullets = []
    upgrade_items = []
    explosions = []
    hit_effects = []
    boss_death_explosions_pending = []
    explosion_spawn_counter = 0
    score = 0
    game_over = False
    boss = None
    background_y = 0 # Reset nền

# --- Hàm vẽ nền cuộn ---
def draw_scrolling_background():
    global background_y
    # Tăng tốc độ cuộn nền để tạo cảm giác di chuyển
    scroll_speed = 1.5
    background_y += scroll_speed
    if background_y > HEIGHT:
        background_y = 0
    WIN.blit(background_img, (0, background_y))
    WIN.blit(background_img, (0, background_y - HEIGHT)) # Vẽ thêm một ảnh nền bên trên để tạo hiệu ứng cuộn liên tục

# --- Hàm vẽ HUD (Heads-Up Display) ---
def draw_hud():
    score_text = FONT.render(f"SCORE: {score}", True, WHITE)
    WIN.blit(score_text, (10, 10))

    # Vẽ mạng sống bằng biểu tượng trái tim
    for i in range(spaceship.lives):
        WIN.blit(heart_icon_img, (WIDTH - 40 - i * 35, 10)) # Cách nhau 35 pixel

    weapon_text = FONT.render(f"WEAPON: {spaceship.weapon_level}", True, WHITE)
    WIN.blit(weapon_text, (10, 40))

    stage_text = FONT.render(f"STAGE: {stage}", True, YELLOW)
    WIN.blit(stage_text, (WIDTH // 2 - stage_text.get_width() // 2, 10))

    if not boss: # Chỉ hiển thị sóng khi không có boss
        wave_text = FONT.render(f"WAVE: {waves}", True, YELLOW)
        WIN.blit(wave_text, (WIDTH // 2 - wave_text.get_width() // 2, 40))

# --- Hàm xử lý va chạm ---
def handle_collisions():
    global score, game_over, boss, stage, waves, wave_enemy_count

    # Va chạm đạn người chơi với kẻ thù
    for bullet in player_bullets[:]:
        for enemy in enemies[:]:
            if bullet.rect.colliderect(enemy.rect):
                explosions.append(Explosion(enemy.x, enemy.y))
                EXPLOSION_SOUND.play()
                hit_effects.append(HitEffect(bullet.x, bullet.y)) # Thêm hiệu ứng va chạm
                
                if random.random() < 0.2: # Tăng tỉ lệ rơi nâng cấp
                    upgrade_type = random.choice(["weapon", "speed", "life"])
                    upgrade_items.append(UpgradeItem(enemy.x, enemy.y, upgrade_type))
                
                enemies.remove(enemy)
                if bullet in player_bullets: # Kiểm tra lại để tránh lỗi nếu đạn đã bị xóa
                    player_bullets.remove(bullet)
                score += 10
                break # Đạn chỉ trúng 1 kẻ thù

    # Va chạm đạn người chơi với boss
    if boss:
        for bullet in player_bullets[:]:
            if bullet.rect.colliderect(boss.rect):
                boss.health -= 1
                HIT_SOUND.play()
                hit_effects.append(HitEffect(bullet.x, bullet.y)) # Thêm hiệu ứng va chạm
                if bullet in player_bullets:
                    player_bullets.remove(bullet)
                
                if boss.health <= 0:
                    for _ in range(50): # Nhiều vụ nổ hơn khi boss chết
                        ex_x = boss.x + random.randint(0, BOSS_SIZE - 64)
                        ex_y = boss.y + random.randint(0, BOSS_SIZE - 64)
                        boss_death_explosions_pending.append((ex_x, ex_y))
                    
                    score += 200 if stage == 1 else 500
                    boss = None
                    EXPLOSION_SOUND.play() # Phát âm thanh nổ lớn khi boss chết
                    
                    if stage == 1: # Chuyển sang Stage 2
                        stage = 2
                        waves = 1 # Bắt đầu lại sóng cho Stage 2
                        wave_enemy_count = 15 # Tăng số lượng kẻ thù ở Stage 2
                        # enemies sẽ được tạo ở đầu vòng lặp game khi boss = None và waves = 0 (reset)
                    
                break # Đạn chỉ trúng boss một lần

    # Va chạm đạn kẻ thù với người chơi
    for bullet in enemy_bullets[:]:
        if bullet.rect.colliderect(spaceship.rect):
            spaceship.lives -= 1
            HIT_SOUND.play()
            explosions.append(Explosion(spaceship.x, spaceship.y, SHIP_WIDTH)) # Nổ nhỏ khi người chơi bị trúng
            enemy_bullets.remove(bullet)
            if spaceship.lives <= 0:
                game_over = True

    # Va chạm kẻ thù với người chơi (nếu kẻ thù chạm vào tàu)
    for enemy in enemies[:]:
        if enemy.rect.colliderect(spaceship.rect):
            spaceship.lives -= 1
            EXPLOSION_SOUND.play()
            enemies.remove(enemy)
            explosions.append(Explosion(enemy.x, enemy.y)) # Kẻ thù nổ khi chạm tàu
            if spaceship.lives <= 0:
                game_over = True

    # Va chạm vật phẩm nâng cấp với người chơi
    for item in upgrade_items[:]:
        if item.rect.colliderect(spaceship.rect):
            if item.type == "weapon":
                spaceship.weapon_level = min(spaceship.weapon_level + 1, 3) # Max level 3
            elif item.type == "speed":
                spaceship.speed = min(spaceship.speed + 1, 10) # Max speed 10
            elif item.type == "life":
                spaceship.lives += 1
            
            if POWERUP_SOUND: # Chỉ phát nếu load được sound
                POWERUP_SOUND.play()
            upgrade_items.remove(item)

# --- Hàm quản lý tạo sóng và boss ---
def manage_waves_and_bosses():
    global enemies, boss, waves, wave_enemy_count, stage

    if not enemies and not boss: # Nếu không còn kẻ thù và không có boss
        if stage == 1:
            if waves < 3:
                waves += 1
                wave_enemy_count += 5 # Tăng số lượng kẻ thù mỗi sóng
                enemies = [Enemy(random.choice([-ENEMY_SIZE, WIDTH]), random.randint(20, 150), waves, stage) for _ in range(wave_enemy_count)]
            else: # Sau 3 sóng của Stage 1, spawn Boss 1
                boss = Boss()
                waves = 0 # Reset waves cho stage tiếp theo
                enemies = [] # Đảm bảo không còn kẻ thù thường khi boss xuất hiện
        elif stage == 2:
            if waves < 3:
                waves += 1
                wave_enemy_count += 5
                enemies = [Enemy(random.choice([-ENEMY_SIZE, WIDTH]), random.randint(20, 150), waves, stage) for _ in range(wave_enemy_count)]
            else: # Sau 3 sóng của Stage 2, spawn Boss 2
                boss = Boss2()
                waves = 0
                enemies = []
        else: # Stage 2 Boss defeated, game ends with YOU WIN
            return True # Báo hiệu trò chơi đã kết thúc với chiến thắng
    return False # Trò chơi vẫn đang tiếp diễn

# --- Hàm màn hình khởi động (Press Start) ---
def start_screen():
    pygame.mixer.music.stop()
    
    title_text = LARGE_FONT.render("SPACE INVADERS", True, WHITE)
    subtitle_text = MEDIUM_FONT.render("THE ENHANCED EDITION", True, YELLOW)
    press_start_text = FONT.render("PRESS ANY KEY TO START", True, WHITE)
    credit_text = SMALL_FONT.render("Created by YourNameHere", True, GREY) # Thay bằng tên của bạn

    blink_timer = 0
    show_text = True

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                pygame.mixer.music.play(-1)
                return

        WIN.blit(background_img, (0, 0)) # Sử dụng hình nền game cho menu

        # Vẽ tiêu đề chính
        title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 80))
        WIN.blit(title_text, title_rect)

        # Vẽ tiêu đề phụ
        subtitle_rect = subtitle_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30))
        WIN.blit(subtitle_text, subtitle_rect)

        # Hiệu ứng nhấp nháy cho chữ "PRESS ANY KEY TO START"
        blink_timer += 1
        if blink_timer % 30 == 0:
            show_text = not show_text

        if show_text:
            press_start_rect = press_start_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
            WIN.blit(press_start_text, press_start_rect)
        
        # Credit text
        credit_rect = credit_text.get_rect(center=(WIDTH // 2, HEIGHT - 30))
        WIN.blit(credit_text, credit_rect)

        pygame.display.update()
        CLOCK.tick(FPS)

# --- Hàm màn hình Game Over / You Win ---
def end_screen(won=False):
    pygame.mixer.music.stop()
    
    if won:
        main_text = LARGE_FONT.render("YOU WIN!", True, GREEN)
        instruction_text = MEDIUM_FONT.render("CONGRATULATIONS!", True, YELLOW)
    else:
        main_text = LARGE_FONT.render("GAME OVER!", True, RED)
        instruction_text = MEDIUM_FONT.render("YOU FAILED THE GALAXY", True, YELLOW)

    score_text = FONT.render(f"FINAL SCORE: {score}", True, WHITE)
    restart_text = FONT.render("PRESS R TO RESTART", True, WHITE)
    quit_text = FONT.render("PRESS ESC TO QUIT", True, WHITE)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    pygame.mixer.music.play(-1)
                    return True # Báo hiệu để chơi lại
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    exit()

        WIN.blit(background_img, (0, 0))

        main_rect = main_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100))
        instruction_rect = instruction_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40))
        score_rect = score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20))
        restart_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 80))
        quit_rect = quit_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 120))

        WIN.blit(main_text, main_rect)
        WIN.blit(instruction_text, instruction_rect)
        WIN.blit(score_text, score_rect)
        WIN.blit(restart_text, restart_rect)
        WIN.blit(quit_text, quit_rect)
        
        pygame.display.update()
        CLOCK.tick(FPS)

# --- Vòng lặp game chính ---
def game_loop():
    global game_over, score, spaceship, stage, waves, wave_enemy_count, enemies, player_bullets, enemy_bullets, upgrade_items, explosions, hit_effects, boss_death_explosions_pending, explosion_spawn_counter, boss

    reset_game_state() # Đảm bảo trạng thái game được đặt lại

    running = True
    while running:
        CLOCK.tick(FPS)
        draw_scrolling_background() # Vẽ nền cuộn

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if SHOOT_SOUND: # Chỉ phát nếu load được sound
                        SHOOT_SOUND.play()
                    if spaceship.weapon_level == 1:
                        player_bullets.append(Bullet(spaceship.x + SHIP_WIDTH // 2 - BULLET_WIDTH // 2, spaceship.y, -10)) # Đạn nhanh hơn
                    else:
                        player_bullets.append(Bullet(spaceship.x + SHIP_WIDTH // 2 - 25, spaceship.y, -10, special=True))
                        player_bullets.append(Bullet(spaceship.x + SHIP_WIDTH // 2, spaceship.y, -10, special=True))
                        player_bullets.append(Bullet(spaceship.x + SHIP_WIDTH // 2 + 25, spaceship.y, -10, special=True))

        if game_over:
            if end_screen(won=False): # Game Over
                reset_game_state()
                pygame.mixer.music.play(-1)
                game_over = False
            else:
                running = False
            continue

        # Kiểm tra điều kiện thắng
        if manage_waves_and_bosses(): # Hàm này trả về True nếu game đã thắng
            if end_screen(won=True): # You Win
                reset_game_state()
                pygame.mixer.music.play(-1)
                game_over = False # Game over sẽ là False, không dùng biến này cho thắng
            else:
                running = False
            continue

        keys = pygame.key.get_pressed()
        spaceship.move(keys)
        spaceship.draw()

        # Cập nhật và vẽ kẻ thù
        for enemy in enemies[:]:
            enemy.move()
            enemy.draw()
            if random.random() < 0.007: # Tần suất bắn của kẻ thù
                enemy_bullets.append(Bullet(enemy.x + ENEMY_SIZE // 2 - BULLET_WIDTH // 2, enemy.y + ENEMY_SIZE, 6, is_enemy=True))

        # Cập nhật và vẽ boss
        if boss:
            boss.move()
            boss.draw()
            if stage == 1 and random.random() < 0.025: # Tần suất bắn của Boss 1
                for dx in [-20, 0, 20]:
                    enemy_bullets.append(Bullet(boss.x + BOSS_SIZE // 2 + dx, boss.y + BOSS_SIZE, 7, is_enemy=True))
            elif stage == 2 and random.random() < 0.015: # Tần suất bắn đặc biệt của Boss 2
                for b in boss.special_attack():
                    bullet = Bullet(b["x"], b["y"], 0, is_enemy=True)
                    bullet.dx = b["dx"]
                    bullet.dy = b["dy"]
                    enemy_bullets.append(bullet)

        # Cập nhật đạn người chơi và loại bỏ đạn ra khỏi màn hình
        for bullet in player_bullets[:]:
            bullet.move()
            bullet.draw()
            if bullet.y < 0:
                player_bullets.remove(bullet)

        # Cập nhật đạn kẻ thù và loại bỏ đạn ra khỏi màn hình
        for bullet in enemy_bullets[:]:
            bullet.move()
            bullet.draw()
            if bullet.y > HEIGHT or bullet.x < 0 or bullet.x > WIDTH:
                enemy_bullets.remove(bullet)

        # Cập nhật các vật phẩm nâng cấp
        for item in upgrade_items[:]:
            item.move()
            item.draw()
            if item.y > HEIGHT:
                upgrade_items.remove(item)

        handle_collisions() # Gọi hàm xử lý va chạm

        # Hiệu ứng nổ khi boss chết (tạo ra nhiều vụ nổ nhỏ)
        explosion_spawn_counter += 1
        if boss_death_explosions_pending and explosion_spawn_counter % 2 == 0: # Nổ nhanh hơn
            ex_pos = boss_death_explosions_pending.pop(0)
            explosions.append(Explosion(ex_pos[0], ex_pos[1], random.randint(40, 80))) # Kích thước vụ nổ ngẫu nhiên
            # EXPLOSION_SOUND.play() # Có thể play ở đây nếu muốn âm thanh mỗi vụ nổ nhỏ

        # Vẽ các vụ nổ
        for explosion in explosions[:]:
            explosion.draw()
            if explosion.done:
                explosions.remove(explosion)
        
        # Vẽ hiệu ứng va chạm
        for effect in hit_effects[:]:
            effect.draw()
            if effect.timer <= 0:
                hit_effects.remove(effect)

        draw_hud() # Vẽ HUD cuối cùng để nó luôn ở trên cùng

        pygame.display.update()

    pygame.quit()

# --- Logic chạy game ---
if __name__ == "__main__":
    start_screen() # Hiển thị màn hình "Press Start" đầu tiên
    game_loop()    # Sau đó, bắt đầu vòng lặp game chính