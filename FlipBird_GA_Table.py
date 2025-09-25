import pygame, random, sys, csv
import matplotlib.pyplot as plt

# ----------------- CONFIG -----------------
LARGEUR, HAUTEUR = 400, 600
FPS = 60
RAYON = 15
GRAVITE = 0.5
VITESSE_TUYAUX = 3.0
LARGEUR_TUYAU = 60
ECART = 150
JUMP_V = -8.0

POP_SIZE = 20
MUT_RATE = 0.2

# ----------------- Pygame init -----------------
pygame.init()
Ecran = pygame.display.set_mode((LARGEUR, HAUTEUR))
pygame.display.set_caption("Flappy Bird - GA & Manu")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 20, bold=True)

# ----------------- GA DATA -----------------
generation = 0
scores_history = []  # pour matplotlib
best_scores_history = []

# init matplotlib
plt.ion()
fig, ax = plt.subplots()
line_mean, = ax.plot([], [], label="Score moyen")
line_best, = ax.plot([], [], label="Meilleur score")
ax.legend()
ax.set_xlabel("Génération")
ax.set_ylabel("Score")

# ----------------- ENV -----------------
def creer_tuyau():
    hauteur = random.randint(80, HAUTEUR - 220)
    return {"x": LARGEUR, "haut": hauteur, "bas": hauteur + ECART}

def afficher_tuyaux(surface, tuyaux, couleur=(0,200,0)):
    for t in tuyaux:
        pygame.draw.rect(surface, couleur, (t["x"], 0, LARGEUR_TUYAU, t["haut"]))
        pygame.draw.rect(surface, couleur, (t["x"], t["bas"], LARGEUR_TUYAU, HAUTEUR - t["bas"]))

def verifier_collision(o_y, tuyaux):
    if o_y - RAYON < 0 or o_y + RAYON > HAUTEUR:
        return True
    for t in tuyaux:
        if (60 + RAYON > t["x"] and 60 - RAYON < t["x"] + LARGEUR_TUYAU):
            if o_y - RAYON < t["haut"] or o_y + RAYON > t["bas"]:
                return True
    return False

# ----------------- GA BOT -----------------
class Bot:
    def __init__(self, threshold=None):
        self.threshold = threshold if threshold is not None else random.uniform(-100,100)
        self.score = 0

    def decide(self, o_y, tuyaux):
        if not tuyaux: return False
        p = tuyaux[0]
        centre = (p["haut"] + p["bas"]) / 2.0
        return (o_y - centre) > self.threshold

