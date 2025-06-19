import random
import streamlit as st
from iot_device_simulator import generate_iot_devices
from ga_module import generate_initial_population
import copy
from ga_module import generate_initial_population, evaluate_population


devices = generate_iot_devices(n=8)

CLOUD_CLUSTERS = {
    "Cluster 1": [
        {"server_id": "S1", "cpu": 4000, "ram": 16, "bandwidth": 10, "throughput": 5, "tasks": []},
        {"server_id": "S2", "cpu": 3000, "ram":  8, "bandwidth":  8, "throughput": 4, "tasks": []},
    ],
    "Cluster 2": [
        {"server_id": "S3", "cpu": 3500, "ram": 12, "bandwidth":  9, "throughput": 4, "tasks": []},
        {"server_id": "S4", "cpu": 2500, "ram":  8, "bandwidth":  7, "throughput": 3, "tasks": []},
    ],
}

ORIGINAL_CLUSTERS = copy.deepcopy(CLOUD_CLUSTERS)

for device in devices:
  
    cluster_name = random.choice(list(CLOUD_CLUSTERS.keys()))
    servers = CLOUD_CLUSTERS[cluster_name]

    for task in device["task_queue"]:
       
        servers_sorted = sorted(servers, key=lambda s: s["cpu"], reverse=True)
        for server in servers_sorted:
            if task["complexity"] <= server["cpu"]:
                server["tasks"].append({
                    "device_id": device["id"],
                    "task": task["task"],
                    "complexity": task["complexity"]
                })
                server["cpu"] -= task["complexity"] 
                break 


st.title("Smart Home IoT Load Balancer")


st.header("Step 1: IoT Devices")
for device in devices:
    with st.expander(f"{device['id']} — {device['type']}"):
        st.write(f"**CPU:** {device['cpu']} MIPS")
        st.write(f"**RAM:** {device['ram']} GB")
        st.write(f"**Bandwidth:** {device['bandwidth']} Mbps")
        st.write(f"**Throughput:** {device['throughput']} MB/s")
        st.write(f"**Availability:** {device['availability'] * 100:.1f}%")
        st.write(f"**Priority Score:** {device['priority_score']}")
        st.write(f"**Status:** {device['status']}")
        st.subheader("Task Queue")
        for t in device["task_queue"]:
            st.markdown(f"- **{t['task']}** (Complexity: {t['complexity']})")

st.header("Step 2: Cloud Data Center Simulation")

for cluster_name, servers in CLOUD_CLUSTERS.items():
    with st.expander(cluster_name):
        for i, server in enumerate(servers):  
            st.subheader(f"Server {server['server_id']}")
            init_cpu = ORIGINAL_CLUSTERS[cluster_name][i]["cpu"] 
            st.write(f"- **Initial CPU:** {init_cpu} MIPS")
            st.write(f"- **Remaining CPU:** {server['cpu']} MIPS")
            st.write(f"- **RAM:** {server['ram']} GB")
            st.write(f"- **Bandwidth:** {server['bandwidth']} Mbps")
            st.write(f"- **Throughput:** {server['throughput']} MB/s")
            st.write("**Assigned Tasks:**")
            if server["tasks"]:
                for task in server["tasks"]:
                    st.markdown(
                        f"- Device {task['device_id']} → **{task['task']}** "
                        f"(Complexity: {task['complexity']})"
                    )
            else:
                st.write("No tasks assigned")


pop_size = st.slider("Select population size", min_value=2, max_value=20, value=5)
initial_population = generate_initial_population(CLOUD_CLUSTERS, population_size=pop_size)

st.header("Step 3: Initial Chromosome Population (Per Cluster)")

for cluster_name, population in initial_population.items():
    with st.expander(f"{cluster_name} — Initial Chromosomes"):
        for idx, chromosome in enumerate(population):
            st.subheader(f"Chromosome {idx + 1}")
            for gene in chromosome:
                st.markdown(
                    f"- Device {gene['device_id']} → Task **{gene['task']}** "
                    f"(Complexity: {gene['complexity']}) → Assigned to Server {gene['server_id']}"
                )

st.header("Step 4: Fitness Evaluation")

weights = {
    "cpu": 0.1,
    "ram": 0.3,
    "bandwidth": 0.2,
    "throughput": 0.4
}

fitness_map = evaluate_population(initial_population, ORIGINAL_CLUSTERS, weights)

for cluster_name, fitnesses in fitness_map.items():
    with st.expander(f"{cluster_name} — Chromosome Fitness"):
        for idx, score in enumerate(fitnesses, start=1):
            st.write(f"Chromosome {idx}: Fitness = {score:.2f}")


from ga_module import evolve_population

st.header("Step 5–7: Genetic Algorithm Cycle")

generations = st.slider("Number of generations", min_value=1, max_value=10, value=1)

final_generations = {}
final_fitnesses = {}

for cluster_name, population in initial_population.items():
    st.subheader(f"{cluster_name} — Evolution Process")
    import copy
    servers = copy.deepcopy(ORIGINAL_CLUSTERS[cluster_name])
    current_population = population
    fitness_scores = evaluate_population({cluster_name: current_population}, ORIGINAL_CLUSTERS, weights)[cluster_name]

    for gen in range(generations):
        current_population = evolve_population(current_population, fitness_scores, servers, population_size=pop_size)
        fitness_scores = evaluate_population({cluster_name: current_population}, ORIGINAL_CLUSTERS, weights)[cluster_name]

        with st.expander(f"Generation {gen + 1}"):
            for idx, chrom in enumerate(current_population):
                st.markdown(f"**Chromosome {idx + 1}** — Fitness: `{fitness_scores[idx]:.2f}`")
                for gene in chrom:
                    st.markdown(
                        f"- Device `{gene['device_id']}` → Task **{gene['task']}** → Server `{gene['server_id']}`"
                    )

    final_generations[cluster_name] = current_population
    final_fitnesses[cluster_name] = fitness_scores


st.header("Step 8: Final Leader Election")

for cluster_name, chromosomes in final_generations.items():
    fitnesses = final_fitnesses[cluster_name]
    best_idx = fitnesses.index(max(fitnesses))
    best_chrom = chromosomes[best_idx]

    
    server_task_count = {}
    for gene in best_chrom:
        server_id = gene["server_id"]
        server_task_count[server_id] = server_task_count.get(server_id, 0) + 1

    elected_leader = max(server_task_count, key=server_task_count.get)

    with st.expander(f"{cluster_name} — Elected Leader"):
        st.success(f"Leader Node: `{elected_leader}`")
        st.write(f"Tasks Assigned: {server_task_count[elected_leader]}")
        st.subheader("Final Best Chromosome")
        for gene in best_chrom:
            st.markdown(
                f"- Device `{gene['device_id']}` → Task **{gene['task']}** (Complexity: `{gene['complexity']}`) → Server `{gene['server_id']}`"
            )
