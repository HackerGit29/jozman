# vrp_solver.py
# ------------------------
# Module principal pour la gestion du VRP :
# - Génération de villes + matrice de distances
# - Calcul du coût total d'une solution
# - Fonctions utilitaires pour Tabu Search (initialisation, validation, échange de clients)

import numpy as np
import random
import math
import copy

# 1) Générer les villes (coordonnées + matrice de distances)
def createcity(nbr, tempsmax, seed):
    """
    Génère 'nbr' villes (dont l'indice 0 est le dépôt) et retourne :
      - city : liste de tuples (x, y) pour chaque ville
      - tempo: matrice (nbr × nbr) des distances entières (euclidiennes arrondies)
    Args :
        nbr     : nombre total de villes (incluant le dépôt)
        tempsmax: valeur maximale pour les coordonnées (0..tempsmax)
        seed    : graine pour le générateur aléatoire, assure la reproductibilité
    Retour :
        city  : [(x0, y0), (x1, y1), ..., (x_{nbr-1}, y_{nbr-1})]
        tempo : np.ndarray de taille (nbr, nbr), tempo[i][j] = distance entre i et j
    """
    random.seed(seed)
    city = [(random.randint(0, tempsmax), random.randint(0, tempsmax)) for _ in range(nbr)]
    tempo = np.zeros((nbr, nbr), dtype=int)
    for i in range(nbr):
        for j in range(nbr):
            if i != j:
                dx = city[i][0] - city[j][0]
                dy = city[i][1] - city[j][1]
                # Distance euclidienne arrondie à l'entier le plus proche
                tempo[i][j] = int(round(math.hypot(dx, dy)))
    return city, tempo


# 2) Calculer le coût total (somme des distances) d'une solution VRP
def calculer_cout_total(solution, tempo):
    """
    Calcule la somme des distances pour une solution donnée.
    Args :
        solution : liste de tournées, chaque tournée est une liste d'indices de villes,
                   e.g. [[0, 3, 5, 0], [0, 2, 4, 1, 0], ...]
        tempo    : matrice des distances (produite par createcity)
    Retour :
        cout     : somme des distances parcourues pour toutes les tournées
    """
    cout = 0
    for tour in solution:
        if len(tour) >= 2:
            # Distance du dépôt au premier client
            cout += tempo[0][tour[1]]
            # Distance entre clients successifs
            for i in range(1, len(tour) - 1):
                cout += tempo[tour[i]][tour[i + 1]]
            # Retour du dernier client au dépôt
            cout += tempo[tour[-1]][0]
    return cout


# 3) Fonctions utilitaires pour Tabu Search

def est_tournee_valide(tournee):
    """
    Vérifie qu'une tournée commence et se termine bien au dépôt (indice 0).
    Args :
        tournee : liste d'indices de villes (ex. [0, 5, 2, 0])
    Retour :
        True si tournee[0] == 0 et tournee[-1] == 0, False sinon.
    """
    return len(tournee) >= 2 and tournee[0] == 0 and tournee[-1] == 0

def initialiser_solution(k, nbr):
    """
    Crée une solution initiale faisable pour Tabu Search :
    - Répartition cyclique des clients (1..nbr-1) dans k tournées
    - Ajout du dépôt (0) au début et à la fin de chaque tournée
    - Ajustement pour éviter les tournées vides (juste [0,0])
    Args :
        k   : nombre de véhicules
        nbr : nombre total de villes (incluant le dépôt)
    Retour :
        tournees : liste de k tournées faisables, e.g. [[0,3,5,0], [0,1,2,4,0], ...]
    """
    clients = list(range(1, nbr))
    random.shuffle(clients)
    tournees = [[] for _ in range(k)]
    # Répartition cyclique
    for idx, client in enumerate(clients):
        tournees[idx % k].append(client)
    # Ajout du dépôt au début et à la fin
    for i in range(k):
        tournees[i] = [0] + tournees[i] + [0]
    # Si une tournée ne contient aucun client (seulement [0,0]),
    # on déplace un client depuis une tournée plus remplie
    while any(len(t) == 2 for t in tournees):
        for i in range(k):
            if len(tournees[i]) == 2:
                for j in range(k):
                    if len(tournees[j]) > 2:
                        # Déplacer le second élément (indice 1) de t[j] vers t[i]
                        client_a_deplacer = tournees[j].pop(1)
                        tournees[i].insert(1, client_a_deplacer)
                        break
    return tournees

