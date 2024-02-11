import random
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.animation import FuncAnimation

# Constants
PLOT_SIZE = (100, 100)
MIN_ROOM_SIZE = (10, 10)
NUM_BEDROOMS = 2
POPULATION_SIZE = 50
NUM_GENERATIONS = 5
MUTATION_RATE = 0.1
MAX_MUTATION_PERCENTAGE = 0.2
SIZE_INCREASE_FACTOR = 100
COLLISION_RESOLUTION_STEPS = 0
MIN_NUM_ROOMS = 2
GRID_SIZE = (10, 10)  # Divide the plot into a 10x10 grid

def generate_initial_population(num_bedrooms):
    return [{'rooms': generate_random_rooms(num_bedrooms), 'fitness': 0} for _ in range(POPULATION_SIZE)]

def generate_random_rooms(num_rooms):
    rooms = []
    grid = [(x, y) for x in range(0, PLOT_SIZE[0], GRID_SIZE[0]) for y in range(0, PLOT_SIZE[1], GRID_SIZE[1])]

    for _ in range(num_rooms):
        room_grid = random.choice(grid)
        size = (GRID_SIZE[0], GRID_SIZE[1])
        position = (room_grid[0], room_grid[1])

        rooms.append({'position': position, 'size': size})

    return rooms

def evaluate_fitness(floor_plan):
    total_area = sum(room['size'][0] * room['size'][1] for room in floor_plan)
    return total_area

def crossover(parent1, parent2):
    crossover_point = random.randint(1, min(len(parent1['rooms']), len(parent2['rooms'])) - 1)
    new_rooms = parent1['rooms'][:crossover_point] + parent2['rooms'][crossover_point:]

    return {'rooms': new_rooms, 'fitness': 0}

def mutate(floor_plan, expand_walls=True):
    mutated_plan = floor_plan.copy()

    for room in mutated_plan['rooms']:
        if random.random() < MUTATION_RATE:
            mutation_percentage = random.uniform(-MAX_MUTATION_PERCENTAGE, MAX_MUTATION_PERCENTAGE)
            mutated_width = room['size'][0] * (1 + mutation_percentage)
            mutated_height = room['size'][1] * (1 + mutation_percentage)

            available_width = PLOT_SIZE[0] - room['position'][0]
            available_height = PLOT_SIZE[1] - room['position'][1]

            while mutated_width <= available_width and mutated_height <= available_height:
                mutated_width = room['size'][0] * (1 + mutation_percentage)
                mutated_height = room['size'][1] * (1 + mutation_percentage)

                available_width = PLOT_SIZE[0] - room['position'][0]
                available_height = PLOT_SIZE[1] - room['position'][1]

            if mutated_width <= available_width and mutated_height <= available_height:
                room['size'] = (mutated_width, mutated_height)
                mutated_plan['fitness'] = evaluate_fitness(mutated_plan['rooms'])

    for room in mutated_plan['rooms']:
        if expand_walls:
            room_x, room_y = room['position']
            room_w, room_h = room['size']
            available_width = PLOT_SIZE[0] - room_x - room_w
            available_height = PLOT_SIZE[1] - room_y - room_h

            if available_width > 0 and available_height > 0:
                room['size'] = (room_w + available_width, room_h + available_height)

    if len(mutated_plan['rooms']) < MIN_NUM_ROOMS:
        mutated_plan['rooms'] += generate_random_rooms(NUM_BEDROOMS - len(mutated_plan['rooms']), external=True)

    return mutated_plan


def find_colliding_rooms(target_room, all_rooms):
    return [other_room for other_room in all_rooms if other_room != target_room and rooms_overlap(target_room, other_room)]

def rooms_overlap(room1, room2):
    x1, y1, w1, h1 = room1['position'][0], room1['position'][1], room1['size'][0], room1['size'][1]
    x2, y2, w2, h2 = room2['position'][0], room2['position'][1], room2['size'][0], room2['size'][1]

    return not (x1 + w1 < x2 or x2 + w2 < x1 or y1 + h1 < y2 or y2 + h2 < y1)

def resolve_collisions(room1, colliding_rooms, expand_walls=True):
    for other_room in colliding_rooms:
        resolve_collision(room1, other_room, expand_walls)

def resolve_collision(room1, room2, expand_walls=True):
    x_overlap = max(0, min(room1['position'][0] + room1['size'][0], room2['position'][0] + room2['size'][0]) - max(room1['position'][0], room2['position'][0]))
    y_overlap = max(0, min(room1['position'][1] + room1['size'][1], room2['position'][1] + room2['size'][1]) - max(room1['position'][1], room2['position'][1]))

    if x_overlap < y_overlap:
        if expand_walls:
            room1['position'] = (room1['position'][0] - x_overlap / 2, room1['position'][1])
            room1['size'] = (room1['size'][0] + x_overlap, room1['size'][1])
        else:
            room1['position'] = (room1['position'][0] + x_overlap, room1['position'][1])
    else:
        if expand_walls:
            room1['position'] = (room1['position'][0], room1['position'][1] - y_overlap / 2)
            room1['size'] = (room1['size'][0], room1['size'][1] + y_overlap)
        else:
            room1['position'] = (room1['position'][0], room1['position'][1] + y_overlap)

def genetic_algorithm(num_bedrooms):

    print("Generating initial population...")
    population = generate_initial_population(num_bedrooms)
    best_floor_plan = None

    fig, ax = plt.subplots()

    ax.set_xlim(0, PLOT_SIZE[0])
    ax.set_ylim(0, PLOT_SIZE[1])

    def update_plot(generation):
        nonlocal best_floor_plan
        nonlocal population

        ax.clear()
        ax.set_xlim(0, PLOT_SIZE[0])
        ax.set_ylim(0, PLOT_SIZE[1])

        for room in best_floor_plan['rooms']:
            position = room['position']
            size = room['size']
            edge_color = 'black' if room.get('external', False) else 'r'
            rect = Rectangle((position[0], position[1]), size[0], size[1], linewidth=0.9, edgecolor=edge_color, facecolor='none')
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


print("Starting Genetic Algorithm...")
best_floor_plan = genetic_algorithm(NUM_BEDROOMS)
print("Genetic Algorithm finished.")
print("Best Floor Plan: ", best_floor_plan)