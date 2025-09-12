import pygame, random, sys

# Initialisation
pygame.init()
LARGEUR, HAUTEUR = 400, 600
ECRAN = pygame.display.set_mode((LARGEUR, HAUTEUR))
pygame.display.set_caption("Flappy Bird - Manuel / Auto Rule-Based")

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

# Joueur
oiseau_x, oiseau_y = 60, HAUTEUR//2
rayon = 15
gravite = 0.5
vitesse = 0

# Tuyaux
tuyaux = []
largeur_tuyau = 60
ecart = 150
vitesse_tuyau = 3

# Score
score = 0
font = pygame.font.SysFont("Arial", 24, bold=True)

# Mode de jeu
mode_auto = None   # None = menu, True = auto, False = manuel

def creer_tuyau():
    hauteur = random.randint(100, 400)
    return {"x": LARGEUR, "haut": hauteur, "bas": hauteur + ecart}

def afficher_tuyaux():
    for t in tuyaux:
        pygame.draw.rect(ECRAN, VERT, (t["x"], 0, largeur_tuyau, t["haut"]))
        pygame.draw.rect(ECRAN, VERT, (t["x"], t["bas"], largeur_tuyau, HAUTEUR))

def verifier_collision():
    if oiseau_y - rayon < 0 or oiseau_y + rayon > HAUTEUR:
        return True
    for t in tuyaux:
        if (oiseau_x + rayon > t["x"] and oiseau_x - rayon < t["x"] + largeur_tuyau):
            if oiseau_y - rayon < t["haut"] or oiseau_y + rayon > t["bas"]:
                return True
    return False

# === AUTOMATISME PAR RÈGLES FIXES ===
def bot_action():
    """
    Rule-Based amélioré :
    - Le bot vise le centre du trou
    - S'il est trop bas par rapport au centre → saute
    - S'il est trop haut → ne fait rien (descend avec la gravité)
    """
    if not tuyaux:
        return False

    # Récupère le prochain tuyau
    prochain = tuyaux[0]
    if oiseau_x > prochain["x"] + largeur_tuyau and len(tuyaux) > 1:
        prochain = tuyaux[1]

    centre_trou = (prochain["haut"] + prochain["bas"]) // 2

    # marge de tolérance (évite que l’oiseau saute trop souvent)
    tolerance = 20  

    # Si l’oiseau est en dessous du centre du trou → sauter
    if oiseau_y > centre_trou + tolerance:
        return True
    # Sinon → rien faire (laisser descendre)
    return False

def afficher_bouton(txt, x, y, w, h, couleur, couleur_hover, action=None):
    """Affiche un bouton cliquable"""
    souris = pygame.mouse.get_pos()
    clic = pygame.mouse.get_pressed()
    if x < souris[0] < x + w and y < souris[1] < y + h:
        pygame.draw.rect(ECRAN, couleur_hover, (x, y, w, h))
        if clic[0] == 1 and action is not None:
            return action
    else:
        pygame.draw.rect(ECRAN, couleur, (x, y, w, h))

    texte = font.render(txt, True, BLANC)
    ECRAN.blit(texte, (x + (w - texte.get_width()) // 2, y + (h - texte.get_height()) // 2))
    return None

def reset_jeu():
    """Réinitialise les variables du jeu"""
    global oiseau_y, vitesse, tuyaux, score, en_jeu
    oiseau_y = HAUTEUR // 2
    vitesse = 0
    tuyaux = [creer_tuyau()]
    score = 0
    en_jeu = True

# Boucle principale
en_jeu = False
tuyaux.append(creer_tuyau())

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if not en_jeu and mode_auto is not None and event.key == pygame.K_r:
                reset_jeu()
            if event.key == pygame.K_SPACE and en_jeu and mode_auto is False:
                vitesse = -8

    # --- MENU ---
    if mode_auto is None:
        ECRAN.fill(BLEU_CIEL)
        titre = font.render("Choisis ton mode :", True, NOIR)
        ECRAN.blit(titre, (LARGEUR//2 - titre.get_width()//2, 150))

        choix1 = afficher_bouton("Mode Manuel", 120, 250, 160, 50, ROUGE, (255, 50, 50), False)
        choix2 = afficher_bouton("Mode Auto R-B", 120, 350, 160, 50, VERT, (0, 255, 0), True)

        if choix1 is not None:
            mode_auto = choix1
            reset_jeu()
        if choix2 is not None:
            mode_auto = choix2
            reset_jeu()

        pygame.display.flip()
        clock.tick(FPS)
        continue

    # --- JEU ---
    if en_jeu:
        if mode_auto and bot_action():
            vitesse = -8

        vitesse += gravite
        oiseau_y += vitesse

        for t in tuyaux:
            t["x"] -= vitesse_tuyau
        if tuyaux[-1]["x"] < LARGEUR - 200:
            tuyaux.append(creer_tuyau())
        if tuyaux[0]["x"] + largeur_tuyau < 0:
            tuyaux.pop(0)
            score += 1

        if verifier_collision():
            en_jeu = False

    # --- AFFICHAGE ---
    ECRAN.fill(BLEU_CIEL)
    afficher_tuyaux()
    pygame.draw.circle(ECRAN, JAUNE, (oiseau_x, int(oiseau_y)), rayon)

    texte = font.render(f"Score : {score}", True, BLANC)
    ECRAN.blit(texte, (10, 10))

    mode_txt = "AUTO R-B" if mode_auto else "MANUEL"
    texte2 = font.render(f"Mode : {mode_txt}", True, NOIR)
    ECRAN.blit(texte2, (LARGEUR-200, 10))

    if not en_jeu:
        msg = font.render("GAME OVER", True, ROUGE)
        ECRAN.blit(msg, (LARGEUR//2 - msg.get_width()//2, 220))

        # Boutons Game Over
        action1 = afficher_bouton("Rejouer", 120, 300, 160, 50, ROUGE, (255, 50, 50), "rejouer")
        action2 = afficher_bouton("Menu", 120, 400, 160, 50, GRIS, (150, 150, 150), "menu")

        if action1 == "rejouer":
            reset_jeu()
        if action2 == "menu":
            mode_auto = None  # retour menu

    pygame.display.flip()
    clock.tick(FPS)

