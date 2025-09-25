import pygame
import random
import csv
import os
import matplotlib.pyplot as plt

# === Paramètres du jeu ===
LARGEUR, HAUTEUR = 600, 600
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
pygame.display.set_caption("Flappy Bird - Menu Manu / GA")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 18, bold=True)

# === Historique ===
history_ga = []
history_manu = []

# === CSV Files ===
CSV_GA = "birds_evolution_ga.csv"
CSV_MANU = "manual_scores.csv"
for file, header in [(CSV_GA, ["Generation", "Bird_ID", "Score"]),
                     (CSV_MANU, ["Game", "Score"])]:
    if not os.path.exists(file):
        with open(file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(header)

# === Classe Bot (GA) ===
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

# === Graphiques ===
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

# === Dessin boutons ===
def draw_game_buttons(buttons):
    mouse_pos = pygame.mouse.get_pos()
    for btn, text in buttons:
        color = (180,180,250) if btn.collidepoint(mouse_pos) else (200,200,200)
        pygame.draw.rect(Ecran, color, btn)
        Ecran.blit(font.render(text, True, (0,0,0)), (btn.x + 10, btn.y + 5))

# === Menu avant le mode manuel ===
def manual_start_menu():
    start_btn = pygame.Rect(200, 200, 200, 50)
    menu_btn = pygame.Rect(200, 300, 200, 50)
    while True:
        Ecran.fill((150, 200, 250))
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "quit"
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_btn.collidepoint(event.pos): return "start"
                if menu_btn.collidepoint(event.pos): return "menu"
        draw_game_buttons([(start_btn,"Start"), (menu_btn,"Menu")])
        pygame.display.flip()
        clock.tick(30)

# === Menu post-mort pour mode manuel avec graphique ===
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

# === Jeu Manuel ===
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
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE: o_v = SAUT
            o_v += GRAVITE
            o_y += o_v
            for t in tuyaux: t["x"] -= VITESSE_TUYAUX
            if tuyaux[0]["x"] < -LARGEUR_TUYAU: tuyaux.pop(0)
            if tuyaux[-1]["x"] < LARGEUR - 200: tuyaux.append(creer_tuyau())
            for t in tuyaux:
                if not t["passed"] and t["x"] + LARGEUR_TUYAU < o_x:
                    t["passed"] = True
                    score += 1
            collision = False
            if o_y - RAYON < 0 or o_y + RAYON > HAUTEUR: collision = True
            for t in tuyaux:
                if (o_x+RAYON > t["x"] and o_x-RAYON < t["x"]+LARGEUR_TUYAU):
                    if o_y-RAYON < t["haut"] or o_y+RAYON > t["bas"]: collision = True
            Ecran.fill((135,206,250))
            for t in tuyaux:
                pygame.draw.rect(Ecran, (0,200,0), (t["x"], 0, LARGEUR_TUYAU, t["haut"]))
                pygame.draw.rect(Ecran, (0,200,0), (t["x"], t["bas"], LARGEUR_TUYAU, HAUTEUR-t["bas"]))
            pygame.draw.circle(Ecran, (255,220,0), (o_x, int(o_y)), RAYON)
            score_txt = font.render(f"Score: {score}", True, (0,0,0))
            Ecran.blit(score_txt, (10, 10))
            pygame.display.flip()
            clock.tick(60)
            if collision: running = False
        history_manu.append((game, score))
        with open(CSV_MANU, "a", newline="") as f:
            csv.writer(f).writerow([game, score])
        choice = manual_game_over_menu()
        if choice == "restart": continue
        elif choice == "menu": return "menu"
        elif choice == "quit": return "quit"

# === Jeu GA ===
def play_ga():
    generation = 0
    population = [Bot() for _ in range(POP_SIZE)]
    tuyaux = [creer_tuyau()]
    plt.ion()
    plt.figure(figsize=(6,4))
    while True:
        generation += 1
        while any(bot.alive for bot in population):
            for event in pygame.event.get():
                if event.type == pygame.QUIT: plt.ioff(); plt.show(); return "quit"
            for t in tuyaux: t["x"] -= VITESSE_TUYAUX
            if tuyaux[0]["x"] < -LARGEUR_TUYAU: tuyaux.pop(0)
            if tuyaux[-1]["x"] < LARGEUR - 200: tuyaux.append(creer_tuyau())
            for t in tuyaux:
                if not t["passed"] and t["x"] + LARGEUR_TUYAU < 60:
                    t["passed"] = True
                    for bot in population:
                        if bot.alive: bot.pipes_passed += 1
            for bot in population: bot.update(tuyaux)
            Ecran.fill((135,206,250))
            best_score = max(bot.pipes_passed for bot in population)
            for t in tuyaux:
                pygame.draw.rect(Ecran, (0,200,0), (t["x"], 0, LARGEUR_TUYAU, t["haut"]))
                pygame.draw.rect(Ecran, (0,200,0), (t["x"], t["bas"], LARGEUR_TUYAU, HAUTEUR-t["bas"]))
            for bot in population: bot.draw(Ecran)
            txt = font.render(f"Gen {generation} | Best {best_score}", True, (0,0,0))
            Ecran.blit(txt, (10, 10))
            pygame.display.flip()
            clock.tick(60)
        population = next_generation(population, generation)
        update_graph_ga_live()
        tuyaux = [creer_tuyau()]

# === Menu Principal ===
def menu():
    manu_btn = pygame.Rect(200, 200, 200, 50)
    ga_btn = pygame.Rect(200, 300, 200, 50)
    quit_btn = pygame.Rect(200, 400, 200, 50)
    while True:
        Ecran.fill((100,150,250))
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "quit"
            if event.type == pygame.MOUSEBUTTONDOWN:
                if manu_btn.collidepoint(event.pos): return "manual"
                if ga_btn.collidepoint(event.pos): return "ga"
                if quit_btn.collidepoint(event.pos): return "quit"
        draw_game_buttons([(manu_btn,"Mode Manuel"), (ga_btn,"Mode GA"), (quit_btn,"Quit")])
        pygame.display.flip()
        clock.tick(30)

# === Main ===
if __name__ == "__main__":
    mode = "menu"
    while True:
        if mode=="menu": mode = menu()
        elif mode=="manual":
            if manual_start_menu() == "quit": break
            mode = play_manual()
        elif mode=="ga": mode = play_ga()
        elif mode=="quit": break
    pygame.quit()
