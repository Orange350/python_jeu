import pygame
import random
import csv
import os
import matplotlib.pyplot as plt

# =============================================================================
# === Paramètres du jeu ===
# =============================================================================
LARGEUR, HAUTEUR = 600, 600
GRAVITE = 0.5
SAUT = -8
VITESSE_TUYAUX = 3
LARGEUR_TUYAU = 60
ECART = 150
RAYON = 12

# =============================================================================
# DÉFINITION DES COULEURS POUR LE TUYAU
# =============================================================================
WHITE = (255, 255, 255) #Blanc
BLACK = (0, 0, 0) #Noir
RED = (200,10,10) #Vermelho
GREEN = (0, 200, 0) #Vert
DARK_GREEN = (0,100,0) #Vert foncé
BLUE = (0, 120, 255)
DARK_BLUE = (0,50,150) #Blue foncé
GRAY = (200, 200, 200) #Gris
DARK_GRAY = (100, 100, 100) #Gris foncé
LIGHT_BLUE = (173, 216, 230) #Blue claire
PURPLE = (100,50,150) #Purpura
ORANGE = (250,150,0) 
CYAN = (0, 255, 255)
PINK = (180,30,130) #Rose
VIOLET = (150,50,150)
YELLOW = (250,200,10) #Jaune
BROWN = (100,50,10) #Marron


# === Paramètres GA ===
POP_SIZE = 30   
MUTATION_RATE = 0.2

pygame.init()
pygame.mixer.init()  # Initialisation audio

Ecran = pygame.display.set_mode((LARGEUR, HAUTEUR))
pygame.display.set_caption("Flappy Bird - Menu Manu / GA")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 18, bold=True)

# =============================================================================
# === Images de fond des menus===
# =============================================================================
try:
    fond_menu = pygame.image.load("Images/montain_nege.jpg")
    fond_menu = pygame.transform.scale(fond_menu, (LARGEUR, HAUTEUR))

    fond_menu_manu = pygame.image.load("Images/montain_nege.jpg")
    fond_menu_manu = pygame.transform.scale(fond_menu_manu, (LARGEUR, HAUTEUR))

    fond_manu = pygame.image.load("Images/paysage_vert.jpg")
    fond_manu = pygame.transform.scale(fond_manu, (LARGEUR, HAUTEUR))

    fond_ga = pygame.image.load("Images/florest_vert.jpg")
    fond_ga = pygame.transform.scale(fond_ga, (LARGEUR, HAUTEUR))
except Exception as e:
    print("⚠️ Erreur chargement fond :", e)
    fond_menu = fond_manu = fond_ga = None

# =============================================================================
#Image pour le oiseau
# =============================================================================

try:
    bird_img = pygame.image.load("Images/Bird rose.png").convert_alpha()
    bird_img = pygame.transform.scale(bird_img, (40, 30))  # ajuste taille
except Exception as e:
    print("⚠️ Erreur chargement oiseau :", e)
    bird_img = None

# =============================================================================
# === AUDIO ===
# =============================================================================
try:
    son_saut = pygame.mixer.Sound("Sound/Mario Jump.mp3")
    son_mort = pygame.mixer.Sound("Sound/Fail music.wav")
    son_point = pygame.mixer.Sound("Sound/coin.mp3")
    pygame.mixer.music.load("Sound/Fond_Music_retro.mp3")
    pygame.mixer.music.play(-1)  # musique en boucle
except Exception as e:
    print("⚠️ Audio non chargé :", e)

# === Variables sons ON/OFF ===
sound_enabled = True   # effets sonores
music_enabled = True   # musique de fond

# === Historique ===
history_ga = []
history_manu = []

