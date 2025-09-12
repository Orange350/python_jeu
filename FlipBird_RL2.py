import pygame, random, sys

# ---------- Initialisation ----------
pygame.init()
LARGEUR, HAUTEUR = 400, 600
ECRAN = pygame.display.set_mode((LARGEUR, HAUTEUR))
pygame.display.set_caption("Flappy Bird - Auto RL Visualisation")

# Couleurs
BLANC = (255, 255, 255)
VERT = (0, 200, 0)
BLEU_CIEL = (135, 206, 250)
JAUNE = (255, 220, 0)
NOIR = (0, 0, 0)
ROUGE = (200, 0, 0)
GRIS = (100, 100, 100)

# Horloge
FPS = 60
clock = pygame.time.Clock()

# Paramètres du jeu
rayon = 15
gravite = 0.5
vitesse_tuyau = 3.0
largeur_tuyau = 60
ecart = 150
jump_velocity = -8.0

# États / Scores
mode = None   # None = menu, "manu", "auto"
en_jeu = False
score = 0
high_score_manu = 0
high_score_auto = 0

# Variables joueur / tuyaux
oiseau_x = 60
oiseau_y = 0.0
vitesse = 0.0
tuyaux = []

font = pygame.font.SysFont("Arial", 22, bold=True)

# ---------- Fonctions utilitaires ----------
def creer_tuyau():
    hauteur = random.randint(100, HAUTEUR - 200)
    return {"x": LARGEUR, "haut": hauteur, "bas": hauteur + ecart}

def afficher_tuyaux():
    for t in tuyaux:
        pygame.draw.rect(ECRAN, VERT, (t["x"], 0, largeur_tuyau, t["haut"]))
        pygame.draw.rect(ECRAN, VERT, (t["x"], t["bas"], largeur_tuyau, HAUTEUR - t["bas"]))

def verifier_collision():
    if oiseau_y - rayon < 0 or oiseau_y + rayon > HAUTEUR:
        return True
    for t in tuyaux:
        if (oiseau_x + rayon > t["x"] and oiseau_x - rayon < t["x"] + largeur_tuyau):
            if oiseau_y - rayon < t["haut"] or oiseau_y + rayon > t["bas"]:
                return True
    return False

# ---------- Mode Auto RL fonctionnel ----------
def bot_action_rl():
    """
    Mode Auto RL simulé :
    - regarde le prochain tuyau
    - calcule la différence verticale entre l'oiseau et le centre du trou
    - saute si l'oiseau est trop bas
    """
    if not tuyaux:
        return False
    prochain = tuyaux[0]
    if prochain["x"] + largeur_tuyau < oiseau_x and len(tuyaux) > 1:
        prochain = tuyaux[1]

    centre_trou = (prochain["haut"] + prochain["bas"]) / 2
    diff = oiseau_y - centre_trou

    tolerance = 20  # ajustable
    return diff > tolerance

