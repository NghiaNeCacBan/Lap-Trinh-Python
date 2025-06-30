import pygame
import random

pygame.init()

# Màn hình
WIDTH, HEIGHT = 800, 600
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invaders")

# FPS
clock = pygame.time.Clock()
FPS = 60

# Màu
RED = (255, 0, 0)

# Kích thước
SHIP_WIDTH, SHIP_HEIGHT = 64, 64
ENEMY_SIZE = 64
BOSS_SIZE = 128
BULLET_WIDTH, BULLET_HEIGHT = 8, 20

# Load ảnh
spaceship_img = pygame.transform.scale(pygame.image.load("assets/images/spaceship.png"), (SHIP_WIDTH, SHIP_HEIGHT))
enemy_img = pygame.transform.scale(pygame.image.load("assets/images/enemy.png"), (ENEMY_SIZE, ENEMY_SIZE))
boss_img = pygame.transform.scale(pygame.image.load("assets/images/boss.png"), (BOSS_SIZE, BOSS_SIZE))
bullet_img = pygame.transform.scale(pygame.image.load("assets/images/bullet.png"), (BULLET_WIDTH, BULLET_HEIGHT))

# Class
class Spaceship:
    def __init__(self):
        self.x = WIDTH // 2 - SHIP_WIDTH // 2
        self.y = HEIGHT - SHIP_HEIGHT - 10
        self.speed = 6

    def draw(self):
        win.blit(spaceship_img, (self.x, self.y))

    def move(self, keys):
        if keys[pygame.K_LEFT] and self.x > 0:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] and self.x < WIDTH - SHIP_WIDTH:
            self.x += self.speed

class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed_x = 1.5

    def draw(self):
        win.blit(enemy_img, (self.x, self.y))

class Boss:
    def __init__(self):
        self.x = WIDTH // 2 - BOSS_SIZE // 2
        self.y = 50
        self.health = 5
        self.speed_x = 2

    def draw(self):
        win.blit(boss_img, (self.x, self.y))
        pygame.draw.rect(win, RED, (self.x, self.y - 20, BOSS_SIZE, 10))
        pygame.draw.rect(win, (0, 255, 0), (self.x, self.y - 20, BOSS_SIZE * (self.health / 5), 10))

class Bullet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 8

    def draw(self):
        win.blit(bullet_img, (self.x, self.y))

    def move(self):
        self.y -= self.speed

class EnemyBullet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 5

    def draw(self):
        pygame.draw.rect(win, (255, 50, 50), (self.x, self.y, 6, 15))

    def move(self):
        self.y += self.speed

# Hàm tạo enemy
def create_enemies(count):
    enemies = []
    while len(enemies) < count:
        new_x = random.randint(0, WIDTH - ENEMY_SIZE)
        new_y = random.randint(20, 150)
        overlap = False
        for e in enemies:
            if abs(e.x - new_x) < ENEMY_SIZE and abs(e.y - new_y) < ENEMY_SIZE:
                overlap = True
                break
        if not overlap:
            enemies.append(Enemy(new_x, new_y))
    return enemies

# Khởi tạo
spaceship = Spaceship()
enemies = create_enemies(10)
bullets = []
boss_bullets = []
boss = None

# Game loop
run = True
while run:
    clock.tick(FPS)
    win.fill((0, 0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    keys = pygame.key.get_pressed()
    spaceship.move(keys)

    # Bắn
    if keys[pygame.K_SPACE]:
        if len(bullets) < 50:
            bullets.append(Bullet(spaceship.x + SHIP_WIDTH // 2 - BULLET_WIDTH // 2, spaceship.y))

    spaceship.draw()

    # Enemy logic
    move_down = False
    for enemy in enemies:
        if enemy.x <= 0 or enemy.x >= WIDTH - ENEMY_SIZE:
            move_down = True
            break

    for enemy in enemies:
        if move_down:
            enemy.speed_x *= -1
            enemy.y += 20
        enemy.x += enemy.speed_x
        enemy.draw()

    # Khi hết enemy thì sinh boss
    if len(enemies) == 0 and boss is None:
        boss = Boss()

    # Boss logic
    if boss:
        boss.x += boss.speed_x
        if boss.x <= 0 or boss.x >= WIDTH - BOSS_SIZE:
            boss.speed_x *= -1

        boss.draw()

        if random.random() < 0.01:
            boss_bullets.append(EnemyBullet(boss.x + BOSS_SIZE // 2, boss.y + BOSS_SIZE))

    # Boss bullet
    for b_bullet in boss_bullets[:]:
        b_bullet.move()
        b_bullet.draw()

        # Va chạm với spaceship
        if spaceship.x < b_bullet.x < spaceship.x + SHIP_WIDTH and spaceship.y < b_bullet.y < spaceship.y + SHIP_HEIGHT:
            print("Bạn bị boss bắn trúng!")
            boss_bullets.remove(b_bullet)

        elif b_bullet.y > HEIGHT:
            boss_bullets.remove(b_bullet)

    # Bullet người chơi
    for bullet in bullets[:]:
        bullet.move()
        bullet.draw()

        for enemy in enemies[:]:
            if enemy.x < bullet.x < enemy.x + ENEMY_SIZE and enemy.y < bullet.y < enemy.y + ENEMY_SIZE:
                enemies.remove(enemy)
                bullets.remove(bullet)
                break

        if boss:
            if boss.x < bullet.x < boss.x + BOSS_SIZE and boss.y < bullet.y < boss.y + BOSS_SIZE:
                boss.health -= 1
                bullets.remove(bullet)
                if boss.health <= 0:
                    boss = None
                break

        if bullet.y < 0:
            bullets.remove(bullet)

    pygame.display.update()

pygame.quit()
