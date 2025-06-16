import random
import math
import pulp
import time
from matplotlib import pyplot as plt
from typing import List, Tuple

# Classe pour représenter une ville
class City:
    def __init__(self, x: float, y: float, early: float, late: float):
        self.x = x
        self.y = y
        self.early = early
        self.late = late

# Lire une instance depuis un fichier
def read_instance(filename: str) -> Tuple[List[City], int, int]:
    cities = []
    num_clients = 0
    num_vehicles = 0
    with open(f"instances/{filename}", 'r') as f:
        for line in f:
            parts = line.strip().split()
            if parts[0] == "NUM_CLIENTS":
                num_clients = int(parts[1])
            elif parts[0] == "NUM_VEHICLES":
                num_vehicles = int(parts[1])
            elif parts[0] == "CITY":
                cities.append(City(float(parts[2]), float(parts[3]), float(parts[4]), float(parts[5])))
    return cities, num_clients, num_vehicles

# Calculer la distance euclidienne
def distance(city1: City, city2: City) -> float:
    return math.sqrt((city1.x - city2.x) ** 2 + (city1.y - city2.y) ** 2)

# Résoudre avec PuLP (pour petites instances)
def solve_vrptw_pulp(cities: List[City], k: int) -> Tuple[List[List[int]], float]:
    n = len(cities) - 1
    prob = pulp.LpProblem("VRPTW", pulp.LpMinimize)
    x = pulp.LpVariable.dicts("x", ((i, j, v) for i in range(n+1) for j in range(n+1) if i != j for v in range(k)), cat='Binary')
    t = pulp.LpVariable.dicts("t", (i for i in range(n+1)), lowBound=0)
    prob += pulp.lpSum(distance(cities[i], cities[j]) * x[i, j, v] for i in range(n+1) for j in range(n+1) if i != j for v in range(k))
    for i in range(1, n+1):
        prob += pulp.lpSum(x[i, j, v] for j in range(n+1) if i != j for v in range(k)) == 1
    for v in range(k):
        prob += pulp.lpSum(x[0, j, v] for j in range(1, n+1)) == 1
        prob += pulp.lpSum(x[i, 0, v] for i in range(1, n+1)) == 1
    for i in range(n+1):
        for v in range(k):
            prob += pulp.lpSum(x[i, j, v] for j in range(n+1) if i != j) == pulp.lpSum(x[j, i, v] for j in range(n+1) if i != j)
    M = 10000
    for i in range(n+1):
        for j in range(1, n+1):
            if i != j:
                for v in range(k):
                    prob += t[j] >= t[i] + distance(cities[i], cities[j]) - M * (1 - x[i, j, v])
        if i != 0:
            prob += t[i] >= cities[i].early
            prob += t[i] <= cities[i].late
    prob.solve()
    if pulp.LpStatus[prob.status] != 'Optimal':
        return None, None
    routes = [[] for _ in range(k)]
    for v in range(k):
        current = 0
        route = [0]
        while True:
            for j in range(n+1):
                if j != current and pulp.value(x[current, j, v]) == 1:
                    route.append(j)
                    current = j
                    break
            if current == 0:
                break
        routes[v] = route
    return routes, pulp.value(prob.objective)

# Heuristique simple pour grandes instances
def heuristic_vrptw(cities: List[City], k: int) -> Tuple[List[List[int]], float]:
    n = len(cities) - 1
    clients = list(range(1, n + 1))
    random.shuffle(clients)
    routes = [[] for _ in range(k)]
    for i, client in enumerate(clients):
        routes[i % k].append(client)
    for route in routes:
        if route:
            route.insert(0, 0)
            route.append(0)
    total_cost = 0
    feasible = True
    for route in routes:
        if not route: continue
        time = 0
        for i in range(len(route) - 1):
            dist = distance(cities[route[i]], cities[route[i + 1]])
            total_cost += dist
            time += dist
            if time < cities[route[i + 1]].early:
                time = cities[route[i + 1]].early
            if time > cities[route[i + 1]].late:
                feasible = False
    return routes, total_cost if feasible else float('inf')

# Visualiser les tournées
def plot_routes(cities: List[City], routes: List[List[int]], filename: str):
    colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k']
    plt.figure(figsize=(10, 10))
    for v, route in enumerate(routes):
        if route:
            x_coords = [cities[i].x for i in route]
            y_coords = [cities[i].y for i in route]
            plt.plot(x_coords, y_coords, color=colors[v % len(colors)], marker='o', label=f'Véhicule {v+1}')
    for i, city in enumerate(cities):
        plt.text(city.x, city.y, f'{i}', fontsize=12)
    plt.title(f"Tournées pour {filename}")
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.legend()
    plt.grid(True)
    plt.show()

# Programme principal
if __name__ == "__main__":
    MAX_CITIES = 500
    instance_files = ["instance1.txt", "instance2.txt", "instance3.txt", "instance4.txt", "instance5.txt", "instance6.txt", "instance7.txt", "instance8.txt"]

    for filename in instance_files:
        print(f"\n### Traitement de l'instance : {filename} ###")
        start_time = time.time()
        
        # Lire l'instance
        try:
            cities, num_clients, num_vehicles = read_instance(filename)
            print(f"Instance lue : {num_clients} clients, {num_vehicles} véhicules")
        except FileNotFoundError:
            print(f"Erreur : fichier {filename} non trouvé.")
            continue

        # Vérifier la limite
        if num_clients > MAX_CITIES:
            print(f"Nombre de clients ({num_clients}) dépasse la limite de {MAX_CITIES}. Ignoré.")
            continue

        # Résoudre
        if num_clients <= 10:
            print("Résolution avec PuLP...")
            routes, cost = solve_vrptw_pulp(cities, num_vehicles)
        else:
            print("Résolution avec heuristique...")
            routes, cost = heuristic_vrptw(cities, num_vehicles)

        # Afficher les résultats
        elapsed_time = time.time() - start_time
        if routes and cost is not None and cost != float('inf'):
            print("Solution trouvée :")
            for v, route in enumerate(routes):
                if route:
                    print(f"Tournée du véhicule {v+1}: {route}")
            print(f"Coût total : {cost:.2f}")
            print(f"Nombre de villes parcourues : {num_clients} (max {MAX_CITIES})")
            print(f"Temps de résolution : {elapsed_time:.2f} secondes")
            plot_routes(cities, routes, filename)
        else:
            print("Aucune solution faisable trouvée.")
            print(f"Temps de résolution : {elapsed_time:.2f} secondes")