import os
import time
import datetime
import tracemalloc
import numpy as np
import random
import math
import copy

# 1) Charger une instance depuis un fichier texte (format : coordonnées x y par ligne)
def charger_instance(fichier_instance):
    with open(fichier_instance, 'r') as f:
        lignes = f.readlines()
    villes = [(int(x.split()[0]), int(x.split()[1])) for x in lignes if x.strip()]
    nbr = len(villes)
    tempo = np.zeros((nbr, nbr), dtype=int)
    for i in range(nbr):
        for j in range(nbr):
            if i != j:
                dx = villes[i][0] - villes[j][0]
                dy = villes[i][1] - villes[j][1]
                tempo[i][j] = int(round(math.hypot(dx, dy)))
    return villes, tempo

def calculer_cout_total(solution, tempo):
    cout = 0
    for tour in solution:
        if len(tour) >= 2:
            cout += tempo[0][tour[1]]
            for i in range(1, len(tour) - 1):
                cout += tempo[tour[i]][tour[i + 1]]
            cout += tempo[tour[-1]][0]
    return cout

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
                        client = tournees[j].pop(1)
                        tournees[i].insert(1, client)
                        break
    return tournees

def echanger_clients(route1, route2):
    if len(route1) > 2 and len(route2) > 2:
        idx1 = random.randint(1, len(route1) - 2)
        idx2 = random.randint(1, len(route2) - 2)
        route1[idx1], route2[idx2] = route2[idx2], route1[idx1]

def recherche_tabou_vrp(tempo, k, nbr, taille_tabou=50, nb_iterations=500):
    meilleure_solution = initialiser_solution(k, nbr)
    meilleur_cout = calculer_cout_total(meilleure_solution, tempo)
    solution_actuelle = copy.deepcopy(meilleure_solution)
    liste_tabou = []
    for _ in range(nb_iterations):
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
    return meilleure_solution, meilleur_cout

# 5) Point d’entrée principal
def executer_solver(instance_filename, k, taille_tabou, nb_iterations):
    compilation = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    start_exec = time.time()
    debut = datetime.datetime.now()
    
    tracemalloc.start()

    villes, tempo = charger_instance(instance_filename)
    nbr = len(villes)

    solution, cout = recherche_tabou_vrp(tempo, k, nbr, taille_tabou, nb_iterations)

    fin = datetime.datetime.now()
    end_exec = time.time()
    temps_exec = end_exec - start_exec

    jours, reste = divmod(int(temps_exec), 86400)
    heures, reste = divmod(reste, 3600)
    minutes, secondes = divmod(reste, 60)

    _, peak_memory = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    taille_tabou_mo = round(peak_memory / 1024 / 1024, 4)

    nom_fichier = os.path.basename(instance_filename).replace(".txt", "")
    fichier_solution = f"solutions/solution_{nom_fichier}.txt"
    os.makedirs("solutions", exist_ok=True)

    with open(fichier_solution, "w") as f:
        f.write(f"Compilation effectuée le : {compilation}\n")
        f.write(f"Exécution lancée le      : {debut.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Exécution achevée le     : {fin.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Le programme a été exécuté en {round(temps_exec, 3)} secondes\n")
        f.write(f"  => soit : {jours} jours, {heures} heures, {minutes} minutes, {secondes} secondes\n")
        f.write(f"\nNombre d'itérations       : {nb_iterations}\n")
        f.write(f"Espace mémoire liste tabou: {taille_tabou_mo} Mo\n")
        f.write(f"\nCoût total (distance)     : {cout}\n")
        f.write("\nTournées:\n")
        for i, t in enumerate(solution):
            f.write(f"Camion {i + 1}: {t}\n")

    print(f"Solution enregistrée dans {fichier_solution}")

if __name__ == "__main__":
    # Exemple d'utilisation : fichier, nb véhicules, taille tabou, nb itérations
    executer_solver("instances/instance_01.txt", k=5, taille_tabou=50, nb_iterations=500)
