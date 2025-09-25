import pygame
import sys
import random
import os

# Initialisation de Pygame
pygame.init()

# =============================================================================
# CONSTANTES DU JEU
# =============================================================================
WIDTH, HEIGHT = 400, 600
FPS = 60
GRAVITY = 0.25
FLAP_STRENGTH = -7
PIPE_SPEED = 3
PIPE_GAP = 180  # Augmenté pour faciliter le passage
PIPE_FREQUENCY = 1500

# Création de la fenêtre
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('FlipBird - Version Améliorée')
clock = pygame.time.Clock()

# =============================================================================
# DÉFINITION DES COULEURS
# =============================================================================
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 120, 255)
GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)
LIGHT_BLUE = (173, 216, 230)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
CYAN = (0, 255, 255)
PINK = (255, 192, 203)

# Couleurs des tuyaux par niveau
PIPE_COLORS = [
    (34, 139, 34),    # Vert forêt - Niveau 1
    (255, 165, 0),    # Orange - Niveau 2
    (128, 0, 128),    # Violet - Niveau 3
    (255, 0, 0),      # Rouge - Niveau 4
    (0, 0, 255)       # Bleu - Niveau 5
]

# =============================================================================
# SYSTÈME DE SON
# =============================================================================
class SoundSystem:
    """Système de gestion de son personnalisé"""
    
    def __init__(self):
        self.sounds = {}
        self.music_playing = False
        self.muted = False
        
    def load_sound(self, name, file_path):
        """Charge un son dans le système"""
        try:
            sound = pygame.mixer.Sound(file_path)
            self.sounds[name] = sound
            print(f"Son chargé: {name}")
        except Exception as e:
            print(f"Erreur chargement son {name}: {e}")
            # Créer un son silencieux de remplacement
            self.sounds[name] = pygame.mixer.Sound(pygame.sndarray.array(pygame.Surface((1, 1))))
    
    def play_sound(self, name, volume=0.7):
        """Joue un son"""
        if not self.muted and name in self.sounds:
            self.sounds[name].set_volume(volume)
            self.sounds[name].play()
    
    def play_music(self, file_path, volume=0.5, loops=-1):
        """Joue de la musique de fond"""
        try:
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(loops)
            self.music_playing = True
            print("Musique de fond lancée")
        except Exception as e:
            print(f"Erreur musique: {e}")
    
    def stop_music(self):
        """Arrête la musique"""
        pygame.mixer.music.stop()
        self.music_playing = False

# Initialisation du système de son
sound_system = SoundSystem()

