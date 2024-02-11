import random
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.animation import FuncAnimation

# Input parameters
plot_size = (100, 100)  # Example plot size (width, height)
min_room_size = (10, 10)  # Example minimum room size (width, height)
num_bedrooms = 3  # Example number of bedrooms

# Genetic algorithm parameters
POPULATION_SIZE = 50
NUM_GENERATIONS = 30
MUTATION_RATE = 0.1
MAX_MUTATION_PERCENTAGE = 0.2  # Maximum percentage change during mutation
SIZE_INCREASE_FACTOR = 1.5  # Factor by which a room size can be increased

# Generate initial population
def generate_initial_population(num_bedrooms):
    return [{'rooms': generate_random_rooms(num_bedrooms), 'fitness': 0} for _ in range(POPULATION_SIZE)]

# Generate random rooms for a floor plan
def generate_random_rooms(num_bedrooms):
    num_rooms = max(num_bedrooms, random.randint(1, 5))
    rooms = []

    for _ in range(num_rooms):
        size = (random.randint(min_room_size[0], plot_size[0] // 2),
                random.randint(min_room_size[1], plot_size[1] // 2))

        # Ensure rooms are placed more centrally to reduce wasted space
        position = (random.randint(0, plot_size[0] - size[0]),
                    random.randint(0, plot_size[1] - size[1]))

        rooms.append({'position': position, 'size': size})

    return rooms

# Evaluate fitness of a floor plan
def evaluate_fitness(floor_plan):
    total_area = sum(room['size'][0] * room['size'][1] for room in floor_plan)
    return total_area

# Crossover (Recombination)
def crossover(parent1, parent2):
    crossover_point = random.randint(1, min(len(parent1['rooms']), len(parent2['rooms'])) - 1)
    new_rooms = parent1['rooms'][:crossover_point] + parent2['rooms'][crossover_point:]
    
    return {'rooms': new_rooms, 'fitness': 0}

# Mutate a floor plan
def mutate(floor_plan):
    mutated_plan = floor_plan.copy()

    for room in mutated_plan['rooms']:
        if random.random() < MUTATION_RATE:
            # Mutate room size with a sensible change
            mutation_percentage = random.uniform(-MAX_MUTATION_PERCENTAGE, MAX_MUTATION_PERCENTAGE)
            mutated_width = max(min(room['size'][0] * (1 + mutation_percentage), plot_size[0]), min_room_size[0])
            mutated_height = max(min(room['size'][1] * (1 + mutation_percentage), plot_size[1]), min_room_size[1])

            # Check for available space to increase room size
            available_width = plot_size[0] - (room['position'][0] + mutated_width)
            available_height = plot_size[1] - (room['position'][1] + mutated_height)

            if available_width > 0 and available_height > 0:
                # Increase room size
                mutated_width = min(mutated_width * SIZE_INCREASE_FACTOR, available_width)
                mutated_height = min(mutated_height * SIZE_INCREASE_FACTOR, available_height)

            room['size'] = (mutated_width, mutated_height)

    return {'rooms': mutated_plan['rooms'], 'fitness': 0}

# Main genetic algorithm loop
def genetic_algorithm(num_bedrooms):
    population = generate_initial_population(num_bedrooms)
    best_floor_plan = None

    fig, ax = plt.subplots()
    ax.set_xlim(0, plot_size[0])
    ax.set_ylim(0, plot_size[1])

    def update_plot(generation):
        nonlocal best_floor_plan
        nonlocal population

        ax.clear()
        ax.set_xlim(0, plot_size[0])
        ax.set_ylim(0, plot_size[1])

        for room in best_floor_plan['rooms']:
            position = room['position']
            size = room['size']
            rect = Rectangle((position[0], position[1]), size[0], size[1], linewidth=1, edgecolor='r', facecolor='none')
            ax.add_patch(rect)

        plt.title(f'Generation {generation}, Fitness: {best_floor_plan["fitness"]}')
        plt.draw()

    for generation in range(NUM_GENERATIONS):
        for i in range(POPULATION_SIZE):
            population[i]['fitness'] = evaluate_fitness(population[i]['rooms'])

        parents = sorted(population, key=lambda x: x['fitness'], reverse=True)[:2]

        new_population = [crossover(parents[0], parents[1]) for _ in range(POPULATION_SIZE)]
        new_population = [mutate(floor_plan) for floor_plan in new_population]

        population = new_population

        best_floor_plan = max(population, key=lambda x: x['fitness'])

        update_plot(generation)
    
    plt.show()

    return best_floor_plan['rooms']

# Example usage
best_floor_plan = genetic_algorithm(num_bedrooms)
print("Best Floor Plan:", best_floor_plan)
