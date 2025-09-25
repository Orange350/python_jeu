import pygame
import random

# === Paramètres du jeu ===
LARGEUR, HAUTEUR = 400, 600
GRAVITE = 0.5
SAUT = -8
VITESSE_TUYAUX = 3
LARGEUR_TUYAU = 60
ECART = 150
RAYON = 12

# === Paramètres GA ===
POP_SIZE = 20
MUTATION_RATE = 0.2

pygame.init()
Ecran = pygame.display.set_mode((LARGEUR, HAUTEUR))
pygame.display.set_caption("Flappy Bird - Manu / GA")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 20, bold=True)

# === Classe Bot (GA) ===
class Bot:
    def __init__(self, threshold=None):
        self.x = 60
        self.y = HAUTEUR // 2
        self.v = 0
        self.alive = True
        self.score = 0
        self.pipes_passed = 0
        self.threshold = threshold if threshold is not None else random.uniform(-50, 50)

    def update(self, tuyaux):
        if not self.alive:
            return
        self.v += GRAVITE
        self.y += self.v

        if tuyaux:
            p = tuyaux[0]
            centre = (p["haut"] + p["bas"]) / 2
            if self.y > centre + self.threshold:
                self.v = SAUT

        if self.y - RAYON < 0 or self.y + RAYON > HAUTEUR:
            self.alive = False
        for t in tuyaux:
            if (self.x + RAYON > t["x"] and self.x - RAYON < t["x"] + LARGEUR_TUYAU):
                if self.y - RAYON < t["haut"] or self.y + RAYON > t["bas"]:
                    self.alive = False

    def draw(self, surface, color=(255,220,0)):
        if self.alive:
            pygame.draw.circle(surface, color, (self.x, int(self.y)), RAYON)

# === Fonctions GA ===
def crossover(p1, p2):
    child_threshold = (p1.threshold + p2.threshold) / 2
    if random.random() < MUTATION_RATE:
        child_threshold += random.uniform(-20, 20)
    return Bot(child_threshold)

def next_generation(population):
    population.sort(key=lambda b: b.pipes_passed, reverse=True)
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

# === Boutons ===
def draw_button(rect, text, color=(180,180,180)):
    pygame.draw.rect(Ecran, color, rect)
    pygame.draw.rect(Ecran, (0,0,0), rect, 2)
    label = font.render(text, True, (0,0,0))
    Ecran.blit(label, (rect.x + 8, rect.y + 5))

# === Jeu Manuel ===
def play_manual():
    o_x, o_y, o_v = 60, HAUTEUR//2, 0
    tuyaux = [creer_tuyau()]
    score, paused = 0, False
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "quit"
            if event.type == pygame.MOUSEBUTTONDOWN:
                if pause_btn.collidepoint(event.pos): paused = True
                if menu_btn.collidepoint(event.pos): return "menu"
                if restart_btn.collidepoint(event.pos): return "restart_manual"
                if resume_btn.collidepoint(event.pos): paused = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not paused: o_v = SAUT

        if paused:
            Ecran.fill((200,200,200))
            draw_button(resume_btn, "Reprendre")
            draw_button(menu_btn, "Menu")
            draw_button(restart_btn, "Restart")
            txt = font.render("⏸ Jeu en pause", True, (0,0,0))
            Ecran.blit(txt, (130, 200))
            pygame.display.flip()
            clock.tick(30)
            continue

        # Gravité + saut
        o_v += GRAVITE
        o_y += o_v

        # Tuyaux
        for t in tuyaux: t["x"] -= VITESSE_TUYAUX
        if tuyaux[0]["x"] < -LARGEUR_TUYAU: tuyaux.pop(0)
        if tuyaux[-1]["x"] < LARGEUR - 200: tuyaux.append(creer_tuyau())

        # Score → compte un tuyau quand franchi
        for t in tuyaux:
            if not t["passed"] and t["x"] + LARGEUR_TUYAU < o_x:
                t["passed"] = True
                score += 1

        # Collisions
        if o_y - RAYON < 0 or o_y + RAYON > HAUTEUR: return "menu"
        for t in tuyaux:
            if (o_x+RAYON > t["x"] and o_x-RAYON < t["x"]+LARGEUR_TUYAU):
                if o_y-RAYON < t["haut"] or o_y+RAYON > t["bas"]: return "menu"

        # Dessin
        Ecran.fill((135,206,250))

        # Couleur change avec score
        if score < 5: couleur_tuyau = (0,200,0)
        elif score < 10: couleur_tuyau = (200,0,0)
        else: couleur_tuyau = (0,0,200)

        for t in tuyaux:
            pygame.draw.rect(Ecran, couleur_tuyau, (t["x"], 0, LARGEUR_TUYAU, t["haut"]))
            pygame.draw.rect(Ecran, couleur_tuyau, (t["x"], t["bas"], LARGEUR_TUYAU, HAUTEUR-t["bas"]))

        pygame.draw.circle(Ecran, (255,220,0), (o_x, int(o_y)), RAYON)

        score_txt = font.render(f"Score: {score}", True, (0,0,0))
        Ecran.blit(score_txt, (10, 10))

        draw_button(pause_btn, "Pause")
        draw_button(restart_btn, "Restart")
        draw_button(menu_btn, "Menu")

        pygame.display.flip()
        clock.tick(60)

