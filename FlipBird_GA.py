import pygame, random, sys, time

# ----------------- Config -----------------
LARGEUR, HAUTEUR = 400, 600
FPS = 60
RAYON = 15
GRAVITE = 0.5
VITESSE_TUYAUX = 3.0
LARGEUR_TUYAU = 60
ECART = 150
JUMP_V = -8.0

# ----------------- Pygame init -----------------
pygame.init()
Ecran = pygame.display.set_mode((LARGEUR, HAUTEUR))
pygame.display.set_caption("Flappy Bird - Manuel & Auto")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 20, bold=True)

# ----------------- Fonctions utiles -----------------
def creer_tuyau():
    hauteur = random.randint(80, HAUTEUR - 220)
    return {"x": LARGEUR, "haut": hauteur, "bas": hauteur + ECART}

def afficher_tuyaux(surface, tuyaux):
    for t in tuyaux:
        pygame.draw.rect(surface, (0,200,0), (t["x"], 0, LARGEUR_TUYAU, t["haut"]))
        pygame.draw.rect(surface, (0,200,0), (t["x"], t["bas"], LARGEUR_TUYAU, HAUTEUR - t["bas"]))

def verifier_collision(o_y, tuyaux):
    if o_y - RAYON < 0 or o_y + RAYON > HAUTEUR:
        return True
    for t in tuyaux:
        if (60 + RAYON > t["x"] and 60 - RAYON < t["x"] + LARGEUR_TUYAU):
            if o_y - RAYON < t["haut"] or o_y + RAYON > t["bas"]:
                return True
    return False

def get_next_pipe(tuyaux, o_x=60):
    if not tuyaux:
        return None
    if tuyaux[0]["x"] + LARGEUR_TUYAU < o_x and len(tuyaux) > 1:
        return tuyaux[1]
    return tuyaux[0]

# ----------------- Bot Automatique (rule-based) -----------------

def bot_rule(o_y, tuyaux):
    if not tuyaux:
        return False
    p = get_next_pipe(tuyaux)
    centre = (p["haut"] + p["bas"]) / 2.0
    diff = o_y - centre
    return diff > 18  # threshold

# ----------------- Jeu -----------------
def main():
    # game state
    mode = None  # "manu" ou "auto"
    running = True
    en_jeu = False

    # joueur
    o_x = 60
    o_y = HAUTEUR / 2.0
    o_v = 0.0
    tuyaux = []
    score = 0
    best_manual = 0
    best_auto = 0
    last_pipe_pass_x = None

    # UI
    MENU_BTNS = {
        "manu": pygame.Rect(120, 200, 160, 50),
        "auto": pygame.Rect(120, 300, 160, 50),
    }
    GAMEOVER_BTNS = {
        "replay": pygame.Rect(120, 320, 160, 50),
        "menu": pygame.Rect(120, 400, 160, 50),
    }

    def reset_game():
        nonlocal o_y, o_v, tuyaux, score, en_jeu, last_pipe_pass_x
        o_y = HAUTEUR / 2.0
        o_v = 0.0
        tuyaux = [creer_tuyau(), creer_tuyau()]
        tuyaux[1]["x"] = tuyaux[0]["x"] + 220
        score = 0
        en_jeu = True
        last_pipe_pass_x = None

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = event.pos
                if mode is None:  # menu
                    if MENU_BTNS["manu"].collidepoint(pos):
                        mode = "manu"; reset_game()
                    elif MENU_BTNS["auto"].collidepoint(pos):
                        mode = "auto"; reset_game()
                else:
                    if not en_jeu:
                        if GAMEOVER_BTNS["replay"].collidepoint(pos):
                            reset_game()
                        elif GAMEOVER_BTNS["menu"].collidepoint(pos):
                            mode = None; en_jeu = False

        if not running:
            break

        if not en_jeu:
            # menu affiché
            Ecran.fill((135,206,250))
            title = font.render("Choisis ton mode :", True, (0,0,0))
            Ecran.blit(title, (LARGEUR//2 - title.get_width()//2, 120))
            # boutons
            pygame.draw.rect(Ecran, (200,0,0), MENU_BTNS["manu"])
            Ecran.blit(font.render("Mode Manuel", True, (255,255,255)), (MENU_BTNS["manu"].x+18, MENU_BTNS["manu"].y+13))
            pygame.draw.rect(Ecran, (120,120,120), MENU_BTNS["auto"])
            Ecran.blit(font.render("Mode Auto", True, (255,255,255)), (MENU_BTNS["auto"].x+45, MENU_BTNS["auto"].y+13))
            pygame.display.flip()
            clock.tick(FPS)
            continue

        # ---- LOGIQUE ----
        action = 0
        if mode == "manu":
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE]:
                action = 1
        else:  # mode auto
            action = 1 if bot_rule(o_y, tuyaux) else 0

        if action == 1:
            o_v = JUMP_V

        o_v += GRAVITE
        o_y += o_v

        # tuyaux
        for t in tuyaux:
            t["x"] -= VITESSE_TUYAUX

        if tuyaux[-1]["x"] < LARGEUR - 200:
            new = creer_tuyau()
            new["x"] = tuyaux[-1]["x"] + 220
            tuyaux.append(new)

        if tuyaux and tuyaux[0]["x"] + LARGEUR_TUYAU < o_x and (last_pipe_pass_x != tuyaux[0]["x"]):
            score += 1
            last_pipe_pass_x = tuyaux[0]["x"]

        if tuyaux and tuyaux[0]["x"] + LARGEUR_TUYAU < 0:
            tuyaux.pop(0)

        done = verifier_collision(o_y, tuyaux)
        if done:
            en_jeu = False
            if mode == "manu" and score > best_manual:
                best_manual = score
            if mode == "auto" and score > best_auto:
                best_auto = score

        # ---- RENDU ----
        Ecran.fill((135,206,250))
        afficher_tuyaux(Ecran, tuyaux)
        pygame.draw.circle(Ecran, (255,220,0), (o_x, int(o_y)), RAYON)

        Ecran.blit(font.render(f"Mode: {'MANUEL' if mode=='manu' else 'AUTO'}", True, (0,0,0)), (10,10))
        Ecran.blit(font.render(f"Score: {score}", True, (255,255,255)), (10,40))
        Ecran.blit(font.render(f"Best Manu: {best_manual}", True, (0,0,0)), (LARGEUR-180,10))
        Ecran.blit(font.render(f"Best Auto: {best_auto}", True, (0,0,0)), (LARGEUR-180,40))

        if not en_jeu:
            pygame.draw.rect(Ecran, (0,0,0,128), (20, 140, LARGEUR-40, 180))
            title = font.render("GAME OVER", True, (200,0,0))
            Ecran.blit(title, (LARGEUR//2 - title.get_width()//2, 160))
            sc = font.render(f"Score: {score}", True, (0,0,0))
            Ecran.blit(sc, (LARGEUR//2 - sc.get_width()//2, 200))
            pygame.draw.rect(Ecran, (200,0,0), GAMEOVER_BTNS["replay"])
            Ecran.blit(font.render("Rejouer", True, (255,255,255)), (GAMEOVER_BTNS["replay"].x+40, GAMEOVER_BTNS["replay"].y+15))
            pygame.draw.rect(Ecran, (120,120,120), GAMEOVER_BTNS["menu"])
            Ecran.blit(font.render("Menu", True, (255,255,255)), (GAMEOVER_BTNS["menu"].x+55, GAMEOVER_BTNS["menu"].y+10))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    print("Exited.")

if __name__ == "__main__":
    main()
