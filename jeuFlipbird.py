import pygame, random, sys

# Initialisation
pygame.init()
LARGEUR, HAUTEUR = 400, 600
ECRAN = pygame.display.set_mode((LARGEUR, HAUTEUR))
pygame.display.set_caption("Flappy Bird en Python")

# Couleurs
BLANC = (255, 255, 255)
VERT = (0, 200, 0)
BLEU_CIEL = (135, 206, 250)

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

def creer_tuyau():
    """Crée un tuyau avec un trou aléatoire"""
    hauteur = random.randint(100, 400)
    return {"x": LARGEUR, "haut": hauteur, "bas": hauteur + ecart}

def afficher_tuyaux():
    """Affiche tous les tuyaux"""
    for t in tuyaux:
        pygame.draw.rect(ECRAN, VERT, (t["x"], 0, largeur_tuyau, t["haut"]))
        pygame.draw.rect(ECRAN, VERT, (t["x"], t["bas"], largeur_tuyau, HAUTEUR))

def verifier_collision():
    """Vérifie si l’oiseau touche un tuyau ou sort de l’écran"""
    global en_jeu
    if oiseau_y - rayon < 0 or oiseau_y + rayon > HAUTEUR:
        return True
    for t in tuyaux:
        if (oiseau_x + rayon > t["x"] and oiseau_x - rayon < t["x"] + largeur_tuyau):
            if oiseau_y - rayon < t["haut"] or oiseau_y + rayon > t["bas"]:
                return True
    return False




# Boucle principale
en_jeu = True
tuyaux.append(creer_tuyau())

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and en_jeu:
                vitesse = -8
            if event.key == pygame.K_r and not en_jeu:
                # Réinitialiser le jeu
                oiseau_y = HAUTEUR//2
                vitesse = 0
                tuyaux = [creer_tuyau()]
                score = 0
                en_jeu = True

    if en_jeu:
        # Mise à jour physique
        vitesse += gravite
        oiseau_y += vitesse

        # Déplacement tuyaux
        for t in tuyaux:
            t["x"] -= vitesse_tuyau
        if tuyaux[-1]["x"] < LARGEUR - 200:
            tuyaux.append(creer_tuyau())
        if tuyaux[0]["x"] + largeur_tuyau < 0:
            tuyaux.pop(0)
            score += 1

        # Collision
        if verifier_collision():
            en_jeu = False

    # Affichage
    ECRAN.fill(BLEU_CIEL)
    afficher_tuyaux()
    pygame.draw.circle(ECRAN, (255, 255, 0), (oiseau_x, int(oiseau_y)), rayon)

    texte = font.render(f"Score : {score}", True, BLANC)
    ECRAN.blit(texte, (10, 10))

    if not en_jeu:
        msg = font.render("GAME OVER - Appuie R pour rejouer", True, (200, 0, 0))
        ECRAN.blit(msg, (20, HAUTEUR//2))

    pygame.display.flip()
    clock.tick(FPS)