# =============================================================================
# CHARGEMENT DES ASSETS
# =============================================================================
def create_bird_image():
    """Crée une image d'oiseau de taille appropriée"""
    bird_size = 40  # Taille réduite de l'oiseau
    bird_surface = pygame.Surface((bird_size, bird_size), pygame.SRCALPHA)
    
    # Corps de l'oiseau (jaune)
    pygame.draw.circle(bird_surface, (255, 255, 0), (bird_size//2, bird_size//2), bird_size//2)
    
    # Œil (noir)
    pygame.draw.circle(bird_surface, BLACK, (bird_size//2 + 10, bird_size//2 - 8), 4)
    
    # Bec (rouge)
    pygame.draw.polygon(bird_surface, RED, [
        (bird_size//2 + 15, bird_size//2),
        (bird_size//2 + 25, bird_size//2 - 5),
        (bird_size//2 + 25, bird_size//2 + 5)
    ])
    
    # Aile (orange)
    pygame.draw.ellipse(bird_surface, (255, 165, 0), (5, bird_size//2, 15, 10))
    
    return bird_surface

def create_pipe_image(width, height, color):
    """Crée une image de tuyau"""
    pipe_surface = pygame.Surface((width, height))
    pipe_surface.fill(color)
    pygame.draw.rect(pipe_surface, BLACK, (0, 0, width, height), 3)
    return pipe_surface

# Création des images
bird_img = create_bird_image()
pipe_img = create_pipe_image(80, 400, GREEN)

# Chargement des sons
try:
    sound_system.load_sound("flap", "assets/flap.wav")
    sound_system.load_sound("point", "assets/point.wav")
    sound_system.load_sound("hit", "assets/hit.wav")
    sound_system.load_sound("click", "assets/click.wav")
    sound_system.play_music("assets/background_music.mp3")
except:
    print("Sons non chargés, utilisation des placeholders")

# =============================================================================
# FOND PERSONNALISÉ
# =============================================================================
def create_custom_background():
    """Crée un fond de jeu personnalisé avec dégradé et éléments"""
    background = pygame.Surface((WIDTH, HEIGHT))
    
    # Dégradé de bleu du haut vers le bas
    for y in range(HEIGHT):
        blue_value = max(100, 200 - y // 4)
        color = (100, 150, blue_value)
        pygame.draw.line(background, color, (0, y), (WIDTH, y))
    
    # Ajouter des nuages
    for _ in range(8):
        x, y = random.randint(0, WIDTH), random.randint(0, HEIGHT//3)
        cloud_color = (220, 220, 220, 180)
        for dx, dy, size in [(0, 0, 25), (15, -5, 20), (-10, 10, 18), (20, 15, 22)]:
            pygame.draw.circle(background, cloud_color, (x + dx, y + dy), size)
    
    return background

background_img = create_custom_background()

# =============================================================================
# CLASSE BOUTON
# =============================================================================
class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.current_color = color
        self.font = pygame.font.SysFont(None, 32)
        
    def draw(self, surface):
        pygame.draw.rect(surface, self.current_color, self.rect, border_radius=10)
        pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=10)
        
        text_surface = self.font.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
        
    def check_hover(self, pos):
        if self.rect.collidepoint(pos):
            self.current_color = self.hover_color
            return True
        else:
            self.current_color = self.color
            return False
            
    def is_clicked(self, pos, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(pos):
                sound_system.play_sound("click")
                return True
        return False

# =============================================================================
# CLASSE BIRD (TAILLE RÉDUITE)
# =============================================================================
class Bird:
    def __init__(self):
        self.x = 100
        self.y = HEIGHT // 2
        self.velocity = 0
        self.angle = 0
        self.img = bird_img
        # Rectangle de collision plus petit que l'image pour plus de fairness
        self.rect = pygame.Rect(self.x - 15, self.y - 15, 30, 30)
        self.flap_cooldown = 0

    def flap(self):
        self.velocity = FLAP_STRENGTH
        self.angle = -30
        sound_system.play_sound("flap")

    def update(self):
        self.velocity += GRAVITY
        self.y += self.velocity
        self.angle += self.velocity * 0.5
        self.angle = max(-30, min(self.angle, 90))
        self.rect.center = (self.x, self.y)
        
        if self.flap_cooldown > 0:
            self.flap_cooldown -= 1

    def draw(self):
        rotated_bird = pygame.transform.rotate(self.img, -self.angle)
        new_rect = rotated_bird.get_rect(center=self.rect.center)
        screen.blit(rotated_bird, new_rect.topleft)

# =============================================================================
# CLASSE PIPE AVEC COULEURS DYNAMIQUES
# =============================================================================
class Pipe:
    def __init__(self, color_level=0):
        self.gap_y = random.randint(220, HEIGHT - 220)  # Position plus centrée
        self.x = WIDTH
        self.width = 80
        self.passed = False
        self.color_level = min(color_level, len(PIPE_COLORS) - 1)
        
        self.update_pipe_color()
        
        self.top_rect = self.top_pipe.get_rect(midbottom=(self.x, self.gap_y - PIPE_GAP // 2))
        self.bottom_rect = self.bottom_pipe.get_rect(midtop=(self.x, self.gap_y + PIPE_GAP // 2))

    def update_pipe_color(self):
        """Met à jour la couleur des tuyaux selon le niveau"""
        pipe_color = PIPE_COLORS[self.color_level]
        pipe_surface = pygame.Surface((self.width, 500))
        pipe_surface.fill(pipe_color)
        pygame.draw.rect(pipe_surface, BLACK, (0, 0, self.width, 500), 3)
        
        self.top_pipe = pygame.transform.flip(pipe_surface, False, True)
        self.bottom_pipe = pipe_surface

    def update(self):
        self.x -= PIPE_SPEED
        self.top_rect.x = self.x - self.width // 2
        self.bottom_rect.x = self.x - self.width // 2

    def draw(self):
        screen.blit(self.top_pipe, self.top_rect)
        screen.blit(self.bottom_pipe, self.bottom_rect)

# =============================================================================
# FONCTIONS AUXILIAIRES
# =============================================================================
def should_bird_flap(bird, pipes):
    """IA AMÉLIORÉE - Décide quand l'oiseau doit battre des ailes"""
    for pipe in pipes:
        # Vérifie si le tuyau est devant l'oiseau et pas encore passé
        if pipe.x + pipe.width > bird.x - 50 and not pipe.passed:
            # Calcul la position idéale pour passer le tuyau
            target_y = pipe.gap_y - 30  # Légèrement au-dessus du centre
            
            # Si l'oiseau est trop bas, bat des ailes
            if bird.y > target_y + 15:  # Marge de 15 pixels
                return True
            # Si l'oiseau est trop haut et descend trop vite, ne fait rien
            elif bird.y < target_y - 20 and bird.velocity > 2:
                return False
            break
    return False

def draw_text(text, size, x, y, color=WHITE, centered=True):
    font = pygame.font.SysFont(None, size)
    text_surface = font.render(text, True, color)
    if centered:
        text_rect = text_surface.get_rect(center=(x, y))
    else:
        text_rect = text_surface.get_rect(topleft=(x, y))
    screen.blit(text_surface, text_rect)
    return text_rect

def get_pipe_color_level(score):
    """Détermine le niveau de couleur des tuyaux selon le score"""
    if score < 5: return 0
    elif score < 10: return 1
    elif score < 15: return 2
    elif score < 20: return 3
    else: return 4

# =============================================================================
# MENU PRINCIPAL
# =============================================================================
def main_menu():
    manual_btn = Button(WIDTH//2 - 100, 250, 200, 50, "Mode Manuel", BLUE, (100, 180, 255))
    auto_btn = Button(WIDTH//2 - 100, 320, 200, 50, "Mode Auto", GREEN, (100, 255, 100))
    quit_btn = Button(WIDTH//2 - 100, 390, 200, 50, "Quitter", RED, (255, 100, 100))
    
    title_y = 100
    title_direction = 1
    
    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        
        title_y += 0.3 * title_direction
        if title_y > 110 or title_y < 90:
            title_direction *= -1
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if manual_btn.is_clicked(mouse_pos, event):
                return "manual"
            if auto_btn.is_clicked(mouse_pos, event):
                return "auto"
            if quit_btn.is_clicked(mouse_pos, event):
                pygame.quit()
                sys.exit()
        
        screen.blit(background_img, (0, 0))
        
        draw_text("FLIPBIRD", 60, WIDTH//2 + 2, title_y + 2, BLACK)
        draw_text("FLIPBIRD", 60, WIDTH//2, title_y, (255, 215, 0))
        draw_text("Choisissez un mode", 30, WIDTH//2, 180, BLACK)
        
        manual_btn.check_hover(mouse_pos)
        auto_btn.check_hover(mouse_pos)
        quit_btn.check_hover(mouse_pos)
        
        manual_btn.draw(screen)
        auto_btn.draw(screen)
        quit_btn.draw(screen)
        
        pygame.display.update()
        clock.tick(FPS)

# =============================================================================
# BOUCLE PRINCIPALE DU JEU
# =============================================================================
def game_loop(game_mode):
    bird = Bird()
    pipes = []
    last_pipe = pygame.time.get_ticks()
    score = 0
    high_score = 0
    game_over = False
    game_paused = False
    game_started = False
    current_color_level = 0

    menu_btn = Button(10, 10, 100, 40, "Menu", GRAY, WHITE)
    restart_btn = Button(WIDTH - 110, 10, 100, 40, "Restart", GREEN, (100, 255, 100))
    pause_btn = Button(WIDTH - 230, 10, 100, 40, "Pause", BLUE, (100, 180, 255))
    start_btn = Button(WIDTH//2 - 100, HEIGHT//2, 200, 50, "Commencer", GREEN, (100, 255, 100))

    running = True
    while running:
        current_time = pygame.time.get_ticks()
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if menu_btn.is_clicked(mouse_pos, event):
                return "menu"
            if restart_btn.is_clicked(mouse_pos, event):
                return "restart"
            if pause_btn.is_clicked(mouse_pos, event):
                game_paused = not game_paused
            if start_btn.is_clicked(mouse_pos, event) and not game_started:
                game_started = True
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not game_paused:
                    if not game_started:
                        game_started = True
                    if not game_over and game_mode == "manual":
                        bird.flap()
                
                if event.key == pygame.K_p:
                    game_paused = not game_paused
                
                if event.key == pygame.K_r and game_over:
                    return "restart"
                
                if event.key == pygame.K_m:
                    return "menu"
                
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        if not game_paused and game_started and not game_over:
            bird.update()

            # Génération de nouveaux tuyaux
            if current_time - last_pipe > PIPE_FREQUENCY:
                pipes.append(Pipe(current_color_level))
                last_pipe = current_time

            # MODE AUTO FONCTIONNEL
            if game_mode == "auto":
                if should_bird_flap(bird, pipes):
                    bird.flap()

            # Mise à jour des tuyaux
            for pipe in pipes[:]:
                pipe.update()
                
                if pipe.x + pipe.width < -100:
                    pipes.remove(pipe)
                
                # Détection des collisions
                if (bird.rect.colliderect(pipe.top_rect) or 
                    bird.rect.colliderect(pipe.bottom_rect) or 
                    bird.y > HEIGHT - 60 or bird.y < -50):
                    sound_system.play_sound("hit")
                    game_over = True
                    high_score = max(high_score, score)
                
                # Détection des points
                if not pipe.passed and pipe.x + pipe.width < bird.x:
                    pipe.passed = True
                    score += 1
                    sound_system.play_sound("point")
                    
                    # Mise à jour de la couleur des tuyaux
                    new_color_level = get_pipe_color_level(score)
                    if new_color_level != current_color_level:
                        current_color_level = new_color_level
                        for existing_pipe in pipes:
                            existing_pipe.color_level = current_color_level
                            existing_pipe.update_pipe_color()

        # DESSIN
        screen.blit(background_img, (0, 0))
        
        for pipe in pipes:
            pipe.draw()
        
        bird.draw()
        
        # Sol
        ground_rect = pygame.Rect(0, HEIGHT - 60, WIDTH, 60)
        pygame.draw.rect(screen, (139, 69, 19), ground_rect)
        for i in range(0, WIDTH, 30):
            pygame.draw.line(screen, (101, 67, 33), (i, HEIGHT - 60), (i, HEIGHT - 50), 2)
        
        # UI
        score_bg = pygame.Surface((200, 80), pygame.SRCALPHA)
        score_bg.fill((0, 0, 0, 128))
        screen.blit(score_bg, (WIDTH//2 - 100, 50))
        
        draw_text(f'Score: {score}', 36, WIDTH // 2, 70)
        draw_text(f'Meilleur: {high_score}', 24, WIDTH // 2, 100)
        
        mode_text = "AUTO" if game_mode == "auto" else "MANUEL"
        mode_color = GREEN if game_mode == "auto" else BLUE
        draw_text(f'Mode: {mode_text}', 24, WIDTH // 2, 130, mode_color)
        
        # Boutons
        menu_btn.check_hover(mouse_pos)
        restart_btn.check_hover(mouse_pos)
        pause_btn.check_hover(mouse_pos)
        
        menu_btn.draw(screen)
        restart_btn.draw(screen)
        pause_btn.draw(screen)
        
        # Écrans overlay
        if not game_started:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))
            
            draw_text('PRÊT À JOUER?', 48, WIDTH//2, HEIGHT//2 - 80, WHITE)
            start_btn.check_hover(mouse_pos)
            start_btn.draw(screen)
        
        if game_paused:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))
            draw_text('PAUSE', 64, WIDTH//2, HEIGHT//2 - 50, WHITE)
        
        if game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))
            draw_text('GAME OVER!', 64, WIDTH//2, HEIGHT//2 - 80, RED)
            draw_text(f'Score: {score}', 48, WIDTH//2, HEIGHT//2 - 20, WHITE)
            draw_text('R pour recommencer', 28, WIDTH//2, HEIGHT//2 + 30, WHITE)

        pygame.display.update()
        clock.tick(FPS)

# =============================================================================
# FONCTION PRINCIPALE
# =============================================================================
def main():
    game_state = "menu"
    game_mode = "manual"
    
    while True:
        if game_state == "menu":
            game_mode = main_menu()
            game_state = "play"
        elif game_state == "play":
            result = game_loop(game_mode)
            if result == "menu":
                game_state = "menu"
            elif result == "restart":
                game_state = "play"

# =============================================================================
# LANCEMENT DU JEU
# =============================================================================
if __name__ == "__main__":
    if not os.path.exists("assets"):
        os.makedirs("assets")
    
    main()