# === Jeu GA ===
def play_ga():
    generation = 0
    population = [Bot() for _ in range(POP_SIZE)]
    tuyaux = [creer_tuyau()]
    paused = False

    while True:
        generation += 1

        while any(bot.alive for bot in population):
            for event in pygame.event.get():
                if event.type == pygame.QUIT: return "quit"
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if pause_btn.collidepoint(event.pos): paused = True
                    if menu_btn.collidepoint(event.pos): return "menu"
                    if restart_btn.collidepoint(event.pos): return "restart_ga"
                    if resume_btn.collidepoint(event.pos): paused = False

            if paused:
                Ecran.fill((200,200,200))
                draw_button(resume_btn, "Reprendre")
                draw_button(menu_btn, "Menu")
                draw_button(restart_btn, "Restart")
                txt = font.render("⏸ GA en pause", True, (0,0,0))
                Ecran.blit(txt, (130, 200))
                pygame.display.flip()
                clock.tick(30)
                continue

            # Tuyaux
            for t in tuyaux: t["x"] -= VITESSE_TUYAUX
            if tuyaux[0]["x"] < -LARGEUR_TUYAU: tuyaux.pop(0)
            if tuyaux[-1]["x"] < LARGEUR - 200: tuyaux.append(creer_tuyau())

            # Score GA = tuyaux passés
            for t in tuyaux:
                if not t["passed"] and t["x"] + LARGEUR_TUYAU < 60:  # position bots
                    t["passed"] = True
                    for bot in population: 
                        if bot.alive:
                            bot.pipes_passed += 1

            # Update bots
            for bot in population: bot.update(tuyaux)

            # Dessin
            Ecran.fill((135,206,250))
            best_score = max(bot.pipes_passed for bot in population)

            if best_score < 5: couleur_tuyau = (0,200,0)
            elif best_score < 10: couleur_tuyau = (200,0,0)
            else: couleur_tuyau = (0,0,200)

            for t in tuyaux:
                pygame.draw.rect(Ecran, couleur_tuyau, (t["x"], 0, LARGEUR_TUYAU, t["haut"]))
                pygame.draw.rect(Ecran, couleur_tuyau, (t["x"], t["bas"], LARGEUR_TUYAU, HAUTEUR-t["bas"]))

            for bot in population: bot.draw(Ecran)

            gen_txt = font.render(f"Gen {generation} | Alive {sum(b.alive for b in population)} | Best {best_score}", True, (0,0,0))
            Ecran.blit(gen_txt, (10, 10))

            draw_button(pause_btn, "Pause")
            draw_button(restart_btn, "Restart")
            draw_button(menu_btn, "Menu")

            pygame.display.flip()
            clock.tick(60)

        population = next_generation(population)
        tuyaux = [creer_tuyau()]

# === Menu Principal ===
def menu():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "quit"
            if event.type == pygame.MOUSEBUTTONDOWN:
                if manu_btn.collidepoint(event.pos): return "manual"
                if ga_btn.collidepoint(event.pos): return "ga"

        Ecran.fill((100,150,250))
        draw_button(manu_btn, "Mode Manuel")
        draw_button(ga_btn, "Mode GA")
        pygame.display.flip()
        clock.tick(30)

# === Boutons ===
manu_btn = pygame.Rect(120, 240, 160, 40)
ga_btn   = pygame.Rect(120, 300, 160, 40)
pause_btn = pygame.Rect(300, 10, 80, 30)
resume_btn = pygame.Rect(300, 50, 80, 30)
restart_btn = pygame.Rect(300, 90, 80, 30)
menu_btn = pygame.Rect(300, 130, 80, 30)

# === Lancement ===
if __name__ == "__main__":
    mode = "menu"
    while True:
        if mode=="menu": mode = menu()
        elif mode=="manual": mode = play_manual()
        elif mode=="ga": mode = play_ga()
        elif mode=="restart_manual": mode = "manual"
        elif mode=="restart_ga": mode = "ga"
        elif mode=="quit": break
    pygame.quit()
