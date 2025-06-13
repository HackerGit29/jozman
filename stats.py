# stats.py
# ---------- 
# Réalise des études statistiques sur le VRP (Tabu Search), en variant :
# - Taille de l’instance (n = 10, 20, 50)
# - Nombre d’itérations Tabu (500, 1000, 2000)
# - Taille de la liste tabou (20, 50, 100)
#
# Pour chaque configuration, on génère 20 instances aléatoires,
# on exécute la métaheuristique Tabu Search, puis on calcule :
#   • Moyenne et écart‐type du coût (distance totale),
#   • Taux de faisabilité (respect d’une fenêtre de temps),
#   • Moyenne et écart‐type du temps de calcul.
#
# On produit également, pour chaque n, une visualisation de la convergence
# (coût minimal vs itérations) pour une configuration de référence.
#
# Usage : python stats.py

import numpy as np
import random
import math
import copy
import time
import matplotlib.pyplot as plt
import csv


# On importe seulement la génération de villes et le calcul de coût
# depuis le module principal VRP. Il faut que "vrp_solver.py" contienne
# au moins les fonctions createcity(nbr, tempsmax, seed) et calculer_cout_total(solution, tempo).
from vrp_solver import createcity, calculer_cout_total

# --------------------------------------------------------
# 1) Tabu Search paramétrée (retourne aussi l’historique de convergence)
# --------------------------------------------------------
def recherche_tabou_vrp_param(tempo, k, n, time_window, nb_iterations, taille_tabou):
    """
    Métaheuristique Tabu Search pour VRP (sans contrainte de fenêtre inside, mais on vérifie à posteriori).

    Args :
        tempo         : matrice n×n des distances entières entre villes
        k             : nombre de véhicules
        n             : nombre de villes (incluant le dépôt indice 0)
        time_window   : fenêtre de temps globale (en minutes)
        nb_iterations : nombre total d’itérations Tabu
        taille_tabou  : taille de la liste tabou

    Retour :
        meilleure_solution : liste de k tournées (chacune = liste d’indices villes, début/fin à 0)
        meilleur_cout       : somme des distances de toutes les tournées
        hist_costs         : liste des meilleurs coûts (globaux) à chaque itération
    """

    # Fonction interne : initialisation aléatoire d'une solution faisable
    def initialiser_solution():
        clients = list(range(1, n))
        random.shuffle(clients)
        tournees = [[] for _ in range(k)]
        for i, client in enumerate(clients):
            tournees[i % k].append(client)
        for i in range(k):
            tournees[i] = [0] + tournees[i] + [0]
        # Si une tournée est trop courte (pas de client), on redispatche
        while any(len(t) == 2 for t in tournees):
            for i in range(k):
                if len(tournees[i]) == 2:
                    for j in range(k):
                        if len(tournees[j]) > 2:
                            client_a_deplacer = tournees[j].pop(1)
                            tournees[i].insert(1, client_a_deplacer)
                            break
        return tournees

    def est_tournee_valide(t):
        return t[0] == 0 and t[-1] == 0

    def calculer_cout_total_locale(sol):
        return calculer_cout_total(sol, tempo)

    # Initialisation
    meilleure_solution = initialiser_solution()
    meilleur_cout = calculer_cout_total_locale(meilleure_solution)
    solution_actuelle = copy.deepcopy(meilleure_solution)

    liste_tabou = []
    hist_costs = [meilleur_cout]

    # Boucle principale
    for it in range(1, nb_iterations + 1):
        voisinage = []
        # Générer voisins en échangeant 2 clients entre 2 tournées
        for i in range(k):
            for j in range(i + 1, k):
                voisin = copy.deepcopy(solution_actuelle)
                # Échange aléatoire de deux clients (positions 1..len-2 pour ne pas toucher 0)
                if len(voisin[i]) > 2 and len(voisin[j]) > 2:
                    idx1 = random.randint(1, len(voisin[i]) - 2)
                    idx2 = random.randint(1, len(voisin[j]) - 2)
                    voisin[i][idx1], voisin[j][idx2] = voisin[j][idx2], voisin[i][idx1]
                    if all(est_tournee_valide(t) for t in voisin) and voisin not in liste_tabou:
                        voisinage.append(voisin)

        # Sélection du meilleur voisin
        meilleur_voisin = None
        cout_meilleur_voisin = float('inf')
        for voisin in voisinage:
            cout = calculer_cout_total_locale(voisin)
            if cout < cout_meilleur_voisin:
                meilleur_voisin = voisin
                cout_meilleur_voisin = cout

        # Actualisation si on trouve un voisin
        if meilleur_voisin is not None:
            solution_actuelle = meilleur_voisin
            if cout_meilleur_voisin < meilleur_cout:
                meilleure_solution = solution_actuelle
                meilleur_cout = cout_meilleur_voisin

        # Mise à jour de la liste tabou
        liste_tabou.append(copy.deepcopy(solution_actuelle))
        if len(liste_tabou) > taille_tabou:
            liste_tabou.pop(0)

        hist_costs.append(meilleur_cout)

    return meilleure_solution, meilleur_cout, hist_costs