def echanger_clients(route1, route2):
    """
    Échange deux clients aléatoires (non dépôt) entre deux tournées.
    Args :
        route1 : première tournée (liste d'indices, ex. [0,5,3,0])
        route2 : deuxième tournée
    Effet :
        Swap des éléments aux positions aléatoires (entre 1 et len-2).
    """
    if len(route1) > 2 and len(route2) > 2:
        idx1 = random.randint(1, len(route1) - 2)
        idx2 = random.randint(1, len(route2) - 2)
        route1[idx1], route2[idx2] = route2[idx2], route1[idx1]


# 4) Exemple d'une Tabu Search basique (sans paramètres avancés)
def recherche_tabou_vrp(tempo, k, nbr, time_window):
    """
    Tabu Search de base pour le VRP (sans gestion des fenêtres de temps à l'intérieur).
    Args :
        tempo       : matrice (nbr×nbr) des distances entières
        k           : nombre de véhicules
        nbr         : nombre total de villes (incluant dépôt)
        time_window : contrainte de temps maximale (global, en minutes) – ici à vérifier a posteriori
    Retour :
        meilleure_solution : liste de k tournées (validées par est_tournee_valide)
        meilleur_cout       : distance totale de la meilleure solution
    """
    # Paramètres par défaut pour cette version de base
    taille_tabou = max(30, 10 * len(str(nbr)) - 1 + k)
    nb_iterations = min(1000, 50 * nbr)

    # Initialisation
    meilleure_solution = initialiser_solution(k, nbr)
    meilleur_cout = calculer_cout_total(meilleure_solution, tempo)
    solution_actuelle = copy.deepcopy(meilleure_solution)
    liste_tabou = []

    for _ in range(nb_iterations):
        voisinage = []
        # Générer voisins en échangeant deux clients entre deux tournées
        for i in range(k):
            for j in range(i + 1, k):
                voisin = copy.deepcopy(solution_actuelle)
                echanger_clients(voisin[i], voisin[j])
                if all(est_tournee_valide(t) for t in voisin) and voisin not in liste_tabou:
                    voisinage.append(voisin)

        # Sélection du meilleur voisin parmi le voisinage
        meilleur_voisin = None
        cout_meilleur_voisin = float('inf')
        for voisin in voisinage:
            cout_voisin = calculer_cout_total(voisin, tempo)
            if cout_voisin < cout_meilleur_voisin:
                meilleur_voisin = voisin
                cout_meilleur_voisin = cout_voisin

        if meilleur_voisin is not None:
            solution_actuelle = meilleur_voisin
            if cout_meilleur_voisin < meilleur_cout:
                meilleure_solution = solution_actuelle
                meilleur_cout = cout_meilleur_voisin

        # Mettre à jour la liste tabou
        liste_tabou.append(copy.deepcopy(solution_actuelle))
        if len(liste_tabou) > taille_tabou:
            liste_tabou.pop(0)

    return meilleure_solution, meilleur_cout


# 5) Exemple d'utilisation autonome (test rapide)
if __name__ == "__main__":
    # Exécution d'un exemple en mode autonome
    nbr = 10        # Nombre de villes (incluant dépôt)
    k = 3           # Nombre de véhicules
    time_window = 200  # Fenêtre de temps globale

    # Génération
    city, tempo = createcity(nbr, tempsmax=100, seed=42)

    # Initialisation d'une solution
    sol_init = initialiser_solution(k, nbr)
    print("Solution initiale :", sol_init)
    print("Coût initial      :", calculer_cout_total(sol_init, tempo))

    # Exécution de Tabu Search
    best_sol, best_cost = recherche_tabou_vrp(tempo, k, nbr, time_window)
    print("\nMeilleure solution trouvée par Tabu Search :")
    for idx, route in enumerate(best_sol):
        print(f"  Camion {idx+1} :", route)
    print("Coût total (distance) :", best_cost)
