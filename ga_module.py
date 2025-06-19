import random
from typing import Dict, List, Tuple
import copy

def extract_state(cloud_clusters: Dict[str, List[Dict]]
) -> Tuple[Dict[str, List[Dict]], Dict[str, List[Dict]]]:
    
    tasks_by_cluster = {}
    servers_by_cluster = {}

    for cname, servers in cloud_clusters.items():
       
        tasks = []
        for srv in servers:
            for t in srv.get("tasks", []):
                tasks.append({
                    "device_id":  t["device_id"],
                    "task":       t["task"],
                    "complexity": t["complexity"],
                    "orig_server": srv["server_id"]
                })
        tasks_by_cluster[cname] = tasks

        
        servers_by_cluster[cname] = [
            {
                "server_id":  srv["server_id"],
                "cpu":        srv["cpu"],       
                "ram":        srv["ram"],
                "bandwidth":  srv["bandwidth"],
                "throughput": srv.get("throughput", 0),
            }
            for srv in servers
        ]

    return tasks_by_cluster, servers_by_cluster

def generate_chromosome(
    tasks: List[Dict],
    servers: List[Dict],
    use_orig: bool = False
) -> List[Dict]:
   
    chromosome = []
    for task in tasks:
        if use_orig:
            server_id = task["orig_server"]
        else:
            eligible = [s for s in servers if task["complexity"] <= s["cpu"]]
            if not eligible:
                eligible = servers  
            server_id = random.choice(eligible)["server_id"]

        chromosome.append({
            "device_id":  task["device_id"],
            "task":       task["task"],
            "complexity": task["complexity"],
            "server_id":  server_id,
        })
    return chromosome

def generate_initial_population(
    cloud_clusters: Dict[str, List[Dict]],
    population_size: int = 10
) -> Dict[str, List[List[Dict]]]:
    
    tasks_map, servers_map = extract_state(cloud_clusters)
    populations: Dict[str, List[List[Dict]]] = {}

    for cname in cloud_clusters:
        tasks   = tasks_map[cname]
        servers = servers_map[cname]

     
        pop = [generate_chromosome(tasks, servers, use_orig=True)]

      
        for _ in range(population_size - 1):
            pop.append(generate_chromosome(tasks, servers, use_orig=False))

        populations[cname] = pop

    return populations

def evaluate_chromosome(
    chromosome: List[Dict],
    servers: List[Dict],
    weights: Dict[str, float]
) -> float:

   
    tasks_by_srv = {srv["server_id"]: [] for srv in servers}
    for gene in chromosome:
        tasks_by_srv[gene["server_id"]].append(gene)

    best_fs = -float("inf")
    for srv in copy.deepcopy(servers):  
        used_cpu = sum(g["complexity"] for g in tasks_by_srv[srv["server_id"]])
        CA = max(0, srv["cpu"] - used_cpu)         
        RA = srv["ram"]
        BA = srv["bandwidth"]
        TS = srv["throughput"]

        fs = (
            weights["cpu"]        * CA +
            weights["ram"]        * RA +
            weights["bandwidth"]  * BA +
            weights["throughput"] * TS
        )
        best_fs = max(best_fs, fs)
        print(f"[FITNESS] Chromosome with server: {srv['server_id']}, Remaining CPU: {CA}, Fitness: {fs}")

    return best_fs

def evaluate_population(
    populations: Dict[str, List[List[Dict]]],
    ORIGINAL_CLUSTERS: Dict[str, List[Dict]],  
    weights: Dict[str, float]
) -> Dict[str, List[float]]:
    fitness_map: Dict[str, List[float]] = {}
    for cname, chroms in populations.items():
        fitness_map[cname] = [
            evaluate_chromosome(chrom, ORIGINAL_CLUSTERS[cname], weights)
            for chrom in chroms
        ]
    return fitness_map



import random
from typing import List, Dict


def roulette_selection(population: List[List[Dict]], fitness_scores: List[float], num_parents: int = 2) -> List[List[Dict]]:
    total_fitness = sum(fitness_scores)
    if total_fitness == 0:
      
        return random.sample(population, num_parents)

    selection_probs = [score / total_fitness for score in fitness_scores]
    selected = random.choices(population, weights=selection_probs, k=num_parents)
    return selected


def two_point_crossover(parent1: List[Dict], parent2: List[Dict]) -> List[Dict]:
    size = len(parent1)
    if size < 2:
        return parent1.copy()

    pt1 = random.randint(0, size - 2)
    pt2 = random.randint(pt1 + 1, size - 1)

    child = parent1[:pt1] + parent2[pt1:pt2] + parent1[pt2:]

    return child

def mutate_chromosome(chromosome: List[Dict], servers: List[Dict], mutation_rate: float = 0.20) -> List[Dict]:
    new_chrom = []
    for gene in chromosome:
        if random.random() < mutation_rate:
          
            eligible = [s for s in servers if gene["complexity"] <= s["cpu"]]
            if eligible:
                new_server = random.choice(eligible)
                new_gene = gene.copy()
                new_gene["server_id"] = new_server["server_id"]
                new_chrom.append(new_gene)
            else:
                new_chrom.append(gene)
        else:
            new_chrom.append(gene)
    return new_chrom

def evolve_population(
    population: List[List[Dict]],
    fitness_scores: List[float],
    servers: List[Dict],
    population_size: int
) -> List[List[Dict]]:
    import copy
    new_generation = []

    
    best_idx = fitness_scores.index(max(fitness_scores))
    new_generation.append(population[best_idx])

   
    while len(new_generation) < population_size:
       
        attempts = 0
        max_attempts = 10
        while True:
            parent1, parent2 = roulette_selection(population, fitness_scores, num_parents=2)
            if parent1 != parent2:
                break
            attempts += 1
            if attempts >= max_attempts:
               
                break

     
        child = two_point_crossover(parent1, parent2)

        
        mutated_child = mutate_chromosome(child, copy.deepcopy(servers))  

        new_generation.append(mutated_child)

    return new_generation
