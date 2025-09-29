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
pygame.display.set_caption("Flappy Bird - GA avec CSV + Graph")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 18, bold=True)

# === Historique pour graphique ===
history = []  # (gen, best, avg)

# === Fichier CSV ===
CSV_FILE = "birds_evolution_table.csv"

# Création du fichier CSV avec en-tête si absent
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Generation", "Bird_ID", "Score"])

def save_generation(population, generation):
    """Sauvegarde tous les oiseaux d'une génération dans le CSV"""
    with open(CSV_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        for idx, bot in enumerate(population):
            writer.writerow([generation, idx, bot.pipes_passed])

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

def next_generation(population, generation):
    population.sort(key=lambda b: b.pipes_passed, reverse=True)
    best_score = population[0].pipes_passed
    avg_score = sum(b.pipes_passed for b in population) / len(population)

    # Ajout à l'historique + CSV
    history.append((generation, best_score, avg_score))
    save_generation(population, generation)

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

# === Graphique en live ===
def update_graph():
    plt.clf()
    gens = [g for g, _, _ in history]
    bests = [b for _, b, _ in history]
    avgs = [a for _, _, a in history]
    plt.plot(gens, bests, label="Best Score", color="red")
    plt.plot(gens, avgs, label="Avg Score", color="blue")
    plt.xlabel("Generations")
    plt.ylabel("Score (pipes passed)")
    plt.legend()
    plt.title("Evolution des birds (GA)")
    plt.pause(0.01)

# === Jeu GA ===
def play_ga():
    generation = 0
    population = [Bot() for _ in range(POP_SIZE)]
    tuyaux = [creer_tuyau()]

    plt.ion()  # mode interactif matplotlib
    plt.figure(figsize=(6,4))

    while True:
        generation += 1

        while any(bot.alive for bot in population):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    plt.ioff()
                    plt.show()
                    return "quit"

            # Tuyaux
            for t in tuyaux: t["x"] -= VITESSE_TUYAUX
            if tuyaux[0]["x"] < -LARGEUR_TUYAU: tuyaux.pop(0)
            if tuyaux[-1]["x"] < LARGEUR - 200: tuyaux.append(creer_tuyau())

            # Score GA = tuyaux passés
            for t in tuyaux:
                if not t["passed"] and t["x"] + LARGEUR_TUYAU < 60:
                    t["passed"] = True
                    for bot in population:
                        if bot.alive:
                            bot.pipes_passed += 1

            # Update bots
            for bot in population: bot.update(tuyaux)

            # Dessin
            Ecran.fill((135,206,250))
            best_score = max(bot.pipes_passed for bot in population)

            couleur_tuyau = (0,200,0) if best_score < 5 else (200,0,0) if best_score < 10 else (0,0,200)
            for t in tuyaux:
                pygame.draw.rect(Ecran, couleur_tuyau, (t["x"], 0, LARGEUR_TUYAU, t["haut"]))
                pygame.draw.rect(Ecran, couleur_tuyau, (t["x"], t["bas"], LARGEUR_TUYAU, HAUTEUR-t["bas"]))

            for bot in population: bot.draw(Ecran)

            gen_txt = font.render(f"Gen {generation} | Alive {sum(b.alive for b in population)} | Best {best_score}", True, (0,0,0))
            Ecran.blit(gen_txt, (10, 10))

            pygame.display.flip()
            clock.tick(60)

        # Nouvelle génération
        population = next_generation(population, generation)
        update_graph()
        tuyaux = [creer_tuyau()]

# === Lancement ===
if __name__ == "__main__":
    play_ga()
    pygame.quit()
