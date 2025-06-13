import random
import math
from typing import List, Tuple



# Classe pour représenter une ville avec position et fenêtre de temps
class City:
    def __init__(self, x: float, y: float, early: float, late: float):
        self.x = x
        self.y = y
        self.early = early  # Début de la fenêtre de temps
        self.late = late    # Fin de la fenêtre de temps

# Générer des villes aléatoires avec fenêtres de temps
def create_cities(n: int, max_coord: float, time_window: Tuple[float, float]) -> List[City]:
    cities = [City(0, 0, 0, float('inf'))]  # Dépôt
    for _ in range(n):
        x = random.uniform(0, max_coord)
        y = random.uniform(0, max_coord)
        early = random.uniform(time_window[0], time_window[1] - 50)
        late = early + random.uniform(20, 50)  # Fenêtre de 20 à 50 unités
        cities.append(City(x, y, early, late))
    return cities

# Calculer la distance euclidienne
def distance(city1: City, city2: City) -> float:
    return math.sqrt((city1.x - city2.x) ** 2 + (city1.y - city2.y) ** 2)

# Calculer le coût total d'une solution avec vérification des fenêtres de temps
def calculate_total_cost(routes: List[List[int]], cities: List[City]) -> Tuple[float, bool]:
    total_distance = 0
    feasible = True
    for route in routes:
        if not route: continue
        time = 0
        for i in range(len(route) - 1):
            curr = route[i]
            next_city = route[i + 1]
            dist = distance(cities[curr], cities[next_city])
            total_distance += dist
            time += dist  # Supposons que la vitesse est de 1 unité par distance
            if time < cities[next_city].early:
                time = cities[next_city].early  # Attendre si trop tôt
            if time > cities[next_city].late:
                feasible = False  # Violation de la fenêtre
    return total_distance, feasible

# Générer une solution initiale
def initial_solution(n: int, k: int) -> List[List[int]]:
    clients = list(range(1, n + 1))  # Exclure le dépôt (0)
    random.shuffle(clients)
    routes = [[] for _ in range(k)]
    for i, client in enumerate(clients):
        routes[i % k].append(client)
    for route in routes:
        if route:  # Ajouter le dépôt au début et à la fin
            route.insert(0, 0)
            route.append(0)
    return routes

# Échanger deux clients entre deux tournées
def swap_clients(routes: List[List[int]]) -> List[List[int]]:
    new_routes = [route[:] for route in routes]
    r1, r2 = random.sample(range(len(routes)), 2)
    if len(new_routes[r1]) > 2 and len(new_routes[r2]) > 2:  # Exclure dépôt
        i = random.randint(1, len(new_routes[r1]) - 2)
        j = random.randint(1, len(new_routes[r2]) - 2)
        new_routes[r1][i], new_routes[r2][j] = new_routes[r2][j], new_routes[r1][i]
    return new_routes

# Recherche tabou
def tabu_search(cities: List[City], k: int, max_iter: int, tabu_size: int) -> List[List[int]]:
    n = len(cities) - 1  # Nombre de clients hors dépôt
    current_solution = initial_solution(n, k)
    best_solution = current_solution[:]
    best_cost, _ = calculate_total_cost(best_solution, cities)
    tabu_list = []
    
    for _ in range(max_iter):
        neighbor = swap_clients(current_solution)
        cost, feasible = calculate_total_cost(neighbor, cities)
        
        if (feasible and cost < best_cost and tuple(map(tuple, neighbor)) not in tabu_list):
            current_solution = neighbor[:]
            best_solution = neighbor[:]
            best_cost = cost
            tabu_list.append(tuple(map(tuple, neighbor)))
            if len(tabu_list) > tabu_size:
                tabu_list.pop(0)
    
    return best_solution

# Exemple d'exécution
if __name__ == "__main__":
    random.seed(42)
    num_clients = 10
    num_vehicles = 3
    cities = create_cities(num_clients, 100, (0, 200))
    solution = tabu_search(cities, num_vehicles, max_iter=1000, tabu_size=50)
    cost, feasible = calculate_total_cost(solution, cities)
    print(f"Solution: {solution}")
    print(f"Coût total: {cost}, Faisable: {feasible}")