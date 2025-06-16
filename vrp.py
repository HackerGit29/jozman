import numpy as np
import random
import math
import copy
from pulp import *
from matplotlib import pyplot as plt
import time

# 1) Générer les villes (coordonnées + matrice de distances)
def createcity(nbr, tempsmax, seed):
    random.seed(seed)
    # Génère des points (x,y) pour chaque ville, dont la ville 0 = dépôt
    city = [(random.randint(0, tempsmax), random.randint(0, tempsmax)) for _ in range(nbr)]
    # Calcul de la matrice de distances entières (euclidiennes arrondies)
    tempo = np.zeros((nbr, nbr), dtype=int)
    for i in range(nbr):
        for j in range(nbr):
            if i != j:
                dx = city[i][0] - city[j][0]
                dy = city[i][1] - city[j][1]
                tempo[i][j] = int(round(math.hypot(dx, dy)))
    return city, tempo

# 2) Calculer le coût total (temps) d'une solution (liste de tournées)
def calculer_cout_total(solution, tempo):
    cout = 0
    for route in solution:
        if route:
            # Distance du dépôt (0) au premier client
            cout += tempo[0][route[0]]
            # Distances entre clients successifs
            for i in range(len(route) - 1):
                cout += tempo[route[i]][route[i + 1]]
            # Retour au dépôt
            cout += tempo[route[-1]][0]
    return cout

# 3) Échange de deux clients entre deux tournées (pour Tabu Search)
def echanger_clients(route1, route2):
    if len(route1) > 2 and len(route2) > 2:
        idx1 = random.randint(1, len(route1) - 2)
        idx2 = random.randint(1, len(route2) - 2)
        route1[idx1], route2[idx2] = route2[idx2], route1[idx1]

# 4) Vérifier qu'une tournée est valide (départ et retour au dépôt)
def est_tournee_valide(tournee):
    return tournee[0] == 0 and tournee[-1] == 0

# 5) Initialiser une solution faisable pour Tabu Search
def initialiser_solution(k, nbr):
    clients = list(range(1, nbr))
    random.shuffle(clients)
    tournees = [[] for _ in range(k)]
    # Répartition cyclique des clients dans k tournées
    for i, client in enumerate(clients):
        tournees[i % k].append(client)
    # Ajout du dépôt au début et à la fin de chaque tournée
    for i in range(k):
        tournees[i] = [0] + tournees[i] + [0]
    # S'assurer qu'aucune tournée n'est vide (aucun client entre deux zéros)
    while any(len(t) == 2 for t in tournees):
        for i in range(k):
            if len(tournees[i]) == 2:
                # Trouver une tournée plus longue et déplacer un client
                for j in range(k):
                    if len(tournees[j]) > 2:
                        client_a_deplacer = tournees[j].pop(1)
                        tournees[i].insert(1, client_a_deplacer)
                        break
    return tournees

# 6) Tabu Search pour le VRP (sans fenêtres de temps stricte, optimise le coût)
def recherche_tabou_vrp(tempo, k, nbr, time_window):
    n = nbr
    # Taille de la liste tabou proportionnelle à n et k
    taille_tabou = max(30, 10 * len(str(n)) - 1 + k)
    nb_iterations = 10  # Nombre minimal d'itérations avant stagnation
    meilleure_solution = initialiser_solution(k, n)
    meilleur_cout = calculer_cout_total(meilleure_solution, tempo)
    solution_actuelle = copy.deepcopy(meilleure_solution)
    liste_tabou = []

    for iteration in range(nb_iterations):
        voisinage = []
        # Génération de tous les voisins possibles en échangeant 2 clients
        for i in range(k):
            for j in range(i + 1, k):
                voisin = copy.deepcopy(solution_actuelle)
                echanger_clients(voisin[i], voisin[j])
                if all(est_tournee_valide(route) for route in voisin):
                    if voisin not in liste_tabou:
                        voisinage.append(voisin)

        meilleur_voisin = None
        cout_meilleur_voisin = float('inf')
        # Sélection du meilleur voisin faisable
        for voisin in voisinage:
            cout = calculer_cout_total(voisin, tempo)
            if cout < cout_meilleur_voisin:
                meilleur_voisin = voisin
                cout_meilleur_voisin = cout

        if meilleur_voisin is not None:
            solution_actuelle = meilleur_voisin
            cout_actuel = cout_meilleur_voisin
            # Si on améliore la meilleure solution globale
            if cout_actuel < meilleur_cout:
                meilleure_solution = solution_actuelle
                meilleur_cout = cout_actuel

        liste_tabou.append(copy.deepcopy(solution_actuelle))
        if len(liste_tabou) > taille_tabou:
            liste_tabou.pop(0)

    # À la fin, retourner la meilleure solution trouvée et son coût
    return meilleure_solution, meilleur_cout

