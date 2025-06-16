import numpy as np
import random
import math
import copy
import matplotlib.pyplot as plt
import time        # <-- ajout pour mesurer le temps
import sys         # <-- ajout pour mesurer la mémoire

# 1) Générer les villes (coordonnées + matrice de distances)
def createcity(nbr, tempsmax, seed):
    random.seed(seed)
    city = [(random.randint(0, tempsmax), random.randint(0, tempsmax)) for _ in range(nbr)]
    tempo = np.zeros((nbr, nbr), dtype=int)
    for i in range(nbr):
        for j in range(nbr):
            if i != j:
                dx = city[i][0] - city[j][0]
                dy = city[i][1] - city[j][1]
                tempo[i][j] = int(round(math.hypot(dx, dy)))
    return city, tempo

# 2) Calcul du coût total
def calculer_cout_total(solution, tempo):
    cout = 0
    for tour in solution:
        if len(tour) >= 2:
            cout += tempo[0][tour[1]]
            for i in range(1, len(tour) - 1):
                cout += tempo[tour[i]][tour[i + 1]]
            cout += tempo[tour[-1]][0]
    return cout

# 3) Fonctions utilitaires
def est_tournee_valide(tournee):
    return len(tournee) >= 2 and tournee[0] == 0 and tournee[-1] == 0

def initialiser_solution(k, nbr):
    clients = list(range(1, nbr))
    random.shuffle(clients)
    tournees = [[] for _ in range(k)]
    for idx, client in enumerate(clients):
        tournees[idx % k].append(client)
    for i in range(k):
        tournees[i] = [0] + tournees[i] + [0]
    while any(len(t) == 2 for t in tournees):
        for i in range(k):
            if len(tournees[i]) == 2:
                for j in range(k):
                    if len(tournees[j]) > 2:
                        client_a_deplacer = tournees[j].pop(1)
                        tournees[i].insert(1, client_a_deplacer)
                        break
    return tournees

def echanger_clients(route1, route2):
    if len(route1) > 2 and len(route2) > 2:
        idx1 = random.randint(1, len(route1) - 2)
        idx2 = random.randint(1, len(route2) - 2)
        route1[idx1], route2[idx2] = route2[idx2], route1[idx1]





def recherche_tabou_vrp(tempo, k, nbr, time_window, taille_tabou=50, nb_iterations=100):
    meilleure_solution = initialiser_solution(k, nbr)
    meilleur_cout = calculer_cout_total(meilleure_solution, tempo)
    solution_actuelle = copy.deepcopy(meilleure_solution)
    liste_tabou = []

    couts_par_iteration = [meilleur_cout]

    start_time = time.time()  # <-- début chronométrage

    for iteration in range(nb_iterations):
        voisinage = []
        for i in range(k):
            for j in range(i + 1, k):
                voisin = copy.deepcopy(solution_actuelle)
                echanger_clients(voisin[i], voisin[j])
                if all(est_tournee_valide(t) for t in voisin) and voisin not in liste_tabou:
                    voisinage.append(voisin)

        meilleur_voisin = None
        cout_meilleur_voisin = float('inf')
        for voisin in voisinage:
            cout_voisin = calculer_cout_total(voisin, tempo)
            if cout_voisin < cout_meilleur_voisin:
                meilleur_voisin = voisin
                cout_meilleur_voisin = cout_voisin

        if meilleur_voisin:
            solution_actuelle = meilleur_voisin
            if cout_meilleur_voisin < meilleur_cout:
                meilleure_solution = solution_actuelle
                meilleur_cout = cout_meilleur_voisin

        liste_tabou.append(copy.deepcopy(solution_actuelle))
        if len(liste_tabou) > taille_tabou:
            liste_tabou.pop(0)

        couts_par_iteration.append(meilleur_cout)

    end_time = time.time()  # <-- fin chronométrage

    duree = end_time - start_time

    # Calcul mémoire approximative de la liste tabou
    memoire_liste_tabou = sum(sys.getsizeof(sol) for sol in liste_tabou) / (1024*1024)  # en Mo

    # Retour des infos supplémentaires
    return meilleure_solution, meilleur_cout, couts_par_iteration, duree, iteration+1, memoire_liste_tabou


# Fonction d'affichage des résultats et plot (inchangée)
def plot_convergence(couts):
    plt.figure(figsize=(8, 4))
    plt.plot(couts, marker='o', linewidth=1, markersize=2)
    plt.title("Espace de solutions")
    plt.xlabel("Itérations")
    plt.ylabel("Coût total")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    nbr = 10
    k = 8
    time_window = 100

    city, tempo = createcity(nbr, tempsmax=100, seed=42)

    sol_init = initialiser_solution(k, nbr)
    print("Solution initiale :", sol_init)
    print("Coût initial      :", calculer_cout_total(sol_init, tempo))

    best_sol, best_cost, couts_par_iteration, duree, nb_iter, memoire = recherche_tabou_vrp(tempo, k, nbr, time_window)

    print("\nMeilleure solution trouvée par Tabu Search :")
    for idx, route in enumerate(best_sol):
        print(f"  Camion {idx+1} :", route)
    print("Coût total (distance) :", best_cost)

    # Affichage des infos demandées
    print(f"\nTemps de convergence      : {duree:.3f} secondes")
    print(f"Nombre d'itérations       : {nb_iter}")
    print(f"Espace mémoire liste tabou: {memoire:.4f} Mo")

    plot_convergence(couts_par_iteration)