def evolve(population):
    global generation, scores_history, best_scores_history

    generation += 1
    population.sort(key=lambda b: b.score, reverse=True)
    best = population[0].score
    avg = sum(b.score for b in population) / len(population)

    # Sauvegarde CSV
    with open("ga_history.csv", "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([generation, avg, best])

    # Update matplotlib
    scores_history.append(avg)
    best_scores_history.append(best)
    line_mean.set_xdata(range(1, len(scores_history)+1))
    line_mean.set_ydata(scores_history)
    line_best.set_xdata(range(1, len(best_scores_history)+1))
    line_best.set_ydata(best_scores_history)
    ax.relim(); ax.autoscale_view()
    plt.draw(); plt.pause(0.001)

    print(f"Génération {generation}: Best={best}, Moyenne={avg:.1f}")

    # sélection
    survivors = population[:POP_SIZE//2]
    children = []
    for i in range(len(survivors)):
        parent = survivors[i]
        child_thr = parent.threshold + random.uniform(-10,10) if random.random()<MUT_RATE else parent.threshold
        children.append(Bot(child_thr))

    new_pop = survivors + children
    while len(new_pop)<POP_SIZE:
        new_pop.append(Bot())
    return new_pop

# ----------------- GAME -----------------
def main():
    global generation
    mode = None
    running = True
    paused = False
    en_jeu = False

    # variables
    o_x = 60
    o_y = HAUTEUR//2
    o_v = 0
    tuyaux = [creer_tuyau(), creer_tuyau()]
    tuyaux[1]["x"] = tuyaux[0]["x"] + 220
    score = 0
    best_manual = 0

    # GA
    population = [Bot() for _ in range(POP_SIZE)]
    current_bot = None
    bot_index = 0

    # boutons
    MENU_BTNS = {"manu": pygame.Rect(120, 200, 160, 50), "ga": pygame.Rect(120, 300, 160, 50)}
    GAME_BTNS = {"pause": pygame.Rect(10, 550, 80, 30), "restart": pygame.Rect(100, 550, 80, 30), "menu": pygame.Rect(190, 550, 80, 30)}

    def reset_game():
        nonlocal o_y,o_v,tuyaux,score,en_jeu
        o_y = HAUTEUR//2; o_v=0
        tuyaux = [creer_tuyau(), creer_tuyau()]
        tuyaux[1]["x"] = tuyaux[0]["x"] + 220
        score=0; en_jeu=True

    while running:
        for event in pygame.event.get():
            if event.type==pygame.QUIT: running=False
            if event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
                pos=event.pos
                if mode is None:
                    if MENU_BTNS["manu"].collidepoint(pos): mode="manu"; reset_game()
                    elif MENU_BTNS["ga"].collidepoint(pos): mode="ga"; reset_game(); current_bot=population[0]; bot_index=0
                else:
                    if GAME_BTNS["pause"].collidepoint(pos): paused = not paused
                    elif GAME_BTNS["restart"].collidepoint(pos): reset_game()
                    elif GAME_BTNS["menu"].collidepoint(pos): mode=None; en_jeu=False

        if not running: break
        if not en_jeu or paused:
            Ecran.fill((135,206,250))
            if mode is None:
                pygame.draw.rect(Ecran,(200,0,0),MENU_BTNS["manu"]); Ecran.blit(font.render("Manuel",True,(255,255,255)),(MENU_BTNS["manu"].x+30,MENU_BTNS["manu"].y+13))
                pygame.draw.rect(Ecran,(120,120,120),MENU_BTNS["ga"]); Ecran.blit(font.render("Auto GA",True,(255,255,255)),(MENU_BTNS["ga"].x+30,MENU_BTNS["ga"].y+13))
            else:
                Ecran.blit(font.render("Pause" if paused else "Game Over",True,(0,0,0)),(150,250))
            pygame.display.flip(); clock.tick(FPS); continue

        # DECISION
        action=0
        if mode=="manu":
            keys=pygame.key.get_pressed()
            if keys[pygame.K_SPACE]: action=1
        elif mode=="ga" and current_bot:
            action=1 if current_bot.decide(o_y,tuyaux) else 0

        if action==1: o_v=JUMP_V

        # physics
        o_v+=GRAVITE; o_y+=o_v
        for t in tuyaux: t["x"]-=VITESSE_TUYAUX
        if tuyaux[-1]["x"]<LARGEUR-200:
            new=creer_tuyau(); new["x"]=tuyaux[-1]["x"]+220; tuyaux.append(new)
        if tuyaux and tuyaux[0]["x"]+LARGEUR_TUYAU<0: tuyaux.pop(0)
        if tuyaux and tuyaux[0]["x"]+LARGEUR_TUYAU<o_x:
            score+=1
            if mode=="ga" and current_bot: current_bot.score+=1
            tuyaux.pop(0)

        # collisions
        done=verifier_collision(o_y,tuyaux)
        if done:
            if mode=="manu":
                best_manual=max(best_manual,score); en_jeu=False
            elif mode=="ga":
                bot_index+=1
                if bot_index>=POP_SIZE:
                    population=evolve(population)
                    bot_index=0; generation+=1
                current_bot=population[bot_index]
                reset_game()

        # DRAW
        Ecran.fill((135,206,250))
        couleur_tuyaux=(0,200,0) if score<5 else (200,0,200) if score<10 else (0,0,200)
        afficher_tuyaux(Ecran,tuyaux,couleur_tuyaux)
        pygame.draw.circle(Ecran,(255,220,0),(o_x,int(o_y)),RAYON)

        # HUD
        Ecran.blit(font.render(f"Score: {score}",True,(255,255,255)),(10,10))
        if mode=="manu":
            Ecran.blit(font.render(f"Best Manu: {best_manual}",True,(0,0,0)),(250,10))
        elif mode=="ga":
            Ecran.blit(font.render(f"Gen: {generation}",True,(0,0,0)),(250,10))
            Ecran.blit(font.render(f"Bot {bot_index+1}/{POP_SIZE}",True,(0,0,0)),(250,30))

        # boutons
        pygame.draw.rect(Ecran,(200,200,0),GAME_BTNS["pause"]); Ecran.blit(font.render("Pause",True,(0,0,0)),(GAME_BTNS["pause"].x+10,GAME_BTNS["pause"].y+5))
        pygame.draw.rect(Ecran,(200,0,0),GAME_BTNS["restart"]); Ecran.blit(font.render("Restart",True,(255,255,255)),(GAME_BTNS["restart"].x+5,GAME_BTNS["restart"].y+5))
        pygame.draw.rect(Ecran,(120,120,120),GAME_BTNS["menu"]); Ecran.blit(font.render("Menu",True,(255,255,255)),(GAME_BTNS["menu"].x+10,GAME_BTNS["menu"].y+5))

        pygame.display.flip(); clock.tick(FPS)

    pygame.quit()
    plt.ioff(); plt.show()

if __name__=="__main__":
    main()
