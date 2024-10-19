import pygame
import sys
import random

# Initialisation de Pygame
pygame.init()

# Constantes
TAILLE_CASE = 80
LARGEUR = HAUTEUR = 8 * TAILLE_CASE
FENETRE = pygame.display.set_mode((LARGEUR, HAUTEUR))
pygame.display.set_caption("Jeu d'Échecs")

# Couleurs
BLANC = (255, 255, 255)
NOIR = (0, 0, 0)
GRIS = (128, 128, 128)
BLEU = (0, 0, 255)
ROUGE = (255, 0, 0)

# Chargement des images des pièces
PIECES = {}
for couleur in ['b', 'n']:
    for piece in ['R', 'D', 'T', 'F', 'C', 'P']:
        PIECES[f"{couleur}{piece}"] = pygame.transform.scale(
            pygame.image.load(f"pieces/{couleur}{piece}.png"),
            (TAILLE_CASE, TAILLE_CASE)
        )

class Piece:
    def __init__(self, couleur, symbole):
        self.couleur = couleur
        self.symbole = symbole
        self.a_bouge = False

    def mouvements_valides(self, x, y, echiquier):
        return []

class Roi(Piece):
    def __init__(self, couleur):
        super().__init__(couleur, 'R')

    def mouvements_valides(self, x, y, echiquier, verifier_echec=True):
        mouvements = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < 8 and 0 <= ny < 8:
                    if echiquier.plateau[nx][ny] is None or echiquier.plateau[nx][ny].couleur != self.couleur:
                        mouvements.append((nx, ny))
        
        # Roque
        if not self.a_bouge and verifier_echec and not echiquier.est_en_echec(self.couleur):
            # Petit roque
            if (echiquier.plateau[x][7] is not None and 
                isinstance(echiquier.plateau[x][7], Tour) and 
                not echiquier.plateau[x][7].a_bouge and
                all(echiquier.plateau[x][i] is None for i in range(5, 7))):
                if all(not echiquier.case_est_attaquee(x, i, self.couleur) for i in range(4, 7)):
                    mouvements.append((x, 6))
            # Grand roque
            if (echiquier.plateau[x][0] is not None and 
                isinstance(echiquier.plateau[x][0], Tour) and 
                not echiquier.plateau[x][0].a_bouge and
                all(echiquier.plateau[x][i] is None for i in range(1, 4))):
                if all(not echiquier.case_est_attaquee(x, i, self.couleur) for i in range(2, 5)):
                    mouvements.append((x, 2))
        
        return mouvements

class Dame(Piece):
    def __init__(self, couleur):
        super().__init__(couleur, 'D')

    def mouvements_valides(self, x, y, echiquier):
        mouvements = []
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            while 0 <= nx < 8 and 0 <= ny < 8:
                if echiquier.plateau[nx][ny] is None:
                    mouvements.append((nx, ny))
                elif echiquier.plateau[nx][ny].couleur != self.couleur:
                    mouvements.append((nx, ny))
                    break
                else:
                    break
                nx, ny = nx + dx, ny + dy
        return mouvements

class Tour(Piece):
    def __init__(self, couleur):
        super().__init__(couleur, 'T')

    def mouvements_valides(self, x, y, echiquier):
        mouvements = []
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            while 0 <= nx < 8 and 0 <= ny < 8:
                if echiquier.plateau[nx][ny] is None:
                    mouvements.append((nx, ny))
                elif echiquier.plateau[nx][ny].couleur != self.couleur:
                    mouvements.append((nx, ny))
                    break
                else:
                    break
                nx, ny = nx + dx, ny + dy
        return mouvements

class Fou(Piece):
    def __init__(self, couleur):
        super().__init__(couleur, 'F')

    def mouvements_valides(self, x, y, echiquier):
        mouvements = []
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            while 0 <= nx < 8 and 0 <= ny < 8:
                if echiquier.plateau[nx][ny] is None:
                    mouvements.append((nx, ny))
                elif echiquier.plateau[nx][ny].couleur != self.couleur:
                    mouvements.append((nx, ny))
                    break
                else:
                    break
                nx, ny = nx + dx, ny + dy
        return mouvements

class Cavalier(Piece):
    def __init__(self, couleur):
        super().__init__(couleur, 'C')

    def mouvements_valides(self, x, y, echiquier):
        mouvements = []
        directions = [(2, 1), (1, 2), (-1, 2), (-2, 1), (-2, -1), (-1, -2), (1, -2), (2, -1)]
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < 8 and 0 <= ny < 8:
                if echiquier.plateau[nx][ny] is None or echiquier.plateau[nx][ny].couleur != self.couleur:
                    mouvements.append((nx, ny))
        return mouvements

