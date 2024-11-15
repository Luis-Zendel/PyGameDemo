import pygame
import random
import pygame.mixer

pygame.init()
pygame.mixer.init()

# Tamaño de pantalla y colores
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Crear ventana de juego
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Game")

# Ruta de imágenes 
IMAGE_PATH = "./Images"

# Cargar música de fondo y efectos de sonido
background_music = f"{IMAGE_PATH}/fondo.wav"
shoot_player_sound = pygame.mixer.Sound(f"{IMAGE_PATH}/shoot_player.mp3")
shoot_enemy_sound = pygame.mixer.Sound(f"{IMAGE_PATH}/shoot_enemy.mp3")

# música de fondo en bucle
pygame.mixer.music.load(background_music)
pygame.mixer.music.play(-1)  # -1 para reproducir en bucle

# Tamaños específicos para las imágenes
PLAYER_SIZE = (50, 50)
ENEMY_SIZE = (40, 40)
BULLET_SIZE = (5, 15)

# Grupos de sprites
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()

# Variables de juego
score = 0
level = 1
player_lives = 3
game_over = False

# Clase Bullet
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, is_enemy=False):
        super().__init__()
        self.image = pygame.Surface(BULLET_SIZE)
        self.image.fill(RED if is_enemy else WHITE)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 10 if is_enemy else -10  # Velocidad hacia abajo si es un disparo enemigo

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT or self.rect.bottom < 0:
            self.kill()  # Elimina la bala si sale de la pantalla

# Clases Base y con Herencia
class SpaceObject(pygame.sprite.Sprite):
    def __init__(self, x, y, health):
        super().__init__()
        self._health = health
        self.rect = self.image.get_rect(center=(x, y))

    def take_damage(self, amount):
        self._health -= amount
        if self._health <= 0:
            self.kill()

class SpaceShip(SpaceObject):
    def __init__(self, x, y):
        self.image = pygame.image.load(f"{IMAGE_PATH}/player.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, PLAYER_SIZE)
        super().__init__(x, y, health=100)
        self.speed = 5

    def move(self, dx, dy):
        self.rect.x += dx * self.speed
        self.rect.y += dy * self.speed
        self.rect.clamp_ip(screen.get_rect())

    def shoot(self):
        bullet = Bullet(self.rect.centerx, self.rect.top)
        all_sprites.add(bullet)
        bullets.add(bullet)
        shoot_player_sound.play()  

class EnemySpaceShip(SpaceObject):
    def __init__(self, x, y):
        self.image = pygame.image.load(f"{IMAGE_PATH}/enemy.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, ENEMY_SIZE)
        super().__init__(x, y, health=50)
        self.speed = random.randint(1, 3)
        self.direction = 1  # Dirección de movimiento (1 hacia la derecha, -1 hacia la izquierda)

    def update(self):
        self.rect.y += self.speed
        if level >= 3:
            self.rect.x += self.direction * self.speed
            if self.rect.left <= 0 or self.rect.right >= SCREEN_WIDTH:
                self.direction *= -1

        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

        if level >= 2 and random.random() < 0.01:
            self.shoot()

    def shoot(self):
        bullet = Bullet(self.rect.centerx, self.rect.bottom, is_enemy=True)
        all_sprites.add(bullet)
        enemy_bullets.add(bullet)
        shoot_enemy_sound.play()  # Reproducir sonido al disparar enemigo

# crear enemigos
def create_enemies():
    for i in range(7):
        x = random.randint(0, SCREEN_WIDTH - ENEMY_SIZE[0])
        y = random.randint(-100, -40)
        enemy = EnemySpaceShip(x, y)
        all_sprites.add(enemy)
        enemies.add(enemy)

# mostrar texto en la pantalla
def display_text(text, font, color, x, y):
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, (x, y))

#  jugador
player = SpaceShip(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50)
all_sprites.add(player)

# Crear enemigos 
create_enemies()

# Fuente para mostrar texto
font = pygame.font.Font(None, 36)

# Bucle principal del juego
running = True
clock = pygame.time.Clock()

while running:
    clock.tick(60)

    # Eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not game_over:
                player.shoot()
            elif event.key == pygame.K_RETURN and not game_over:
                game_over = False
                score = 0
                level = 1
                player_lives = 3
                create_enemies()
                player.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50)
            elif event.key == pygame.K_r and game_over:
                game_over = False
                score = 0
                level = 1
                player_lives = 3
                create_enemies()
                player.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50)
            elif event.key == pygame.K_q and game_over:
                running = False

    # Si el jugador está muerto
    if player_lives <= 0:
        game_over = True

    # Movimiento del jugador
    keys = pygame.key.get_pressed()
    dx = dy = 0
    if keys[pygame.K_LEFT]:
        dx = -1
    if keys[pygame.K_RIGHT]:
        dx = 1
    if keys[pygame.K_UP]:
        dy = -1
    if keys[pygame.K_DOWN]:
        dy = 1
    if not game_over:
        player.move(dx, dy)

    # Actualización de sprites
    all_sprites.update()

    # Colisiones entre balas y enemigos
    for bullet in bullets:
        enemy_hit_list = pygame.sprite.spritecollide(bullet, enemies, True)
        for enemy in enemy_hit_list:
            bullet.kill()
            score += 100  # Sumar 100 puntos por cada enemigo destruido
            if score >= 600 and level == 1:
                level = 2  # Subir al nivel 2 cuando se alcanzan 600 puntos
                create_enemies()
            elif score >= 1000 and level == 2:
                level = 3  # Subir al nivel 3 cuando se alcanzan 1000 puntos
                create_enemies()

    if pygame.sprite.spritecollide(player, enemy_bullets, True):
        player_lives -= 1
    if player_lives <= 0:
        game_over = True

    
    if pygame.sprite.spritecollide(player, enemies, True):
        player_lives -= 1
    if player_lives <= 0:
        game_over = True

    # Si todos los enemigos han sido eliminados, crear más enemigos
    if len(enemies) == 0:
        create_enemies()

    # Dibujar todo
    screen.fill(BLACK)
    all_sprites.draw(screen)

    # Mostrar puntuación, nivel y vidas
    score_text = font.render(f"Score: {score}", True, WHITE)
    level_text = font.render(f"Level: {level}", True, WHITE)
    lives_text = font.render(f"Lives: {player_lives}", True, WHITE)
    screen.blit(score_text, (10, 10))
    screen.blit(level_text, (10, 50))
    screen.blit(lives_text, (10, 90))

    # Mostrar mensaje de muerte
    if game_over:
        display_text("YOU DIE", font, RED, SCREEN_WIDTH // 3, SCREEN_HEIGHT // 3)
        display_text("Press R to restart", font, WHITE, SCREEN_WIDTH // 3, SCREEN_HEIGHT // 2)
        display_text("Press Q to quit", font, WHITE, SCREEN_WIDTH // 3, SCREEN_HEIGHT // 2 + 40)

    pygame.display.flip()

pygame.quit()
