

# Résolution du Problème de Tournées de Véhicules (VRP) avec Fenêtre de Temps

Ce projet implémente une solution au **Vehicle Routing Problem with Time Windows (VRPTW)**, un problème classique d'optimisation combinatoire qui consiste à planifier les tournées de plusieurs véhicules pour desservir un ensemble de clients, tout en respectant une contrainte de fenêtre de temps globale.

---

## Description du problème (VRPTW)

Le VRP consiste à trouver les itinéraires optimaux pour un nombre donné de véhicules partant d'un dépôt (ville 0), visitant un ensemble de clients, puis revenant au dépôt, de manière à minimiser la distance totale parcourue. Dans cette version, une **fenêtre de temps globale** limite la durée maximale autorisée pour la tournée la plus longue (makespan).

---

## Fonctionnalités principales du code

Le code propose deux méthodes de résolution :

- **PLNE (Programmation Linéaire en Nombres Entiers)** : méthode exacte adaptée aux petits problèmes (nombre de clients ≤ 10, nombre de véhicules ≤ 3).
- **Recherche Tabou (Tabu Search)** : métaheuristique pour les problèmes plus grands, qui explore le voisinage des solutions en évitant les cycles.

---

## Détail des fonctions

### 1. `createcity(nbr, tempsmax, seed)`

- Génère aléatoirement les coordonnées (x, y) de `nbr` villes dans un carré de taille `tempsmax`.
- Calcule la matrice des distances euclidiennes entières entre chaque paire de villes.
- La ville 0 est le dépôt.
- Paramètres :
    - `nbr` : nombre total de villes (clients + dépôt)
    - `tempsmax` : taille maximale pour les coordonnées
    - `seed` : graine aléatoire pour reproductibilité
- Retourne : liste des coordonnées et matrice des distances.


### 2. `calculer_cout_total(solution, tempo)`

- Calcule le coût total (distance) d'une solution donnée, composée de plusieurs tournées.
- Chaque tournée commence et se termine au dépôt (ville 0).
- Paramètres :
    - `solution` : liste de tournées (listes de villes)
    - `tempo` : matrice des distances
- Retourne : coût total (entier).


### 3. `echanger_clients(route1, route2)`

- Échange aléatoirement un client (différent du dépôt) entre deux tournées, pour générer un voisin dans la recherche tabou.
- Ne modifie pas les tournées si elles ont moins de 3 villes (dépôt + au moins 1 client).


### 4. `est_tournee_valide(tournee)`

- Vérifie qu'une tournée commence et se termine bien au dépôt (ville 0).


### 5. `initialiser_solution(k, nbr)`

- Génère une solution initiale faisable pour `k` véhicules et `nbr` villes.
- Répartit cycliquement les clients entre les véhicules.
- Ajoute le dépôt au début et à la fin de chaque tournée.
- S'assure qu'aucune tournée n'est vide.


### 6. `recherche_tabou_vrp(tempo, k, nbr, time_window)`

- Implémente la métaheuristique Tabu Search pour optimiser les tournées.
- Explore le voisinage en échangeant des clients entre tournées.
- Garde une liste tabou pour éviter les retours en arrière.
- Retourne la meilleure solution trouvée et son coût.


### 7. `best_soluce_print(L, city, tempo, k, time_window)`

- Affiche la meilleure solution trouvée (tournées et coût).
- Vérifie si la fenêtre de temps globale est respectée.
- Affiche graphiquement les tournées sur un plan 2D avec matplotlib.


### 8. `plne(nbr, k, city, tempo, time_window)`

- Résout le VRPTW par programmation linéaire en nombres entiers (PLNE) avec la bibliothèque PuLP.
- Modélise les contraintes classiques du VRP avec élimination de sous-tours (MTZ).
- Implique une contrainte globale sur le makespan (durée maximale d'une tournée).
- Adapté aux petits problèmes.
- Retourne les tournées optimales et le coût total.


### 9. `solve_vrptw_complete(nbr, k, city, tempo, time_window)`

- Fonction principale de résolution.
- Choisit la méthode PLNE si le problème est petit, sinon Tabu Search.
- Affiche et trace les résultats.


### 10. Programme principal (`__main__`)

- Demande à l'utilisateur :
    - Nombre de clients (incluant dépôt)
    - Nombre de véhicules
    - Fenêtre de temps globale (ex: "1h30")
- Génère les villes et matrice de distances.
- Lance la résolution complète.

---

## Exemple d'utilisation



---

## 🗺️ Exemple de problème

- `n = 15` villes (0 = dépôt, 1 à 14 = clients)
- `k = 3` véhicules
- Fenêtre de temps = `1h30` (90 minutes)


```bash
Entrez le nombre de clients (incluant le dépôt) : 14
Entrez le nombre de véhicules : 3
Indiquez la fenêtre de temps globale (format HhMM, ex: 1h30) : 1h30
```


## Main programme : plot.py
Le programme affichera les tournées optimales, la distance totale, et indiquera si la fenêtre de temps est respectée, avec un graphique des trajets.  



---

## Dépendances

- Python 3.x
- numpy
- matplotlib
- pulp (pour la PLNE)

Installation via pip :

```bash
pip install numpy matplotlib pulp
```


---

## Architecture simplifiée 

| Fonction                               | Description                                              |
| -------------------------------------- | -------------------------------------------------------- |
| `createcity(nbr, tempsmax, seed)`      | Génère les coordonnées des villes + matrice de distances |
| `calculer_cout_total(solution, tempo)` | Calcule le coût total (distance) d’une solution          |
| `initialiser_solution(k, nbr)`         | Initialise une solution faisable pour Tabu Search        |
| `recherche_tabou_vrp(...)`             | Résout le VRP avec Tabu Search                           |
| `plne(...)`                            | Résout le VRP avec `PuLP` en PLNE (si possible)          |
| `solve_vrptw_complete(...)`            | Appelle PLNE si possible, sinon Tabu Search              |
| `best_soluce_print(...)`               | Affiche et trace la meilleure solution trouvée           |


## Notes

- La modélisation PLNE est simplifiée pour la contrainte de fenêtre de temps globale.
- La recherche tabou est une heuristique qui peut ne pas garantir l'optimalité mais fonctionne bien pour des instances plus grandes.
- Le dépôt est toujours la ville 0.
- La fenêtre de temps est exprimée en minutes.

---

## VRP Solver – Module de base pour le problème de tournées de véhicules sans IHM : vrp_solver.py
Ce module Python propose des outils simples et efficaces pour générer, manipuler et résoudre des instances du Vehicle Routing Problem (VRP), incluant :

Génération de villes et de la matrice de distances,

Calcul du coût total d’une solution,

Fonctions utilitaires pour la métaheuristique Tabu Search.

La seconde partie consistera à faire une étude statistique 