# ---------- UI / Reset ----------
def draw_button(txt, x, y, w, h, color, hover_color):
    rect = pygame.Rect(x, y, w, h)
    if rect.collidepoint(pygame.mouse.get_pos()):
        pygame.draw.rect(ECRAN, hover_color, rect)
    else:
        pygame.draw.rect(ECRAN, color, rect)
    sur = font.render(txt, True, BLANC)
    ECRAN.blit(sur, (x + (w - sur.get_width()) // 2, y + (h - sur.get_height()) // 2))
    return rect

def reset_jeu():
    global oiseau_y, vitesse, tuyaux, score, en_jeu
    oiseau_y = HAUTEUR // 2
    vitesse = 0.0
    tuyaux = [creer_tuyau(), creer_tuyau()]
    tuyaux[1]["x"] = tuyaux[0]["x"] + 220
    score = 0
    en_jeu = True

MENU_BTNS = {
    "manu": pygame.Rect(120, 200, 160, 50),
    "auto": pygame.Rect(120, 300, 160, 50),
}
GAMEOVER_BTNS = {
    "replay": pygame.Rect(120, 320, 160, 50),
    "menu": pygame.Rect(120, 400, 160, 50),
}

# ---------- Boucle principale ----------
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and en_jeu and mode=="manu":
                vitesse = jump_velocity
            if event.key == pygame.K_r and not en_jeu and mode is not None:
                reset_jeu()
        if event.type == pygame.MOUSEBUTTONDOWN and event.button ==1:
            pos = event.pos
            # menu
            if mode is None:
                if MENU_BTNS["manu"].collidepoint(pos):
                    mode="manu"; reset_jeu()
                elif MENU_BTNS["auto"].collidepoint(pos):
                    mode="auto"; reset_jeu()
            else:
                if not en_jeu:
                    if GAMEOVER_BTNS["replay"].collidepoint(pos):
                        reset_jeu()
                    elif GAMEOVER_BTNS["menu"].collidepoint(pos):
                        mode=None
                        en_jeu=False

    # ----- update jeu -----
    if en_jeu:
        # Auto RL
        if mode=="auto" and bot_action_rl():
            vitesse = jump_velocity

        vitesse += gravite
        oiseau_y += vitesse

        for t in tuyaux:
            t["x"] -= vitesse_tuyau

        if tuyaux[-1]["x"] < LARGEUR-200:
            new = creer_tuyau()
            new["x"] = tuyaux[-1]["x"] + 220
            tuyaux.append(new)

        if tuyaux and tuyaux[0]["x"] + largeur_tuyau < 0:
            tuyaux.pop(0)
            score +=1

        if verifier_collision():
            en_jeu=False
            if mode=="manu":
                if score>high_score_manu: high_score_manu=score
            elif mode=="auto":
                if score>high_score_auto: high_score_auto=score

    # ----- rendu -----
    ECRAN.fill(BLEU_CIEL)

    if mode is None:
        titre = font.render("Choisis ton mode :", True, NOIR)
        ECRAN.blit(titre, (LARGEUR//2 - titre.get_width()//2, 120))
        draw_button("Mode Manuel", *MENU_BTNS["manu"].topleft, MENU_BTNS["manu"].width, MENU_BTNS["manu"].height, ROUGE, (255,50,50))
        draw_button("Auto RL", *MENU_BTNS["auto"].topleft, MENU_BTNS["auto"].width, MENU_BTNS["auto"].height, GRIS, (150,150,150))
        pygame.display.flip()
        clock.tick(FPS)
        continue

    afficher_tuyaux()

    # --- Visualisation RL ---
    if mode=="auto" and tuyaux:
        prochain = tuyaux[0]
        if prochain["x"] + largeur_tuyau < oiseau_x and len(tuyaux) > 1:
            prochain = tuyaux[1]
        centre_trou = (prochain["haut"] + prochain["bas"]) / 2
        # ligne rouge = centre du trou
        pygame.draw.line(ECRAN, ROUGE, (prochain["x"], centre_trou), (prochain["x"] + largeur_tuyau, centre_trou), 2)
        # ligne verticale = distance oiseau->centre trou
        pygame.draw.line(ECRAN, NOIR, (oiseau_x, oiseau_y), (oiseau_x, centre_trou), 1)

    # couleur de l'oiseau selon action
    if mode=="auto" and bot_action_rl():
        couleur_oiseau = VERT
    else:
        couleur_oiseau = JAUNE
    pygame.draw.circle(ECRAN, couleur_oiseau, (oiseau_x,int(oiseau_y)), rayon)

    # score et mode
    txt_score = font.render(f"Score : {score}", True, BLANC)
    ECRAN.blit(txt_score, (10,10))
    mode_label = {"manu":"MANUEL", "auto":"AUTO RL"}[mode]
    ECRAN.blit(font.render(f"Mode : {mode_label}", True, NOIR), (LARGEUR-200,10))

    # écran Game Over
    if not en_jeu:
        title = font.render("GAME OVER", True, ROUGE)
        ECRAN.blit(title, (LARGEUR//2 - title.get_width()//2,160))
        sc = font.render(f"Score : {score}", True, NOIR)
        ECRAN.blit(sc, (LARGEUR//2 - sc.get_width()//2, 200))
        if mode=="manu":
            hs = font.render(f"Best Manu : {high_score_manu}", True, NOIR)
        else:
            hs = font.render(f"Best Auto : {high_score_auto}", True, NOIR)
        ECRAN.blit(hs, (LARGEUR//2 - hs.get_width()//2, 235))
        draw_button("Rejouer (R)", *GAMEOVER_BTNS["replay"].topleft, GAMEOVER_BTNS["replay"].width, GAMEOVER_BTNS["replay"].height, ROUGE, (255,50,50))
        draw_button("Menu", *GAMEOVER_BTNS["menu"].topleft, GAMEOVER_BTNS["menu"].width, GAMEOVER_BTNS["menu"].height, GRIS, (150,150,150))

    pygame.display.flip()
    clock.tick(FPS)