# --------------------------------------------------------
# 2) Exécution d’expériences
# --------------------------------------------------------
def run_experiments():
    random.seed(12345)

    # Paramètres à varier
    tailles_n   = [10, 20, 50]               # Nombre de villes (incluant dépôt)
    iterations  = [500, 1000, 2000]          # Nombre d’itérations Tabu
    tabou_sizes = [20, 50, 100]              # Tailles de la liste Tabu
    k_fixed     = 3                          # Nombre fixe de véhicules pour ces tests
    time_window = 1000                       # Fenêtre de temps globale (en minutes), assez grande pour la plupart

    # Nombre d’instances aléatoires par configuration
    runs_per_config = 20

    # Pour stocker tous les résultats :
    # Structure : résultats[(n, nb_iter, tabou_size)] = {
    #       'costs': [...], 'times': [...], 'feasible': [...] 
    # }
    results = {}

    for n in tailles_n:
        for nb_iter in iterations:
            for taille_tabou in tabou_sizes:
                key = (n, nb_iter, taille_tabou)
                results[key] = {'costs': [], 'times': [], 'feasible': []}

                for run_id in range(runs_per_config):
                    # Générer instance aléatoire
                    city, tempo = createcity(n, tempsmax=500, seed=run_id * 100 + n)
                    # On mesure le temps CPU
                    t0 = time.time()
                    sol, cout, _ = recherche_tabou_vrp_param(
                        tempo, k_fixed, n, time_window,
                        nb_iterations=nb_iter, taille_tabou=taille_tabou
                    )
                    t1 = time.time()
                    exec_time = t1 - t0

                    # Vérification de faisabilité temps : calcul du makespan (max durée d'une tournée)
                    max_duration = 0
                    for route in sol:
                        dur = 0
                        for i in range(len(route) - 1):
                            dur += tempo[route[i]][route[i + 1]]
                        if dur > max_duration:
                            max_duration = dur
                    is_feasible = (max_duration <= time_window)

                    # Enregistrement
                    results[key]['costs'].append(cout)
                    results[key]['times'].append(exec_time)
                    results[key]['feasible'].append(1 if is_feasible else 0)

                # Calculer moyennes et écarts-types
                costs_arr     = np.array(results[key]['costs'])
                times_arr     = np.array(results[key]['times'])
                feasible_arr  = np.array(results[key]['feasible'])

                results[key]['cost_mean']      = float(np.mean(costs_arr))
                results[key]['cost_std']       = float(np.std(costs_arr, ddof=1))
                results[key]['time_mean']      = float(np.mean(times_arr))
                results[key]['time_std']       = float(np.std(times_arr, ddof=1))
                results[key]['feasible_rate']  = float(np.mean(feasible_arr))

                print(f"> Instance n={n}, it={nb_iter}, tabu={taille_tabou}  "
                      f"→ cost moy={results[key]['cost_mean']:.1f}±{results[key]['cost_std']:.1f}, "
                      f"time moy={results[key]['time_mean']:.2f}s±{results[key]['time_std']:.2f}s, "
                      f"faisable={results[key]['feasible_rate']*100:.0f}%")

    return results

# --------------------------------------------------------
# 3) Plot : convergence pour une configuration de référence
# --------------------------------------------------------
def plot_convergence_example():
    """
    Trace l’évolution du meilleur coût au fil des itérations pour un exemple
    (n=20, it=2000, tabu=50).
    """
    n_example       = 20
    nb_iter_example = 2000
    tabu_example    = 50
    k_fixed         = 3
    time_window     = 1000

    # Générer une instance aléatoire (seed fixe pour reproductibilité)
    city, tempo = createcity(n_example, tempsmax=500, seed=999)
    # Exécuter Tabu Search en récupérant l’historique des coûts
    _, _, hist_costs = recherche_tabou_vrp_param(
        tempo, k_fixed, n_example, time_window,
        nb_iterations=nb_iter_example, taille_tabou=tabu_example
    )

    plt.figure(figsize=(8, 5))
    plt.plot(range(len(hist_costs)), hist_costs, linewidth=1.5, color='tab:blue')
    plt.xlabel("Itération Tabu")
    plt.ylabel("Meilleur coût (distance totale)")
    plt.title(f"Convergence Tabu Search (n={n_example}, it={nb_iter_example}, tabu={tabu_example})")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# --------------------------------------------------------
# 4) Main : exécuter les expérimentations et tracer
# --------------------------------------------------------
if __name__ == "__main__":

    
    # 4.1) Lancer les 20×3×3×3 expériences
    resultats = run_experiments()

    # 4.2) Sauvegarder  les résultats en csv
    # with open("stats_results.csv", mode="w", newline="", encoding="utf-8") as f_csv:
    #     writer = csv.writer(f_csv)
    #     # En‐tête
    #     writer.writerow([
    #         "n", "nb_iter", "taille_tabou",
    #         "cost_mean", "cost_std",
    #         "time_mean", "time_std",
    #         "feasible_rate"
    #     ])

    #     # Pour chaque configuration (clé = (n, nb_iter, taille_tabou))
    #     for (n, nb_iter, taille_tabou), stats in resultats.items():
    #         writer.writerow([
    #             n,
    #             nb_iter,
    #             taille_tabou,
    #             f"{stats['cost_mean']:.6f}",
    #             f"{stats['cost_std']:.6f}",
    #             f"{stats['time_mean']:.6f}",
    #             f"{stats['time_std']:.6f}",
    #             f"{stats['feasible_rate']:.6f}"
    #         ])




    # 4.3) Tracer un exemple de convergence
    plot_convergence_example()



