import random
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.animation import FuncAnimation
import pygame

# Constants
PLOT_SIZE = (50, 100)
MIN_ROOM_SIZE = (10, 10)
NUM_BEDROOMS = 5
POPULATION_SIZE = 50
NUM_GENERATIONS = 500
MUTATION_RATE = 2
MAX_MUTATION_PERCENTAGE = 0.1
SIZE_INCREASE_FACTOR = 1000
COLLISION_RESOLUTION_STEPS = 4
MIN_NUM_ROOMS = 5
GRID_SIZE = (10, 10)

def generate_initial_population(num_bedrooms):
    return [{'rooms': generate_random_rooms(num_bedrooms), 'fitness': 0} for _ in range(POPULATION_SIZE)]

def generate_random_rooms(num_rooms, external=False):
    # Generate a list of random rooms
    rooms = []


    # room is a dictionary with keys 'position' and 'size'
    # position is a tuple (x, y) and size is a tuple (width, height)
    for _ in range(num_rooms):

        # Generate a random room size and position
        size = (random.randint(MIN_ROOM_SIZE[0], PLOT_SIZE[0] // 2),
                random.randint(MIN_ROOM_SIZE[1], PLOT_SIZE[1] // 2))

        # Generate a random room position
        position = (random.randint(0, PLOT_SIZE[0] - size[0] - 1),
                    random.randint(0, PLOT_SIZE[1] - size[1] - 1))


        # add our new RANDOM room to the list of rooms
        rooms.append({'position': position, 'size': size, 'external': external})

    return rooms

def evaluate_fitness(floor_plan):
    # The fitness of a floor plan is the total area of all rooms
    total_area = sum(room['size'][0] * room['size'][1] for room in floor_plan)

    # Penalize floor plans with overlapping rooms
    for room in floor_plan:
        # Find all rooms that overlap with the current room
        colliding_rooms = find_colliding_rooms(room, floor_plan)
        resolve_collisions(room, colliding_rooms)
        total_area -= sum(room['size'][0] * room['size'][1] for room in colliding_rooms)

    return total_area

def crossover(parent1, parent2):

    # crossover is the process of combining two parents to create a child
    # ensure that the child has no overlapping rooms

    child = {'rooms': [], 'fitness': 0}

    for room1, room2 in zip(parent1['rooms'], parent2['rooms']):
        if random.random() < 0.5:
            child['rooms'].append(room1)
        else:
            child['rooms'].append(room2)

    # Ensure that the child has at least MIN_NUM_ROOMS rooms
    if len(child['rooms']) < MIN_NUM_ROOMS:
        child['rooms'] += generate_random_rooms(MIN_NUM_ROOMS - len(child['rooms']), external=True)

    return child


def increase_room_size(room, max_width, max_height):

    free_space_to_expand = (max_width - room['position'][0] - room['size'][0], max_height - room['position'][1] - room['size'][1])

    if free_space_to_expand[0] < 0 or free_space_to_expand[1] < 0:
        return room
    
    if free_space_to_expand[0] < free_space_to_expand[1]:
        new_width = min(room['size'][0] + free_space_to_expand[0], max_width)
        new_height = room['size'][1]

    else:
        new_width = room['size'][0]
        new_height = min(room['size'][1] + free_space_to_expand[1], max_height)

    return {'position': room['position'], 'size': (new_width, new_height), 'external': room.get('external', False)}




def mutate(floor_plan, expand_walls=True):
    mutated_plan = floor_plan.copy()

    for room in mutated_plan['rooms']:
        if random.random() < MUTATION_RATE:
            mutation_percentage = random.uniform(-MAX_MUTATION_PERCENTAGE, MAX_MUTATION_PERCENTAGE)
            mutated_room = increase_room_size(room, PLOT_SIZE[0], PLOT_SIZE[1])

            mutated_width = max(min(mutated_room['size'][0] * (1 + mutation_percentage), PLOT_SIZE[0]), MIN_ROOM_SIZE[0])
            mutated_height = max(min(mutated_room['size'][1] * (1 + mutation_percentage), PLOT_SIZE[1]), MIN_ROOM_SIZE[1])

            mutated_room['size'] = (mutated_width, mutated_height)

    if len(mutated_plan['rooms']) < MIN_NUM_ROOMS:
        mutated_plan['rooms'] += generate_random_rooms(NUM_BEDROOMS - len(mutated_plan['rooms']), external=True)

    return {'rooms': mutated_plan['rooms'], 'fitness': 0}

def find_colliding_rooms(target_room, all_rooms):
    return [other_room for other_room in all_rooms if other_room != target_room and rooms_overlap(target_room, other_room)]

def rooms_overlap(room1, room2):
    # Check if two rooms overlap
    x1, y1, w1, h1 = room1['position'][0], room1['position'][1], room1['size'][0], room1['size'][1]
    x2, y2, w2, h2 = room2['position'][0], room2['position'][1], room2['size'][0], room2['size'][1]

    return not (x1 + w1 < x2 or x2 + w2 < x1 or y1 + h1 < y2 or y2 + h2 < y1)

def resolve_collisions(room1, colliding_rooms, expand_walls=True):
    for other_room in colliding_rooms:
        resolve_collision(room1, other_room, expand_walls)

def resolve_collision(room1, room2, expand_walls=True):
    # Resolve a collision between two rooms
    # lessen the size of the room of overlap till its minimum size or no overlap whichever is earlier
    x1, y1, w1, h1 = room1['position'][0], room1['position'][1], room1['size'][0], room1['size'][1]
    x2, y2, w2, h2 = room2['position'][0], room2['position'][1], room2['size'][0], room2['size'][1]

    if x1 < x2:
        x_overlap = x1 + w1 - x2
    else:
        x_overlap = x2 + w2 - x1
    
    if y1 < y2:
        y_overlap = y1 + h1 - y2
    else:
        y_overlap = y2 + h2 - y1

    if x_overlap < y_overlap:
        if x1 < x2:
            room1['size'] = (w1 - x_overlap, h1)
        else:
            room1['size'] = (w1 - x_overlap, h1)
    else:
        if y1 < y2:
            room1['size'] = (w1, h1 - y_overlap)
        else:
            room1['size'] = (w1, h1 - y_overlap)

    if expand_walls:
        room1['size'] = increase_room_size(room1, PLOT_SIZE[0], PLOT_SIZE[1])['size']

    return room1


def genetic_algorithm(num_bedrooms):

    print("Generating initial population...")

    # population is a list of dictionaries
    # each dictionary has keys 'rooms' and 'fitness'
    # so each dictionary represents a floor plan
    population = generate_initial_population(num_bedrooms)

    best_floor_plan = None

    fig, ax = plt.subplots()

    # set constraints for the plot
    ax.set_xlim(0, PLOT_SIZE[0])
    ax.set_ylim(0, PLOT_SIZE[1])

    def update_plot(generation):

        # update the plot with the best floor plan
        nonlocal best_floor_plan
        nonlocal population

        ax.clear()
        ax.set_xlim(0, PLOT_SIZE[0])
        ax.set_ylim(0, PLOT_SIZE[1])

        # for each room
        for room in best_floor_plan['rooms']:
            position = room['position']
            size = room['size']
            edge_color = 'black' if room.get('external', False) else 'r'
            rect = Rectangle((position[0], position[1]), size[0], size[1], linewidth=1, edgecolor=edge_color, facecolor='none')
            ax.add_patch(rect)

        plt.title(f'Generation {generation}, Fitness: {best_floor_plan["fitness"]}')
        plt.draw()

    for generation in range(NUM_GENERATIONS):


        # for each chromosome
        for i in range(POPULATION_SIZE):
            # set the fitness pa
            population[i]['fitness'] = evaluate_fitness(population[i]['rooms'])

        # sort the population by fitness
        # the best floor plan is the one with the highest fitness
        parents = sorted(population, key=lambda x: x['fitness'], reverse=True)[:2]

        # now make a new population
        # by crossing over the parents
        # which are the two best floor plans
        # and then mutating the new floor plans
        new_population = [crossover(parents[0], parents[1]) for _ in range(POPULATION_SIZE)]

        # mutate every floor plan of the new population
        # new population is a list of dictionaries
        # it is created by crossing over the two best floor plans
        new_population = [mutate(floor_plan) for floor_plan in new_population]

        population = new_population

        best_floor_plan = max(population, key=lambda x: x['fitness'])

        update_plot(generation)

    plt.show()
    return best_floor_plan['rooms']

# use pygame to display the floor plan
# 1. create a pygame window
# 2. draw the rooms on the window
# 3. display the window
# 4. wait for the user to close the window
# 5. exit the program

def draw_rooms(rooms, screen):
    for room in rooms:
        position = room['position']
        size = room['size']
        color = (255, 0, 0) if room.get('external', False) else (0, 0, 255)
        pygame.draw.rect(screen, color, (position[0], position[1], size[0], size[1]), 2)


print("Starting Genetic Algorithm...")
best_floor_plan = genetic_algorithm(NUM_BEDROOMS)
print("Genetic Algorithm finished.")
screen = pygame.display.set_mode((PLOT_SIZE[0]*10, PLOT_SIZE[1]*10))
draw_rooms(best_floor_plan, screen)
pygame.display.flip()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
pygame.quit()
print("Best Floor Plan: ", best_floor_plan)