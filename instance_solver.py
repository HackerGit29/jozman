import time
import os
from vrp_solver import *
from pathlib import Path

def charger_instance(filepath):
    full_path = f"instances/{filepath}"
    with open(full_path, 'r') as f:
        lines = f.readlines()
    
    num_clients = int(lines[0].split()[1])
    num_vehicles = int(lines[1].split()[1])
    villes = []
    for line in lines[2:]:
        parts = line.strip().split()
        villes.append((float(parts[2]), float(parts[3])))
    
    return num_clients + 1, num_vehicles, villes  # +1 for depot

def generer_tempo_depuis_coords(coords):
    n = len(coords)
    tempo = np.zeros((n, n), dtype=int)
    for i in range(n):
        for j in range(n):
            if i != j:
                tempo[i][j] = int(round(math.hypot(coords[i][0] - coords[j][0], coords[i][1] - coords[j][1])))
    return tempo

def enregistrer_solution(nom_instance, solution, cout, temps_exec, params):
    Path("solutions").mkdir(exist_ok=True)
    output_file = f"solutions/solution_{nom_instance}.txt"
    with open(output_file, 'w') as f:
        f.write(f"Instance: {nom_instance}\n")
        f.write(f"Coût total : {cout}\n")
        f.write(f"Temps de résolution : {temps_exec:.2f} sec\n")
        f.write(f"Paramètres : {params}\n")
        for idx, tour in enumerate(solution):
            f.write(f"Camion {idx+1}: {tour}\n")

if __name__ == "__main__":
    instance_path = input("Nom du fichier d'instance (ex: instance1.txt) : ")
    taille_tabou = int(input("Taille de la liste tabou : "))
    nb_iterations = int(input("Nombre d'itérations : "))

    nom = Path(instance_path).stem

    nbr, k, coords = charger_instance(instance_path)
    tempo = generer_tempo_depuis_coords(coords)

    start = time.time()
    solution, cout = recherche_tabou_vrp(tempo, k, nbr)  # Temps ignoré dans version actuelle
    end = time.time()

    print(f"\nRésultat pour {instance_path}")
    for i, t in enumerate(solution):
        print(f"Camion {i+1} : {t}")
    print(f"Coût total : {cout}")
    print(f"Temps de résolution : {end - start:.2f} sec")

    enregistrer_solution(nom, solution, cout, end - start, {
        "taille_tabou": taille_tabou,
        "nb_iterations": nb_iterations,
        "nb_clients": nbr - 1,
        "nb_vehicules": k
    })