# 7) Affichage de la meilleure solution Tabu Search avec vérification de la fenêtre de temps
def best_soluce_print(L, city, tempo, k, time_window):
    meilleure_solution, meilleur_cout = L
    print("===== Meilleure solution Tabu Search =====")
    for i, tournee in enumerate(meilleure_solution):
        seq = ' -> '.join([f"Ville {a}" for a in tournee[1:-1]])
        print(f"Camion {i+1} : 0 -> {seq} -> 0")
    print(f"Coût total (distance) : {meilleur_cout}")

    # Visualisation graphique
    colors = [np.random.rand(3) for _ in range(len(meilleure_solution))]
    for t, c in zip(meilleure_solution, colors):
        for i in range(len(t) - 1):
            p1, p2 = city[t[i]], city[t[i + 1]]
            plt.plot([p1[0], p2[0]], [p1[1], p2[1]], color=c)

    for i, p in enumerate(city):
        plt.scatter(p[0], p[1], c='k')
        label = 'Dépôt' if i == 0 else f"Ville {i}"
        plt.text(p[0] + 0.5, p[1] + 0.5, label, fontsize=9)

    # Calcul du temps total de la tournée la plus longue (makespan)
    max_duration = 0
    for tournee in meilleure_solution:
        duration = 0
        for i in range(len(tournee) - 1):
            duration += tempo[tournee[i]][tournee[i + 1]]
        if duration > max_duration:
            max_duration = duration

    print(f"\nFenêtre de temps autorisée (global) : {time_window} minutes")
    if max_duration > time_window:
        print(f"La fenêtre de temps est dépassée de {max_duration - time_window} minutes")
    else:
        print(f"La fenêtre de temps est respectée "
              f"(il reste {time_window - max_duration} minutes)")

    plt.title(f"{k} camions – Tous clients desservis")
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.grid(True)
    plt.show()

# 8) Résoudre par PLNE (pour petits nombres) avec ajout de la contrainte globale "temps ≤ time_window"
def plne(nbr, k, city, tempo, time_window):
    prob = LpProblem("VRPTW_PLNE", LpMinimize)

    # Variables binaires x[(i,j)] pour arc i→j
    x = LpVariable.dicts("x", [(i, j) for i in range(nbr) for j in range(nbr) if i != j], cat='Binary')
    # Variables d'ordre pour éliminer sous-tours (MTZ)
    u = LpVariable.dicts("u", range(nbr), lowBound=0, upBound=nbr - 1, cat='Integer')

    # 8.1) Objectif : minimiser la distance totale
    prob += lpSum(tempo[i][j] * x[(i, j)] for i in range(nbr) for j in range(nbr) if i != j)

    # 8.2) Contrainte : chaque ville i reçoit exactement un arc entrant et un arc sortant (sauf i=0, on force k arcs entrants et sortants)
    for i in range(nbr):
        if i == 0:
            # Dépôt : k arcs sortants, k arcs entrants (vrai si chacun des k véhicules part et revient)
            prob += lpSum(x[(0, j)] for j in range(1, nbr)) == k
            prob += lpSum(x[(i, 0)] for i in range(1, nbr)) == k
        else:
            prob += lpSum(x[(i, j)] for j in range(nbr) if i != j) == 1
            prob += lpSum(x[(j, i)] for j in range(nbr) if i != j) == 1

    # 8.3) MTZ pour éliminer les sous-tours (sous-tours interdits)
    N = nbr / k  # borne sur l’ordre des clients
    for i in range(1, nbr):
        for j in range(1, nbr):
            if i != j:
                prob += u[i] - u[j] <= N * (1 - x[(i, j)]) - 1

    # 8.4) Contrainte globale de temps (makespan) ≤ time_window
    #       On impose que la plus longue tournée n’excède pas time_window.
    #       Pour cela, on peut approximer : pour chaque arc (i,j),
    #       si x[i,j]=1, le temps accumulé (variable t_j) ≥ t_i + tempo[i][j].
    #       Mais pour simplifier, on ajoute une variable temps_max (le makespan)
    #       et on relie :
    #         temps_max ≥ somme des distances de la tournée v
    #       On linéarise en sommant sur tous les arcs des k tournées :
    temps_max = LpVariable("temps_max", lowBound=0, cat="Integer")
    # Chaque arc (i,j) utilisé contribue à la distance totale d’un véhicule.
    # Mais pour faire simple, on impose que la somme des distances de TOUTES tournées ≤ k * time_window,
    # puis on force temps_max ≥ distance de chaque tournée séparément via MTZ + variable auxiliaire.
    # Ici, pour la simplicité, on impose directement :
    prob += temps_max <= time_window  # makespan ≤ fenêtre donnée

    # ATTENTION : cette modélisation grossière suppose que la "distance totale / k" approxime le temps par véhicule.
    # Pour un modèle exact, il faudrait des variables t_i pour chaque client et chaque véhicule comme précédemment.
    # Mais pour nos petits n, on accepte cette approximation.

    # 8.5) On lie temps_max à l’objectif en orienteur temporel :
    #       temps_max ≥ distance_totale / k  → distance_totale ≤ k * temps_max
    total_distance = lpSum(tempo[i][j] * x[(i, j)] for i in range(nbr) for j in range(nbr) if i != j)
    prob += total_distance <= k * temps_max

    # 8.6) Résoudre
    prob.solve(PULP_CBC_CMD(msg=False))

    statut = LpStatus[prob.status]
    if statut in ['Infeasible', 'Unbounded']:
        print("PLNE infaisable ou non borné → bascule vers Tabu Search.")
        return None, None

    if statut != 'Optimal':
        print(f"PLNE statut = {statut} (non optimal). On utilise la solution faisable.")

    # 8.7) Extraction des tournées à partir des arêtes sélectionnées
    aretes = [(i, j) for i in range(nbr) for j in range(nbr) if i != j and value(x[(i, j)]) == 1]
    # Reconstitution tournée par tournée
    tours = []
    used = set()
    for v_id in range(k):
        route = [0]
        current = 0
        while True:
            # Cherche un arc sortant (current → j)
            found_next = False
            for (i, j) in aretes:
                if i == current and (i, j) not in used:
                    route.append(j)
                    used.add((i, j))
                    current = j
                    found_next = True
                    break
            if not found_next or current == 0:
                break
        # S'assurer qu'on revient bien au dépôt
        if route[-1] != 0:
            route.append(0)
        tours.append(route)

    # 8.8) Calcul du coût total réel
    total_dist = sum(tempo[route[i]][route[i + 1]] for route in tours for i in range(len(route) - 1))
    return tours, total_dist