class Pion(Piece):
    def __init__(self, couleur):
        super().__init__(couleur, 'P')
        self.en_passant = False

    def mouvements_valides(self, x, y, echiquier):
        mouvements = []
        direction = -1 if self.couleur == 'blanc' else 1
        nx, ny = x + direction, y
        if 0 <= nx < 8 and echiquier.plateau[nx][ny] is None:
            mouvements.append((nx, ny))
            if (self.couleur == 'blanc' and x == 6) or (self.couleur == 'noir' and x == 1):
                nx = x + 2 * direction
                if 0 <= nx < 8 and echiquier.plateau[nx][ny] is None:
                    mouvements.append((nx, ny))
        for dy in [-1, 1]:
            nx, ny = x + direction, y + dy
            if 0 <= nx < 8 and 0 <= ny < 8:
                if echiquier.plateau[nx][ny] is not None and echiquier.plateau[nx][ny].couleur != self.couleur:
                    mouvements.append((nx, ny))
                elif echiquier.plateau[nx][ny] is None:
                    # Prise en passant
                    piece_adjacente = echiquier.plateau[x][ny]
                    if isinstance(piece_adjacente, Pion) and piece_adjacente.en_passant:
                        mouvements.append((nx, ny))
        return mouvements

class Echiquier:
    def __init__(self):
        self.plateau = [[None for _ in range(8)] for _ in range(8)]
        self.initialiser()
        self.dernier_mouvement = None

    def initialiser(self):
        ordre = [Tour, Cavalier, Fou, Dame, Roi, Fou, Cavalier, Tour]
        for i in range(8):
            self.plateau[0][i] = ordre[i]('noir')
            self.plateau[1][i] = Pion('noir')
            self.plateau[6][i] = Pion('blanc')
            self.plateau[7][i] = ordre[i]('blanc')

    def dessiner(self, fenetre):
        for i in range(8):
            for j in range(8):
                couleur = BLANC if (i + j) % 2 == 0 else GRIS
                pygame.draw.rect(fenetre, couleur, (j * TAILLE_CASE, i * TAILLE_CASE, TAILLE_CASE, TAILLE_CASE))
                piece = self.plateau[i][j]
                if piece:
                    fenetre.blit(PIECES[f"{'b' if piece.couleur == 'blanc' else 'n'}{piece.symbole}"], 
                                 (j * TAILLE_CASE, i * TAILLE_CASE))

    def deplacer(self, depart, arrivee):
        x1, y1 = depart
        x2, y2 = arrivee
        piece = self.plateau[x1][y1]
        if piece and (x2, y2) in piece.mouvements_valides(x1, y1, self):
            # Gestion du roque
            if isinstance(piece, Roi) and abs(y2 - y1) == 2:
                # Petit roque
                if y2 > y1:
                    self.plateau[x1][6] = piece  # Déplacer le roi
                    self.plateau[x1][y1] = None
                    self.plateau[x1][5] = self.plateau[x1][7]  # Déplacer la tour
                    self.plateau[x1][7] = None
                # Grand roque
                else:
                    self.plateau[x1][2] = piece  # Déplacer le roi
                    self.plateau[x1][y1] = None
                    self.plateau[x1][3] = self.plateau[x1][0]  # Déplacer la tour
                    self.plateau[x1][0] = None
                piece.a_bouge = True
                self.plateau[x1][3].a_bouge = True  # Marquer la tour comme ayant bougé
                return True

            # Déplacement normal
            self.plateau[x2][y2] = piece
            self.plateau[x1][y1] = None
            piece.a_bouge = True

            # Gestion de la promotion du pion
            if isinstance(piece, Pion) and (x2 == 0 or x2 == 7):
                # Utilise la nouvelle méthode pour demander le choix de la promotion
                choix = self.demander_choix_promotion(piece.couleur)
                if choix == "Dame":
                    self.plateau[x2][y2] = Dame(piece.couleur)
                elif choix == "Tour":
                    self.plateau[x2][y2] = Tour(piece.couleur)
                elif choix == "Fou":
                    self.plateau[x2][y2] = Fou(piece.couleur)
                elif choix == "Cavalier":
                    self.plateau[x2][y2] = Cavalier(piece.couleur)
            
            # Mise à jour de l'état "en passant" pour les pions
            if isinstance(piece, Pion) and abs(x2 - x1) == 2:
                piece.en_passant = True
            else:
                for row in self.plateau:
                    for p in row:
                        if isinstance(p, Pion):
                            p.en_passant = False
            if isinstance(piece, Pion) and y1 != y2:
                # Cela signifie qu'il s'agit d'une prise en passant
                self.plateau[x1][y2] = None  # Supprime le pion capturé

            self.dernier_mouvement = (depart, arrivee)
            return True
        return False

    def demander_choix_promotion(self, couleur):
        # Créez un fond pour le menu de promotion
        fenetre_promotion = pygame.Surface((TAILLE_CASE * 4, TAILLE_CASE))
        fenetre_promotion.fill(GRIS)

        # Chargez les images des pièces pour la promotion
        choix_pieces = ['D', 'T', 'F', 'C']  # Dame, Tour, Fou, Cavalier
        positions = []

        for i, piece in enumerate(choix_pieces):
            image = PIECES[f"{'b' if couleur == 'blanc' else 'n'}{piece}"]
            fenetre_promotion.blit(image, (i * TAILLE_CASE, 0))
            positions.append(pygame.Rect(i * TAILLE_CASE, 0, TAILLE_CASE, TAILLE_CASE))

        # Affiche le menu au centre de l'écran
        FENETRE.blit(fenetre_promotion, (LARGEUR // 2 - TAILLE_CASE * 2, HAUTEUR // 2 - TAILLE_CASE // 2))
        pygame.display.flip()

        # Attendre que l'utilisateur clique sur une pièce pour la promotion
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # Obtenez la position du clic
                    mouse_pos = event.pos
                    for i, rect in enumerate(positions):
                        # Si le clic est sur l'une des icônes
                        if rect.collidepoint(mouse_pos[0] - LARGEUR // 2 + TAILLE_CASE * 2, mouse_pos[1] - HAUTEUR // 2 + TAILLE_CASE // 2):
                            # Retourne le choix de la promotion basé sur l'icône cliquée
                            return ['Dame', 'Tour', 'Fou', 'Cavalier'][i]

    def obtenir_tous_mouvements(self, couleur):
        mouvements = []
        for x in range(8):
            for y in range(8):
                piece = self.plateau[x][y]
                if piece and piece.couleur == couleur:
                    for nx, ny in piece.mouvements_valides(x, y, self):
                        mouvements.append(((x, y), (nx, ny)))
        return mouvements

    def est_en_echec(self, couleur):
        roi_pos = None
        for i in range(8):
            for j in range(8):
                piece = self.plateau[i][j]
                if isinstance(piece, Roi) and piece.couleur == couleur:
                    roi_pos = (i, j)
                    break
            if roi_pos:
                break
        
        return self.case_est_attaquee(*roi_pos, couleur)

    def case_est_attaquee(self, x, y, couleur_defendeur):
        for i in range(8):
            for j in range(8):
                piece = self.plateau[i][j]
                if piece and piece.couleur != couleur_defendeur:
                    if isinstance(piece, Roi):
                        mouvements = piece.mouvements_valides(i, j, self, verifier_echec=False)
                    else:
                        mouvements = piece.mouvements_valides(i, j, self)
                    if (x, y) in mouvements:
                        return True
        return False

    def est_echec_et_mat(self, couleur):
        if not self.est_en_echec(couleur):
            return False
        
        for depart, arrivee in self.obtenir_tous_mouvements(couleur):
            echiquier_temp = self.copier()
            if echiquier_temp.deplacer(depart, arrivee):
                if not echiquier_temp.est_en_echec(couleur):
                    return False
        return True

    def copier(self):
        nouveau = Echiquier()
        nouveau.plateau = [[self.plateau[i][j] for j in range(8)] for i in range(8)]
        return nouveau

class IA:
    def __init__(self, couleur):
        self.couleur = couleur

    def choisir_mouvement(self, echiquier):
        mouvements = echiquier.obtenir_tous_mouvements(self.couleur)
        mouvements_valides = []
        for depart, arrivee in mouvements:
            echiquier_temp = echiquier.copier()
            if echiquier_temp.deplacer(depart, arrivee):
                if not echiquier_temp.est_en_echec(self.couleur):
                    mouvements_valides.append((depart, arrivee))
        return random.choice(mouvements_valides) if mouvements_valides else None

def afficher_menu(fenetre):
    """Affiche le menu de sélection pour choisir le mode de jeu via un clic"""
    font = pygame.font.Font(None, 74)
    text1 = font.render("1. Joueur vs IA", True, BLANC)
    text2 = font.render("2. Joueur vs Joueur", True, BLANC)
    
    # Positions des textes
    text1_rect = text1.get_rect(center=(LARGEUR // 2, HAUTEUR // 2 - 50))
    text2_rect = text2.get_rect(center=(LARGEUR // 2, HAUTEUR // 2 + 50))
    
    # Affichage
    fenetre.fill(NOIR)
    fenetre.blit(text1, text1_rect)
    fenetre.blit(text2, text2_rect)
    
    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Vérifie si le clic a eu lieu sur l'une des options
                mouse_pos = pygame.mouse.get_pos()
                
                if text1_rect.collidepoint(mouse_pos):  # Si le clic est sur "Joueur vs IA"
                    return 'IA'
                elif text2_rect.collidepoint(mouse_pos):  # Si le clic est sur "Joueur vs Joueur"
                    return 'Joueur'



def main():
    echiquier = Echiquier()

    # Afficher le menu et sélectionner le mode de jeu
    mode_de_jeu = afficher_menu(FENETRE)

    ia = IA('noir') if mode_de_jeu == 'IA' else None
    tour = 'blanc'
    piece_selectionnee = None
    mouvements_valides = []
    partie_terminee = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and not partie_terminee:
                x, y = event.pos[1] // TAILLE_CASE, event.pos[0] // TAILLE_CASE
                if piece_selectionnee:
                    if (x, y) in mouvements_valides:
                        if echiquier.deplacer(piece_selectionnee, (x, y)):
                            piece_selectionnee = None
                            mouvements_valides = []
                            tour = 'noir' if tour == 'blanc' else 'blanc'
                    else:
                        piece_selectionnee = None
                        mouvements_valides = []
                else:
                    piece = echiquier.plateau[x][y]
                    if piece and piece.couleur == tour:
                        piece_selectionnee = (x, y)
                        mouvements_valides = piece.mouvements_valides(x, y, echiquier)

                        # Vérifier si le roi est en échec
                        if echiquier.est_en_echec(tour):
                            # Créer une copie de l'échiquier
                            echiquier_temp = echiquier.copier()
                            mouvements_valides = [
                                m for m in mouvements_valides
                                if echiquier_temp.deplacer((x, y), m) and not echiquier_temp.est_en_echec(tour)
                            ]

                            # Si aucun mouvement valide n'est trouvé, réinitialiser
                            if not mouvements_valides:
                                piece_selectionnee = None  # Réinitialiser si aucun mouvement valide
                                continue  # Passer à l'itération suivante
        # Si c'est le tour de l'IA et que le mode de jeu est "Joueur vs IA"
        if tour == 'noir' and mode_de_jeu == 'IA' and not partie_terminee:
            mouvement = ia.choisir_mouvement(echiquier)
            if mouvement:
                echiquier.deplacer(*mouvement)
                tour = 'blanc'

        FENETRE.fill(NOIR)
        echiquier.dessiner(FENETRE)

        if piece_selectionnee:
            pygame.draw.rect(FENETRE, BLEU, 
                            (piece_selectionnee[1] * TAILLE_CASE, piece_selectionnee[0] * TAILLE_CASE, 
                            TAILLE_CASE, TAILLE_CASE), 3)
            for x, y in mouvements_valides:
                pygame.draw.circle(FENETRE, BLEU, 
                                (y * TAILLE_CASE + TAILLE_CASE // 2, x * TAILLE_CASE + TAILLE_CASE // 2), 10)

        # Vérifier si le roi blanc est en échec
        if echiquier.est_en_echec('blanc'):
            roi_pos = next((i, j) for i, row in enumerate(echiquier.plateau) for j, piece in enumerate(row) 
                        if isinstance(piece, Roi) and piece.couleur == 'blanc')
            pygame.draw.rect(FENETRE, ROUGE, 
                            (roi_pos[1] * TAILLE_CASE, roi_pos[0] * TAILLE_CASE, TAILLE_CASE, TAILLE_CASE), 3)

        # Vérifier si c'est échec et mat
        if echiquier.est_echec_et_mat('blanc'):
            partie_terminee = True
            font = pygame.font.Font(None, 74)
            text = font.render('Échec et mat !', True, ROUGE)
            FENETRE.blit(text, (LARGEUR // 2 - text.get_width() // 2, HAUTEUR // 2 - text.get_height() // 2))

        # Vérifier si le roi noir est en échec
        if echiquier.est_en_echec('noir'):
            roi_pos = next((i, j) for i, row in enumerate(echiquier.plateau) for j, piece in enumerate(row) 
                        if isinstance(piece, Roi) and piece.couleur == 'noir')
            pygame.draw.rect(FENETRE, ROUGE, 
                            (roi_pos[1] * TAILLE_CASE, roi_pos[0] * TAILLE_CASE, TAILLE_CASE, TAILLE_CASE), 3)

        # Vérifier si c'est échec et mat
        if echiquier.est_echec_et_mat('noir'):
            partie_terminee = True
            font = pygame.font.Font(None, 74)
            text = font.render('Échec et mat !', True, ROUGE)
            FENETRE.blit(text, (LARGEUR // 2 - text.get_width() // 2, HAUTEUR // 2 - text.get_height() // 2))

        pygame.display.flip()



if __name__ == "__main__":
    main()