

# Résolution du Problème de Tournées de Véhicules (VRP) avec Fenêtre de Temps

Ce projet implémente une solution au **Vehicle Routing Problem with Time Windows (VRPTW)**, un problème classique d'optimisation combinatoire qui consiste à planifier les tournées de plusieurs véhicules pour desservir un ensemble de clients, tout en respectant une contrainte de fenêtre de temps globale.

---

## Description du problème (VRPTW)

Le VRP consiste à trouver les itinéraires optimaux pour un nombre donné de véhicules partant d'un dépôt (ville 0), visitant un ensemble de clients, puis revenant au dépôt, de manière à minimiser la distance totale parcourue. Dans cette version, une **fenêtre de temps globale** limite la durée maximale autorisée pour la tournée la plus longue (makespan).

---


## Présentation du choix et description de l'algorithme

## Fonctionnement et paramètres
La recherche tabou est une méthode heuristique qui explore l’espace des solutions possibles pour trouver une solution de bonne qualité en un temps raisonnable. Elle part d’une solution initiale (générée aléatoirement ou via une heuristique constructive) et itère en modifiant cette solution par des "mouvements" pour explorer son "voisinage". À chaque étape :

Elle évalue les solutions voisines (par exemple, en échangeant deux clients dans une route ou en déplaçant un client d’une route à une autre).
Elle choisit la meilleure solution voisine qui n’est pas interdite par la liste tabou, une structure qui stocke les mouvements récents pour éviter de revenir en arrière et de rester coincé dans des optima locaux.
Un critère d’aspiration peut être appliqué : si un mouvement tabou améliore la meilleure solution trouvée jusque-là, il est accepté.
Les paramètres clés à configurer sont :

Taille de la liste tabou : Détermine combien de mouvements récents sont interdits. Une taille trop petite risque de créer des cycles, une taille trop grande peut limiter l’exploration.
Nombre d’itérations : Définit combien de fois l’algorithme explore de nouveaux voisins avant de s’arrêter.
Structure de voisinage : Définit les types de mouvements possibles (échange, insertion, etc.).
Ces paramètres doivent être ajustés expérimentalement en fonction de la taille de l’instance et des contraintes pour optimiser la performance.

## Spécificités algorithmiques ajoutées à la méthode
Pour adapter la recherche tabou au VRP avec fenêtres de temps (VRPTW) :

Gestion des fenêtres de temps : Les contraintes temporelles sont intégrées soit en rejetant les solutions infaisables, soit en ajoutant une pénalité dans la fonction objectif pour les violations des fenêtres de livraison.
Mouvements spécifiques : Des mouvements peuvent être conçus pour mieux respecter les fenêtres de temps, comme déplacer un client vers une route où sa fenêtre est mieux satisfaite ou réorganiser l’ordre des clients dans une route pour réduire les temps d’attente.
Ces adaptations permettent de traiter des contraintes réalistes tout en maintenant l’efficacité de l’algorithme.

## Modélisation du problème selon le formalisme de l’algorithme
Le VRPT est modélisé comme un graphe complet où :

Les sommets sont les points de livraison (clients) et le dépôt.
Les arêtes représentent les plus courts chemins entre ces points, précalculés à partir du graphe routier d’origine.
Une solution est un ensemble de routes, chacune commençant et finissant au dépôt, couvrant tous les clients tout en respectant les contraintes (capacité des véhicules, fenêtres de temps, etc.).
La fonction objectif peut viser à minimiser la distance totale parcourue selon les besoins industriels.

Pourquoi avoir choisi la recherche tabou ?
La recherche tabou est particulièrement adaptée pour résoudre des instances de VRP de grande taille (plusieurs milliers de villes) pour les raisons suivantes :

Efficacité sur les grandes instances : Contrairement aux méthodes exactes (comme la programmation linéaire en nombres entiers), qui deviennent impraticables pour des milliers de clients en raison de leur complexité exponentielle, la recherche tabou, en tant qu’heuristique, offre des solutions de bonne qualité en un temps raisonnable.
Flexibilité : Elle s’adapte facilement à différentes variantes du VRP (avec ou sans fenêtres de temps) en modifiant la structure de voisinage ou la fonction objectif.
Exploration diversifiée : La liste tabou évite les optima locaux, permettant une exploration plus large de l’espace des solutions.
Cependant, elle ne garantit pas l’optimalité globale et nécessite un réglage fin des paramètres (taille de la liste tabou, nombre d’itérations), ce qui peut être un défi mais reste gérable via des tests empiriques.



---

### Comprendre une instance dans le contexte du VRP
Dans le contexte du Vehicle Routing Problem (VRP), une instance est un ensemble spécifique de données qui définit une occurrence particulière du problème à résoudre. Une instance contient toutes les informations nécessaires pour modéliser et résoudre une situation concrète de routage de véhicules. Plus précisément, pour le VRP avec fenêtres de temps (VRPTW), une instance inclut généralement :

Nombre de clients  : Le nombre de points à livrer, hors dépôt.
Nombre de véhicules  : Le nombre de camions disponibles.
Coordonnées des villes : Positions géographiques (par exemple, coordonnées (x, y) dans un plan 2D) du dépôt (souvent noté 0) et des clients (notés 1 à n).
Distances ou temps de trajet : Une matrice de distances ou de temps entre chaque paire de villes (souvent calculée comme la distance euclidienne).
Capacités des véhicules (optionnel) : La capacité maximale de chaque véhicule (par exemple, en poids ou volume).
Demandes des clients (optionnel) : La quantité (poids, volume) à livrer à chaque client.

Une instance est donc un fichier ou une structure de données qui regroupe ces paramètres pour représenter un scénario spécifique, par exemple, une journée de livraison pour une entreprise avec 10 clients, 3 camions et des contraintes de temps.

---

## Fonctionnements et paramètres de l'algorithme 

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

## Instance Solver – Module de base pour le problème de tournées de véhicules sans IHM : instance_solver.py qui utilise VRP Solverpour résoudre chaque instance


### Fonctionnement global
1. Chargement de l’instance

villes, tempo = charger_instance(fichier_instance)

- Lit un fichier texte contenant les coordonnées (x, y) de chaque ville.

Calcule une matrice tempo[i][j] représentant les distances euclidiennes arrondies entre toutes les paires de villes.

2. Initialisation d’une solution

solution_initiale = initialiser_solution(k, nbr)

- Répartit aléatoirement les clients (hors dépôt) entre k camions.
- Chaque tournée commence et se termine par le dépôt (0).

3. Boucle de la recherche tabou

for _ in range(nb_iterations):

À chaque itération :

- Génère des voisins en échangeant deux clients entre deux tournées différentes.

- Évalue les voisins viables (non tabous).

- Sélectionne le meilleur voisin non tabou (coût minimal).

- Met à jour la solution actuelle et éventuellement la meilleure.

- Ajoute la solution actuelle à la liste tabou.

4. Retour du résultat

- Retourne la meilleure solution trouvée (ensemble de tournées) et son coût total (distance cumulée).

- Sauvegarde tous les résultats dans un fichier texte.


## Space – Résoud un VRP à partir du VRP Solver et affiche l'espace des solutions avec la convergence: space.py 


## Instance – Module qui permet de créer des fichiers d'instances du VRP : instance.py 


## Charge - Script pour la montée en charge avec une résolution simultanée de plusieurs instances avec des paramètres croissants.




 