# 9) Fonction de bascule : si PLNE échoue, on appelle Tabu Search
def solve_vrptw_complete(nbr, k, city, tempo, time_window):
    # Pour petits n,k → PLNE
    if nbr <= 10 and k <= 3:
        tours, dist = plne(nbr, k, city, tempo, time_window)
        if tours is not None:
            print("\n=== Résultats PLNE ===")
            for idx, route in enumerate(tours):
                seq = ' -> '.join(str(v) for v in route[1:-1])
                print(f"Camion {idx+1} : 0 -> {seq} -> 0")
            print(f"Distance totale PLNE : {dist}")
            # Vérification de la fenêtre de temps
            # Calcul du temps maximum d'une tournée
            max_time = 0
            for route in tours:
                t_route = sum(tempo[route[i]][route[i + 1]] for i in range(len(route) - 1))
                max_time = max(max_time, t_route)
            print(f"Temps le plus long (makespan) : {max_time} min / Fenêtre autorisée : {time_window} min")
            if max_time > time_window:
                print(f"Fenêtre de temps dépassée de {max_time - time_window} minutes.")
            else:
                print(f"Fenêtre de temps respectée ({time_window - max_time} min restantes).")
            # Trace
            colors = [np.random.rand(3) for _ in range(len(tours))]
            for route, c in zip(tours, colors):
                for i in range(len(route) - 1):
                    p1, p2 = city[route[i]], city[route[i + 1]]
                    plt.plot([p1[0], p2[0]], [p1[1], p2[1]], color=c)
            for i, p in enumerate(city):
                plt.scatter(p[0], p[1], c='k')
                label = 'Dépôt' if i == 0 else f"Ville {i}"
                plt.text(p[0] + 0.5, p[1] + 0.5, label, fontsize=9)
            plt.title(f"PLNE : {k} camions – {nbr} villes")
            plt.xlabel("X")
            plt.ylabel("Y")
            plt.grid(True)
            plt.show()
            return

    # Sinon → Tabu Search
    print("→ Utilisation de la métaheuristique Tabu Search (besoin de plus de clients ou véhicules).")
    meilleure_solution, meilleur_cout = recherche_tabou_vrp(tempo, k, nbr, time_window)
    best_soluce_print((meilleure_solution, meilleur_cout), city, tempo, k, time_window)

# 10) Programme principal
if __name__ == "__main__":
    # Lecture des paramètres utilisateur
    nbr = int(input("Entrez le nombre de clients (incluant le dépôt) : "))
    k = int(input("Entrez le nombre de véhicules : "))
    tw = input("Indiquez la fenêtre de temps globale (format HhMM, ex: 1h30) : ")
    try:
        hours, minutes = map(int, tw.split('h'))
        time_window = hours * 60 + minutes
    except ValueError:
        print("Format de la fenêtre de temps invalide. Utilisez le format HhMM (ex: 1h30).")
        exit(1)

    tempsmax = 500
    seed = 3

    # Création des villes et de la matrice de distances
    city, tempo = createcity(nbr, tempsmax, seed)

    # Appel de la fonction de résolution complète (PLNE ou Tabu Search)
    solve_vrptw_complete(nbr, k, city, tempo, time_window)
