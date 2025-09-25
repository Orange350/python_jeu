import pygame
import random
import math

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
GENERATIONS = 50

pygame.init()
Ecran = pygame.display.set_mode((LARGEUR, HAUTEUR))
pygame.display.set_caption("Flappy Bird - Genetic Algorithm")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 18, bold=True)

# === Classe Bot ===
class Bot:
    def __init__(self, threshold=None):
        self.x = 60
        self.y = HAUTEUR // 2
        self.v = 0
        self.alive = True
        self.score = 0
        self.fitness = 0
        # "ADN" = seuil de saut
        self.threshold = threshold if threshold is not None else random.uniform(-50, 50)

    def update(self, tuyaux):
        if not self.alive:
            return
        self.v += GRAVITE
        self.y += self.v

        # Décision : jump si trop bas par rapport au centre du trou
        if tuyaux:
            p = tuyaux[0]  # tuyau en face
            centre = (p["haut"] + p["bas"]) / 2
            if self.y > centre + self.threshold:
                self.v = SAUT

        # Collision
        if self.y - RAYON < 0 or self.y + RAYON > HAUTEUR:
            self.alive = False
        for t in tuyaux:
            if (self.x + RAYON > t["x"] and self.x - RAYON < t["x"] + LARGEUR_TUYAU):
                if self.y - RAYON < t["haut"] or self.y + RAYON > t["bas"]:
                    self.alive = False

    def draw(self, surface, color=(255,220,0)):
        if self.alive:
            pygame.draw.circle(surface, color, (self.x, int(self.y)), RAYON)

# === Fonctions Génétique ===
def crossover(p1, p2):
    """Croisement entre deux parents"""
    child_threshold = (p1.threshold + p2.threshold) / 2
    if random.random() < MUTATION_RATE:
        child_threshold += random.uniform(-20, 20)
    return Bot(child_threshold)

def next_generation(population):
    # Trier par fitness
    population.sort(key=lambda b: b.fitness, reverse=True)
    best = population[:POP_SIZE//4]  # top 25%
    new_pop = []

    # Reproduction
    while len(new_pop) < POP_SIZE:
        p1, p2 = random.sample(best, 2)
        new_pop.append(crossover(p1, p2))

    return new_pop, best[0].fitness

# === Tuyaux ===
def creer_tuyau():
    h = random.randint(80, HAUTEUR - 220)
    return {"x": LARGEUR, "haut": h, "bas": h + ECART}

# === Boucle d'entraînement GA ===
def entrainer():
    generation = 0
    population = [Bot() for _ in range(POP_SIZE)]
    meilleur_score = 0

    running = True
    while running and generation < GENERATIONS:
        generation += 1
        tuyaux = [creer_tuyau()]
        frame = 0

        while any(bot.alive for bot in population):
            frame += 1
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # Déplacer tuyaux
            for t in tuyaux:
                t["x"] -= VITESSE_TUYAUX
            if tuyaux[0]["x"] < -LARGEUR_TUYAU:
                tuyaux.pop(0)
            if tuyaux[-1]["x"] < LARGEUR - 200:
                tuyaux.append(creer_tuyau())

            # MAJ bots
            for bot in population:
                bot.update(tuyaux)
                if bot.alive:
                    bot.score += 1

            # Affichage
            Ecran.fill((135,206,250))
            for t in tuyaux:
                pygame.draw.rect(Ecran, (0,200,0), (t["x"], 0, LARGEUR_TUYAU, t["haut"]))
                pygame.draw.rect(Ecran, (0,200,0), (t["x"], t["bas"], LARGEUR_TUYAU, HAUTEUR - t["bas"]))
            for bot in population:
                bot.draw(Ecran)

            txt = font.render(f"Gen {generation} | Alive: {sum(b.alive for b in population)}", True, (0,0,0))
            Ecran.blit(txt, (10, 10))
            pygame.display.flip()
            clock.tick(60)

        # Fitness = score total
        for bot in population:
            bot.fitness = bot.score

        # Nouvelle génération
        population, best_fit = next_generation(population)
        meilleur_score = max(meilleur_score, best_fit)
        print(f"Generation {generation} terminée. Meilleur fitness: {best_fit}")

    print(f"Entraînement terminé. Meilleur score global = {meilleur_score}")
    pygame.quit()

# === Lancement ===
if __name__ == "__main__":
    entrainer()