# =============================================================================
# === CSV Files ===
# =============================================================================
CSV_GA = "birds_evolution_ga.csv"
CSV_MANU = "manual_scores.csv"
for file, header in [(CSV_GA, ["Generation", "Bird_ID", "Score"]),
                     (CSV_MANU, ["Game", "Score"])]:
    if not os.path.exists(file):
        with open(file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(header)

# =============================================================================
# === Classe Bot (GA) ===
# =============================================================================
class Bot:
    def __init__(self, threshold=None):
        self.x = 60
        self.y = HAUTEUR // 2
        self.v = 0
        self.alive = True
        self.pipes_passed = 0
        self.threshold = threshold if threshold is not None else random.uniform(-50, 50)

    def update(self, tuyaux):
        if not self.alive: return
        self.v += GRAVITE
        self.y += self.v
        if tuyaux:
            p = tuyaux[0]
            centre = (p["haut"] + p["bas"]) / 2
            if self.y > centre + self.threshold:
                self.v = SAUT
        if self.y - RAYON < 0 or self.y + RAYON > HAUTEUR:
            self.alive = False

            #Pour le son
            if sound_enabled:
                try: son_mort.play() # Audio de mort 
                except: pass

        for t in tuyaux:
            if (self.x + RAYON > t["x"] and self.x - RAYON < t["x"] + LARGEUR_TUYAU):
                if self.y - RAYON < t["haut"] or self.y + RAYON > t["bas"]:
                    self.alive = False
                    #Pour le bouton de son
                    if sound_enabled:
                        try: son_mort.play() # Audio de mort 
                        except: pass
    #Image oiseau
    def draw(self, surface, color=(255,220,0)):
        if self.alive:
            if bird_img:
                surface.blit(bird_img, (self.x - bird_img.get_width()//2, int(self.y) - bird_img.get_height()//2))
            else:
                pygame.draw.circle(surface, color, (self.x, int(self.y)), RAYON)

# =============================================================================
# === Fonctions GA ===
# =============================================================================
def crossover(p1, p2):
    child_threshold = (p1.threshold + p2.threshold) / 2
    if random.random() < MUTATION_RATE:
        child_threshold += random.uniform(-20, 20)
    return Bot(child_threshold)

def next_generation(population, generation):
    population.sort(key=lambda b: b.pipes_passed, reverse=True)
    best_score = population[0].pipes_passed
    avg_score = sum(b.pipes_passed for b in population) / len(population)
    history_ga.append((generation, best_score, avg_score))
    with open(CSV_GA, "a", newline="") as f:
        writer = csv.writer(f)
        for idx, bot in enumerate(population):
            writer.writerow([generation, idx, bot.pipes_passed])
    best = population[:POP_SIZE//4]
    new_pop = []
    while len(new_pop) < POP_SIZE:
        p1, p2 = random.sample(best, 2)
        new_pop.append(crossover(p1, p2))
    return new_pop

# === Tuyaux ===
def creer_tuyau():
    h = random.randint(80, HAUTEUR - 220)
    return {"x": LARGEUR, "haut": h, "bas": h + ECART, "passed": False}

# =============================================================================
# Fonction auxilaire pour dessiner du texte dans le menu principal
# =============================================================================
def draw_text(text, size, x, y, color=WHITE, centered=True):
    font = pygame.font.SysFont(None, size)
    text_surface = font.render(text, True, color)
    if centered:
        text_rect = text_surface.get_rect(center=(x, y))
    else:
        text_rect = text_surface.get_rect(topleft=(x, y))
    Ecran.blit(text_surface, text_rect)
    return text_rect

# =============================================================================
# ==== Fonction utilitaire pour changer la coleur du tuyau ====
# =============================================================================   
def get_pipe_color_by_score(best_score):
    if best_score < 5:
        return (GREEN)        # vert  = (0, 200, 0)
    elif best_score < 10:
        return (ORANGE)      # orange clair = (250,150,0) 
    elif best_score < 15:
        return (RED)      # rouge = (200,10,10) 
    elif best_score < 20:
        return (BROWN)      # Marron = (100,50,10)
    elif best_score < 25:
        return (DARK_GREEN)        # vert foncé = (0,100,0) 
    elif best_score < 30:
        return (DARK_BLUE)       # bleu foncé = (0,50,150) 
    elif best_score < 35:
        return (PURPLE)     # pourpre = (100,50,150) 
    elif best_score < 40:
        return (VIOLET)     # violet = (150,50,150)
    elif best_score < 45:
        return (PINK)     # rose = (180,30,130) 
    else:
        return (DARK_GRAY)    # Gris foncé = (100, 100, 100)
    
# =============================================================================
# === Graphiques ===
# =============================================================================
def update_graph_manu():
    plt.figure(figsize=(6,4))
    plt.clf()
    games = [g for g, _ in history_manu]
    scores = [s for _, s in history_manu]
    plt.plot(games, scores, marker="o", color="green")
    plt.xlabel("Games")
    plt.ylabel("Score")
    plt.title("Evolution du score (Manuel)")
    plt.show()

def update_graph_ga_live():
    plt.clf()
    gens = [g for g, _, _ in history_ga]
    bests = [b for _, b, _ in history_ga]
    avgs = [a for _, _, a in history_ga]
    plt.plot(gens, bests, label="Best Score", color="red")
    plt.plot(gens, avgs, label="Avg Score", color="blue")
    plt.xlabel("Generations")
    plt.ylabel("Score (pipes passed)")
    plt.legend()
    plt.title("Evolution des birds (GA)")
    plt.pause(0.01)

# =============================================================================
# === Dessin boutons ===
# =============================================================================
def draw_game_buttons(buttons):
    mouse_pos = pygame.mouse.get_pos()
    for btn, text in buttons:
        color = (180,180,250) if btn.collidepoint(mouse_pos) else (200,200,200)
        pygame.draw.rect(Ecran, color, btn)
        Ecran.blit(font.render(text, True, (0,0,0)), (btn.x + 10, btn.y + 5))

# =============================================================================
# === Menu avant le mode manuel ===
# =============================================================================
def manual_start_menu():
    start_btn = pygame.Rect(200, 200, 200, 50)
    menu_btn = pygame.Rect(200, 300, 200, 50)
    while True:

        #Image de fond
        if fond_manu:
            Ecran.blit(fond_menu_manu, (0,0))
        else:
            Ecran.fill((150, 200, 250))

        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "quit"
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_btn.collidepoint(event.pos): return "start"
                if menu_btn.collidepoint(event.pos): return "menu"
        draw_game_buttons([(start_btn,"Start"), (menu_btn,"Menu")])
        pygame.display.flip()
        clock.tick(30)

# =============================================================================
# === Menu post-mort pour mode manuel avec graphique ===
# =============================================================================
def manual_game_over_menu():
    restart_btn = pygame.Rect(150, 250, 200, 50)
    menu_btn = pygame.Rect(150, 330, 200, 50)
    graph_btn = pygame.Rect(150, 410, 200, 50)
    while True:
        Ecran.fill((150, 50, 50))
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "quit"
            if event.type == pygame.MOUSEBUTTONDOWN:
                if restart_btn.collidepoint(event.pos): return "restart"
                if menu_btn.collidepoint(event.pos): return "menu"
                if graph_btn.collidepoint(event.pos): update_graph_manu()
        draw_game_buttons([(restart_btn,"Restart"), (menu_btn,"Menu"), (graph_btn,"Graphique")])
        pygame.display.flip()
        clock.tick(30)

# =============================================================================
# === Jeu Manuel ===
# =============================================================================
def play_manual():
    while True:
        game = len(history_manu) + 1
        o_x, o_y, o_v = 60, HAUTEUR//2, 0
        tuyaux = [creer_tuyau()]
        score = 0
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: return "quit"
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE: 
                    o_v = SAUT
                    # Quand l’oiseau saute
                    if sound_enabled:
                        try: 
                         son_saut.play() #Audio de Saut
                        except: pass
                    
            o_v += GRAVITE
            o_y += o_v
            for t in tuyaux: t["x"] -= VITESSE_TUYAUX
            if tuyaux[0]["x"] < -LARGEUR_TUYAU: tuyaux.pop(0)
            if tuyaux[-1]["x"] < LARGEUR - 200: tuyaux.append(creer_tuyau())
            for t in tuyaux:
                if not t["passed"] and t["x"] + LARGEUR_TUYAU < o_x:
                    t["passed"] = True
                    score += 1
                    # Quand on marque un point
                    if sound_enabled:
                        try: son_point.play() # Audio de point
                        except: pass

            collision = False
            if o_y - RAYON < 0 or o_y + RAYON > HAUTEUR: collision = True
            for t in tuyaux:
                if (o_x+RAYON > t["x"] and o_x-RAYON < t["x"]+LARGEUR_TUYAU):
                    if o_y-RAYON < t["haut"] or o_y+RAYON > t["bas"]: collision = True

            #Image de fond
            if fond_manu:
                Ecran.blit(fond_manu, (0,0))
            else:
                Ecran.fill((135,206,250))

            # Coleurs du tuyaux par niveau
            couleur_tuyau = get_pipe_color_by_score(score)

            for t in tuyaux:
                pygame.draw.rect(Ecran, (couleur_tuyau), (t["x"], 0, LARGEUR_TUYAU, t["haut"]))
                pygame.draw.rect(Ecran, (couleur_tuyau), (t["x"], t["bas"], LARGEUR_TUYAU, HAUTEUR-t["bas"]))

            #Image oiseau   
            if bird_img:
                Ecran.blit(bird_img, (o_x - bird_img.get_width()//2, int(o_y) - bird_img.get_height()//2))
            else:
                pygame.draw.circle(Ecran, (255,220,0), (o_x, int(o_y)), RAYON)

            score_txt = font.render(f"Score: {score}", True, (BLACK)) #Noir = (0,0,0)
            Ecran.blit(score_txt, (10, 10))
            pygame.display.flip()
            clock.tick(60)
            if collision: 
                # Quand on perd
                if sound_enabled:
                    try: 
                        son_mort.play() #Audio de mort
                    except: pass
                running = False

        history_manu.append((game, score))
        with open(CSV_MANU, "a", newline="") as f:
            csv.writer(f).writerow([game, score])
        choice = manual_game_over_menu()
        if choice == "restart": continue
        elif choice == "menu": return "menu"
        elif choice == "quit": return "quit"

# =============================================================================
# === Menu post-stop GA ===
# =============================================================================
def ga_post_stop_menu():
    restart_btn = pygame.Rect(150, 250, 200, 50)
    continue_btn = pygame.Rect(150, 330, 200, 50)
    menu_btn = pygame.Rect(150, 410, 200, 50)
    while True:
        Ecran.fill((150, 50, 50))
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "quit"
            if event.type == pygame.MOUSEBUTTONDOWN:
                if restart_btn.collidepoint(event.pos): return "restart"
                if continue_btn.collidepoint(event.pos): return "continue"
                if menu_btn.collidepoint(event.pos): return "menu"
        draw_game_buttons([(restart_btn,"Restart"), (continue_btn,"Continuer"), (menu_btn,"Menu")])
        pygame.display.flip()
        clock.tick(30)

# =============================================================================
# === Jeu GA avec Stop/Menu et post-stop menu ===
# =============================================================================
def play_ga():
    while True:
        population = [Bot() for _ in range(POP_SIZE)]
        tuyaux = [creer_tuyau()]
        plt.ion()
        plt.figure(figsize=(6,4))
        generation = 0
        stop_btn = pygame.Rect(400, 10, 80, 30)
        menu_btn = pygame.Rect(500, 10, 80, 30)

        # Sauvegarde de la génération initiale
        population = next_generation(population, generation)  
        update_graph_ga_live() 

        while True:
            generation += 1
            while any(bot.alive for bot in population):
                for event in pygame.event.get():
                    if event.type == pygame.QUIT: plt.ioff(); plt.show(); return "quit"
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if stop_btn.collidepoint(event.pos):
                            choice = ga_post_stop_menu()
                            if choice == "restart":
                                # Restart GA depuis zéro
                                generation = 0
                                population = [Bot() for _ in range(POP_SIZE)]
                                tuyaux = [creer_tuyau()]
                                history_ga.clear()
                                plt.clf()
                                break
                            elif choice == "continue":
                                # Continuer la partie en cours
                                continue
                            elif choice == "menu":
                                return "menu"
                        if menu_btn.collidepoint(event.pos): return "menu"

                # Déplacement tuyaux
                for t in tuyaux: t["x"] -= VITESSE_TUYAUX
                if tuyaux[0]["x"] < -LARGEUR_TUYAU: tuyaux.pop(0)
                if tuyaux[-1]["x"] < LARGEUR - 200: tuyaux.append(creer_tuyau())

                # Calcul score
                for t in tuyaux:
                    if not t["passed"] and t["x"] + LARGEUR_TUYAU < 60:
                        t["passed"] = True
                        for bot in population:
                            if bot.alive: bot.pipes_passed += 1

                            # Quand on marque un point
                            if sound_enabled:
                                try: 
                                    son_point.play() # Audio de point
                                except: pass

                for bot in population: bot.update(tuyaux)

                #Image de fond
                if fond_ga:
                    Ecran.blit(fond_ga, (0,0))
                else:
                    Ecran.fill((135,206,250))

                best_score = max(bot.pipes_passed for bot in population)
                
                #Couleur du tuyau par niveau
                couleur_tuyau = get_pipe_color_by_score(best_score)

                for t in tuyaux:
                    pygame.draw.rect(Ecran, couleur_tuyau, (t["x"], 0, LARGEUR_TUYAU, t["haut"]))
                    pygame.draw.rect(Ecran, couleur_tuyau, (t["x"], t["bas"], LARGEUR_TUYAU, HAUTEUR-t["bas"]))

                for bot in population: bot.draw(Ecran)
                txt = font.render(f"Gen {generation} | Alive {sum(b.alive for b in population)} |  Score {best_score}", True, (BLACK)) #Noir = (0,0,0)
                Ecran.blit(txt, (10, 10))

                pygame.draw.rect(Ecran, (200,200,200), stop_btn)
                pygame.draw.rect(Ecran, (200,200,200), menu_btn)
                Ecran.blit(font.render("Stop", True, (BLACK)), (stop_btn.x+10, stop_btn.y+5)) #Noir = (0,0,0)
                Ecran.blit(font.render("Menu", True, (BLACK)), (menu_btn.x+10, menu_btn.y+5)) #Noir = (0,0,0)
                pygame.display.flip()
                clock.tick(60)

            population = next_generation(population, generation)
            update_graph_ga_live()
            tuyaux = [creer_tuyau()]
        


# =============================================================================
# === Menu principal ===
# =============================================================================
def menu():

    global music_enabled, sound_enabled

    manu_btn = pygame.Rect(200, 250, 200, 40)
    ga_btn = pygame.Rect(200, 315, 200, 40)
    quit_btn = pygame.Rect(200, 380, 200, 40)
    music_btn = pygame.Rect(200, 445, 200, 40)
    sound_btn = pygame.Rect(200, 500, 200, 40)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                return "quit"
            if event.type == pygame.MOUSEBUTTONDOWN:
                if manu_btn.collidepoint(event.pos): return "manual"
                if ga_btn.collidepoint(event.pos): return "ga"
                if quit_btn.collidepoint(event.pos): return "quit"
                if music_btn.collidepoint(event.pos):
                    music_enabled = not music_enabled
                    if music_enabled:
                        pygame.mixer.music.unpause()
                    else:
                        pygame.mixer.music.pause()
                if sound_btn.collidepoint(event.pos):
                    sound_enabled = not sound_enabled

        #Image de fond du menu
        if fond_menu: 
            Ecran.blit(fond_menu, (0,0))
        else:
            Ecran.fill((100,150,250))


        # === Titre du jeu avec effet ombre ===
        draw_text("FLIPBIRD", 60, LARGEUR//2 + 2, 120 + 2, (BLACK))    # Ombre noire = (0,0,0)
        draw_text("FLIPBIRD", 60, LARGEUR//2, 120, (255, 215, 0))      # Texte doré

        # Phrase d'instruction
        draw_text("Choisissez un mode", 30, LARGEUR//2, 180, (0,0,0)) #Noir (0,0,0)

        #== Boutons ===
        draw_game_buttons([
            (manu_btn,"Mode Manuel"), 
            (ga_btn,"Mode Auto - GA"), 
            (quit_btn,"Quit"),
            (music_btn, f"Musique: {'ON' if music_enabled else 'OFF'}"),
            (sound_btn, f"Effets: {'ON' if sound_enabled else 'OFF'}")
        ])
        pygame.display.flip()
        clock.tick(30)

# === Main ===
if __name__ == "__main__":
    mode = "menu"
    while True:
        if mode=="menu": mode = menu()
        elif mode=="manual": 
            start = manual_start_menu()
            if start=="menu": mode="menu"
            else: mode = play_manual()
        elif mode=="ga": mode = play_ga()
        elif mode=="quit": break
    pygame.quit()
