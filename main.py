import pygame
import random

pygame.init()

WIDTH, HEIGHT = 800, 600
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invaders - Enemy AI")

clock = pygame.time.Clock()
FPS = 45

# Colors
RED = (255, 0, 0)
ORANGE = (255, 165, 0)

SHIP_WIDTH, SHIP_HEIGHT = 64, 64
ENEMY_SIZE = 64
BOSS_SIZE = 128
BULLET_WIDTH, BULLET_HEIGHT = 16, 40

spaceship_img = pygame.transform.scale(pygame.image.load("assets/images/spaceship.png"), (SHIP_WIDTH, SHIP_HEIGHT))
enemy_img = pygame.transform.scale(pygame.image.load("assets/images/enemy.png"), (ENEMY_SIZE, ENEMY_SIZE))
boss_img = pygame.transform.scale(pygame.image.load("assets/images/boss.png"), (BOSS_SIZE, BOSS_SIZE))
bullet_img = pygame.transform.scale(pygame.image.load("assets/images/bullet.png"), (BULLET_WIDTH, BULLET_HEIGHT))

font = pygame.font.Font(None, 36)

class Spaceship:
    def __init__(self):
        self.x = WIDTH // 2 - SHIP_WIDTH // 2
        self.y = HEIGHT - SHIP_HEIGHT - 10
        self.speed = 6
        self.lives = 3

    def draw(self):
        win.blit(spaceship_img, (self.x, self.y))

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
    def __init__(self, x, y, speed_scale=1):
        self.x = x
        self.y = y
        self.speed_x = random.choice([-1, 1]) * random.uniform(0.5, 1.5) * speed_scale
        self.speed_y = random.uniform(0.2, 0.6) * speed_scale

    def move(self):
        self.x += self.speed_x
        self.y += self.speed_y
        if self.x <= -ENEMY_SIZE or self.x >= WIDTH:
            self.x = random.choice([-ENEMY_SIZE, WIDTH])
            self.y = random.randint(20, 150)

    def draw(self):
        win.blit(enemy_img, (self.x, self.y))

class Boss:
    def __init__(self):
        self.x = WIDTH // 2 - BOSS_SIZE // 2
        self.y = 30
        self.speed_x = random.choice([-1, 1]) * 2
        self.health = 20

    def move(self):
        self.x += self.speed_x
        if self.x <= 0 or self.x >= WIDTH - BOSS_SIZE:
            self.speed_x *= -1

    def draw(self):
        win.blit(boss_img, (self.x, self.y))
        pygame.draw.rect(win, RED, (self.x, self.y - 10, BOSS_SIZE, 5))
        pygame.draw.rect(win, (0, 255, 0), (self.x, self.y - 10, BOSS_SIZE * (self.health / 20), 5))

class Bullet:
    def __init__(self, x, y, speed):
        self.x = x
        self.y = y
        self.speed = speed

    def draw(self):
        win.blit(bullet_img, (self.x, self.y))

    def move(self):
        self.y += self.speed

spaceship = Spaceship()
waves = 1
wave_enemy_count = 10
enemies = [Enemy(random.choice([-ENEMY_SIZE, WIDTH]), random.randint(20, 150), waves) for _ in range(wave_enemy_count)]
player_bullets = []
enemy_bullets = []
score = 0
game_over = False
boss = None
damage = 10

run = True
while run:
    clock.tick(FPS)
    win.fill((0, 0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player_bullets.append(Bullet(spaceship.x + SHIP_WIDTH//2 - BULLET_WIDTH//2, spaceship.y, -7))

    keys = pygame.key.get_pressed()
    spaceship.move(keys)
    spaceship.draw()

    if not enemies and not boss:
        if waves < 3:
            waves += 1
            wave_enemy_count += 5
            enemies = [Enemy(random.choice([-ENEMY_SIZE, WIDTH]), random.randint(20, 150), waves) for _ in range(wave_enemy_count)]
        else:
            boss = Boss()
            damage = 5

    for enemy in enemies[:]:
        enemy.move()
        enemy.draw()
        if random.random() < 0.005:
            enemy_bullets.append(Bullet(enemy.x + ENEMY_SIZE//2 - BULLET_WIDTH//2, enemy.y + ENEMY_SIZE, 4))

    if boss:
        boss.move()
        boss.draw()
        if random.random() < 0.02:
            enemy_bullets.append(Bullet(boss.x + BOSS_SIZE//2 - BULLET_WIDTH//2, boss.y + BOSS_SIZE, 5))

    for bullet in player_bullets[:]:
        bullet.move()
        bullet.draw()
        if bullet.y < 0:
            player_bullets.remove(bullet)
            continue
        for enemy in enemies[:]:
            if enemy.x < bullet.x < enemy.x + ENEMY_SIZE and enemy.y < bullet.y < enemy.y + ENEMY_SIZE:
                enemies.remove(enemy)
                player_bullets.remove(bullet)
                score += 10
                break
        if boss and boss.x < bullet.x < boss.x + BOSS_SIZE and boss.y < bullet.y < boss.y + BOSS_SIZE:
            boss.health -= 1
            player_bullets.remove(bullet)
            if boss.health <= 0:
                score += 200
                boss = None

    for bullet in enemy_bullets[:]:
        bullet.move()
        bullet.draw()
        if spaceship.x < bullet.x < spaceship.x + SHIP_WIDTH and spaceship.y < bullet.y < spaceship.y + SHIP_HEIGHT:
            spaceship.lives -= 1
            enemy_bullets.remove(bullet)
            if spaceship.lives <= 0:
                game_over = True
        if bullet.y > HEIGHT:
            enemy_bullets.remove(bullet)

    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    win.blit(score_text, (10, 10))

    lives_text = font.render(f"Lives: {spaceship.lives}", True, (255, 255, 255))
    win.blit(lives_text, (WIDTH - 130, 10))

    if game_over:
        over_text = font.render("GAME OVER!", True, RED)
        win.blit(over_text, (WIDTH//2 - 100, HEIGHT//2))
        pygame.display.update()
        pygame.time.delay(2000)
        break

    pygame.display.update()

pygame.quit()