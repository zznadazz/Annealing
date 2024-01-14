# -*- coding: utf-8 -*-
"""
Created on Sun Jan 14 10:54:12 2024

@author: Nada
"""

import random
import math
import time
import matplotlib.pyplot as plt
import cProfile
# get the start time
st = time.time()

def read_tsp_file(filename):
    """Read TSP data from a file in the TSPLIB format."""
    with open(filename, 'r') as file:
        lines = file.readlines()

    # Extracting node coordinates
    node_coordinates = {}
    read_coordinates = False
    for line in lines:
        if line.startswith("NODE_COORD_SECTION"):
            read_coordinates = True
            continue
        if line.startswith("EOF"):
            break
        if read_coordinates:
            parts = line.strip().split()
            node_coordinates[int(parts[0])] = (float(parts[1]), float(parts[2]))
    
    return node_coordinates

def calculate_distance(coord1, coord2):
    """Calculate Euclidean distance between two coordinates."""
    return math.sqrt((coord1[0] - coord2[0])**2 + (coord1[1] - coord2[1])**2)

def total_distance(tour, node_coordinates):
    """Calculate the total distance of a tour."""
    distance = 0
    for i in range(len(tour)):
        distance += calculate_distance(node_coordinates[tour[i]], node_coordinates[tour[(i + 1) % len(tour)]])
    return distance
def two_opt_swap(route, i, k):
    """Fonction pour effectuer un 2-opt swap."""
    new_route = route[:i] + route[i:k+1][::-1] + route[k+1:]
    return new_route

def two_opt(route, node_coordinates):
    """Fonction pour appliquer l'optimisation 2-opt."""
    improvement = True
    while improvement:
        improvement = False
        for i in range(1, len(route) - 1):
            for k in range(i+1, len(route)):
                new_route = two_opt_swap(route, i, k)
                if total_distance(new_route, node_coordinates) < total_distance(route, node_coordinates):
                    route = new_route
                    improvement = True
        return route
    
def plot_tour(tour, node_coordinates):
    """Plot the tour on a graph."""
    x = [node_coordinates[city][0] for city in tour]
    y = [node_coordinates[city][1] for city in tour]
    
    # Add start to the end to complete the tour
    x.append(x[0])
    y.append(y[0])

    plt.figure(figsize=(12, 8))
    plt.plot(x, y, 'o-', mfc='r')
    plt.xlabel('X Coordinates')
    plt.ylabel('Y Coordinates')
    plt.title('TSP Tour')
    # Add segment numbers
    offset = 5
    for i, city in enumerate(tour):
        plt.text(x[i] + offset , y[i], f'{i+1}', color='blue', fontsize=12)
    plt.show()
# Appliquer 2-opt sur la meilleure solution trouvée
#best_solution = two_opt(best_solution, node_coordinates)
#best_cost = total_distance(best_solution, node_coordinates)

def plot_costs(iteration_costs, temperatures):
    """Plot the cost curve based on iterations."""
    plt.figure(figsize=(10, 5))

    # Plot Distance
    plt.subplot(2, 1, 1)
    plt.plot(iteration_costs[::10], color='red')
    plt.xlabel('Iterations')
    plt.ylabel('Distance')
    plt.title('Distance en fonction des itérations - Simulated Annealing')

    # Plot Temperature
    plt.subplot(2, 1, 2)
    plt.plot(temperatures[::10], color='blue')
    plt.xlabel('Iterations')
    plt.ylabel('Temperature')
    plt.title('Temperature en fonction des itérations - Simulated Annealing')

    plt.tight_layout()
    plt.show()


def simulated_annealing(node_coordinates):
    """Solve the TSP problem using the Simulated Annealing algorithm."""
    # Generate an initial solution randomly
    current_solution = list(node_coordinates.keys())
    random.shuffle(current_solution)
    current_cost = total_distance(current_solution, node_coordinates)

    # Parameters for simulated annealing
    temp = 10000
    cooling_rate = 0.001
    reheating_threshold = 500
    iter_without_improvement = 0
    costs = []
    temperatures = [] 
    
    # Track the best solution found
    best_solution = current_solution
    best_cost = current_cost

    while temp > 1:
        # Generate a neighbor solution with inversion of sub-chain
        neighbor = current_solution[:]
        swap_idx1, swap_idx2 = sorted(random.sample(range(len(neighbor)), 2))
        neighbor[swap_idx1:swap_idx2] = reversed(neighbor[swap_idx1:swap_idx2])

        # Calculate the cost of the neighbor solution
        neighbor_cost = total_distance(neighbor, node_coordinates)
        
        # Add cost to list
        costs.append(current_cost)
        temperatures.append(temp)
        
        # Decide whether to accept the neighbor
        if neighbor_cost < current_cost or random.random() < math.exp((current_cost - neighbor_cost) / temp):
            current_solution = neighbor
            current_cost = neighbor_cost
            iter_without_improvement = 0

            # Update the best solution found
            if neighbor_cost < best_cost:
                best_solution = neighbor
                best_cost = neighbor_cost
        else:
            iter_without_improvement += 1

        # Decrease temperature
        temp *= 1 - cooling_rate

        # Reheating if stuck in a local minimum
        if iter_without_improvement >= reheating_threshold:
            temp *= 1.5
            iter_without_improvement = 0

    # Apply 2-opt optimization on the best solution found
    best_solution = two_opt(best_solution, node_coordinates)
    best_cost = total_distance(best_solution, node_coordinates)

    return best_solution, best_cost, costs, temperatures
    #return best_solution, best_cost

# Example usage with the Berlin

berlin52_coordinates = read_tsp_file("Berlin52.tsp")
#best_tour, best_tour_cost = simulated_annealing(berlin52_coordinates)
#print("Best tour:", best_tour)
#print("Best tour cost:", best_tour_cost)

def run_simulated_annealing_multiple_times(node_coordinates, num_runs):
    """Run the simulated annealing algorithm multiple times and retain the best solution."""
    best_overall_solution = None
    best_overall_cost = float('inf')
    best_overall_iteration_costs = []
    best_temp = []
    for _ in range(num_runs):
        solution, cost, iteration_costs, temperatures = simulated_annealing(node_coordinates)
        #solution, cost = simulated_annealing(node_coordinates)
        if cost < best_overall_cost:
            best_overall_solution = solution
            best_overall_cost = cost
            best_overall_iteration_costs = iteration_costs
            best_temp = temperatures
            
    return best_overall_solution, best_overall_cost, best_overall_iteration_costs, best_temp
    #return best_overall_solution, best_overall_cost
# Exemple d'utilisation :
best_tour, best_tour_cost, iteration_costs, temperatures = run_simulated_annealing_multiple_times(berlin52_coordinates, 15)
#best_tour, best_tour_cost = run_simulated_annealing_multiple_times(berlin52_coordinates, 30)
print("Best overall tour:", best_tour)
print("Best overall tour cost:", best_tour_cost)
plot_tour(best_tour, berlin52_coordinates)
plot_costs(iteration_costs, temperatures)

# Profile the function
#cProfile.run("run_simulated_annealing_multiple_times(berlin52_coordinates, 35)")

# get the end time
et = time.time()

# get the execution time
elapsed_time = et - st
print('Execution time:', elapsed_time, 'seconds')