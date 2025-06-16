import random
import os

def generate_instance(filename: str, num_clients: int, num_vehicles: int, max_coord: float, time_window: tuple):
    with open(filename, 'w') as f:
        f.write(f"NUM_CLIENTS {num_clients}\n")
        f.write(f"NUM_VEHICLES {num_vehicles}\n")

        # Dépôt (toujours à 0,0)
        f.write(f"CITY 0 0.0 0.0 0.0 {time_window[1]}\n")

        for i in range(1, num_clients + 1):
            x = random.uniform(0, max_coord)
            y = random.uniform(0, max_coord)
            early = random.uniform(time_window[0], time_window[1] - 50)
            late = early + random.uniform(20, 50)
            late = min(late, time_window[1])  # Ne pas dépasser la borne supérieure
            f.write(f"CITY {i} {x:.2f} {y:.2f} {early:.2f} {late:.2f}\n")

if __name__ == "__main__":
    random.seed(42)

    MIN_TIME = 10             # 10 minutes
    MAX_TIME = 7 * 24 * 60    # 7 jours en minutes (10080)

    os.makedirs("instances", exist_ok=True)

    for i in range(1, 51):
        filename = f"instances/instance_{i}.txt"
        num_clients = random.randint(10, 500)
        num_vehicles = max(2, num_clients // 10)
        max_coord = 100
        time_limit = MIN_TIME + int((MAX_TIME - MIN_TIME) * (i / 50))  # Croissance linéaire
        time_window = (0, time_limit)
        generate_instance(filename, num_clients, num_vehicles, max_coord, time_window)
