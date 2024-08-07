import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from test import population as population_final


class RoomPlanner(object):
    def __init__(self, PLOT_SIZE=(50, 100), MIN_ROOM_SIZE=(10, 10), NUM_BEDROOMS=2,
                 POPULATION_SIZE=50, NUM_GENERATIONS=500, MUTATION_RATE=2,
                 MAX_MUTATION_PERCENTAGE=0.1, SIZE_INCREASE_FACTOR=1000,
                 COLLISION_RESOLUTION_STEPS=10, MIN_NUM_ROOMS=2,
                 GRID_SIZE=(10, 10), MIN_AREA=10):
        self.PLOT_SIZE = PLOT_SIZE
        self.MIN_ROOM_SIZE = MIN_ROOM_SIZE
        self.NUM_BEDROOMS = NUM_BEDROOMS
        self.POPULATION_SIZE = POPULATION_SIZE
        self.NUM_GENERATIONS = NUM_GENERATIONS
        self.MUTATION_RATE = MUTATION_RATE
        self.MAX_MUTATION_PERCENTAGE = MAX_MUTATION_PERCENTAGE
        self.SIZE_INCREASE_FACTOR = SIZE_INCREASE_FACTOR
        self.COLLISION_RESOLUTION_STEPS = COLLISION_RESOLUTION_STEPS
        self.MIN_NUM_ROOMS = MIN_NUM_ROOMS
        self.GRID_SIZE = GRID_SIZE
        self.MIN_AREA = MIN_AREA
        self.BEDROOM_SIZE = (10, 10)
        self.KITCHEN_SIZE = (5, 8)
        self.APPROXIMATION_FACTOR = 0.5
        self.MAX_XY_RATIO = 1.5
        self.MIN_XY_RATIO = 1
        self.MIN_LIVING_ROOM_SIZE = (20, 20)

    def generate_initial_population(self):
    
        population = [] # 1st to last 


        for _ in range(self.POPULATION_SIZE):
            population.append(self.generate_random_rooms())
        return population
    
    def generate_bedrooms(self, floor_plan):
        bedrooms = []
        for i in range(self.NUM_BEDROOMS-2):
            print(f"Generating bedroom {i + 1}...")
            bedroom_name = f"Bedroom {i + 1}"
            bedrooms.append(self.generate_proper_bedroom(floor_plan, bedroom_name, bedrooms))
        return bedrooms
    
    
    def generate_proper_bedroom(self, floor_plan, bedroom_name, bedrooms):
        # take into consideration the minimum size of the bedroom
        # and the approximation factor
        bedroom = {'name': bedroom_name, 'position': (0, 0), 'size': (0, 0)}
        
        while bedroom['size'][0] < self.BEDROOM_SIZE[0] or bedroom['size'][1] < self.BEDROOM_SIZE[1]:
            bedroom['size'] = (np.random.randint(1, self.PLOT_SIZE[0]), np.random.randint(1, self.PLOT_SIZE[1]))
        corner_clear = {'top_left': True, 'top_right': True, 'bottom_left': True, 'bottom_right': True}
        existing_room_cords = {}
        corner = np.random.choice(['top_left', 'top_right', 'bottom_left', 'bottom_right'])
        if corner == 'top_left':
            bedroom['position'] = (0, 0)
            corner_clear['top_left'] = False
        elif corner == 'top_right':
            bedroom['position'] = (self.PLOT_SIZE[0] - bedroom['size'][0], 0)
            corner_clear['top_right'] = False
        elif corner == 'bottom_left':
            bedroom['position'] = (0, self.PLOT_SIZE[1] - bedroom['size'][1])
            corner_clear['bottom_left'] = False
        else:
            bedroom['position'] = (self.PLOT_SIZE[0] - bedroom['size'][0], self.PLOT_SIZE[1] - bedroom['size'][1])
            corner_clear['bottom_right'] = False
        if self.check_collision(floor_plan, bedroom['position'], bedroom['size']):
            self.resolve_collisions(floor_plan, bedroom['position'], bedroom['size'])
            return bedrooms.append(bedroom)
        return bedrooms.append(bedroom)
    
    
    def generate_narrow_kitchen(self, floor_plan, bedrooms):
    
        kitchen = {'name': 'Kitchen', 'position': (0, 0), 'size': (5,8)}

        while kitchen['size'][0] < self.KITCHEN_SIZE[0] or kitchen['size'][1] < self.KITCHEN_SIZE[1]:
            kitchen['size'] = (np.random.randint(1, self.PLOT_SIZE[0]), np.random.randint(1, self.PLOT_SIZE[1]))
        corner_clear = {'top_left': True, 'top_right': True, 'bottom_left': True, 'bottom_right': True}

        corner = np.random.choice(['top_left', 'top_right', 'bottom_left', 'bottom_right'])
        if corner == 'top_left':
            kitchen['position'] = (0, 0)
            corner_clear['top_left'] = False
        elif corner == 'top_right':
            kitchen['position'] = (self.PLOT_SIZE[0] - kitchen['size'][0], 0)
            corner_clear['top_right'] = False
        elif corner == 'bottom_left':
            kitchen['position'] = (0, self.PLOT_SIZE[1] - kitchen['size'][1])
            corner_clear['bottom_left'] = False
        else:
            kitchen['position'] = (self.PLOT_SIZE[0] - kitchen['size'][0], self.PLOT_SIZE[1] - kitchen['size'][1])
            corner_clear['bottom_right'] = False
        if self.check_collision(floor_plan, kitchen['position'], kitchen['size']):
            self.resolve_collisions(floor_plan, kitchen['position'], kitchen['size'])
            return kitchen
        return None
    
    
    def generate_kitchen(self, floor_plan):
        kitchen = {'position': (0, 0), 'size': (0, 0)}
        while kitchen['size'][0] < self.KITCHEN_SIZE[0] or kitchen['size'][1] < self.KITCHEN_SIZE[1]:
            kitchen['size'] = (np.random.randint(1, self.PLOT_SIZE[0]), np.random.randint(1, self.PLOT_SIZE[1]))
        corner_clear = {'top_left': True, 'top_right': True, 'bottom_left': True, 'bottom_right': True}
        corner = np.random.choice(['top_left', 'top_right', 'bottom_left', 'bottom_right'])
        if corner == 'top_left':
            kitchen['position'] = (0, 0)
            corner_clear['top_left'] = False
        elif corner == 'top_right':
            kitchen['position'] = (self.PLOT_SIZE[0] - kitchen['size'][0], 0)
            corner_clear['top_right'] = False
        elif corner == 'bottom_left':
            kitchen['position'] = (0, self.PLOT_SIZE[1] - kitchen['size'][1])
            corner_clear['bottom_left'] = False
        else:
            kitchen['position'] = (self.PLOT_SIZE[0] - kitchen['size'][0], self.PLOT_SIZE[1] - kitchen['size'][1])
            corner_clear['bottom_right'] = False
        if self.check_collision(floor_plan, kitchen['position'], kitchen['size']):
            self.resolve_collisions(floor_plan, kitchen['position'], kitchen['size'])
            return kitchen
        return None
    

    def generate_random_rooms(self):
        print("gen chage")

        floor_plan = np.zeros(self.PLOT_SIZE)

        rooms = {'rooms': [], 'fitness': 0}

        corner_clear = {'top_left': True, 'top_right': True, 'bottom_left': True, 'bottom_right': True}
        room_cords = {}
        living_room,corner,room_cords = self.generate_living_room(floor_plan,corner_clear,room_cords)
        rooms['rooms'].append(living_room)

        rooms['rooms'].append(self.generate_door(floor_plan, living_room,corner,room_cords)[0])
        for i in range(self.MIN_NUM_ROOMS):
            room_name = f"Room_{i + 1}"
            room = self.generate_random_room(floor_plan, room_name)
            if room is not None:
                rooms['rooms'].append(room)

            # fitness
            rooms['fitness'] = self.calculate_area_fitness(rooms['rooms'])
        return rooms
    
    

    def generate_living_room(self, floor_plan,corner_clear,room_cords):

        living_room = {'name': 'Living Room', 'position': (0, 0), 'size': (40, 40)}

        while (living_room['size'][0] <= self.MIN_LIVING_ROOM_SIZE[0] or living_room['size'][1] <= self.MIN_LIVING_ROOM_SIZE[1]) and (living_room['size'][0] / living_room['size'][1] < self.MIN_XY_RATIO or living_room['size'][0] / living_room['size'][1] > self.MAX_XY_RATIO):
            living_room['size'] = (np.random.randint(1, self.PLOT_SIZE[0]), np.random.randint(1, self.PLOT_SIZE[1]))

        available = []
        if corner_clear['top_left']:
            available.append('top_left')
        if corner_clear['top_right']:
            available.append('top_right')
        if corner_clear['bottom_left']:
            available.append('bottom_left')
        if corner_clear['bottom_right']:
            available.append('bottom_right')

        corner = np.random.choice(available)
        if corner == 'top_left':
            living_room['position'] = (0, 0)
            corner_clear['top_left'] = False
        elif corner == 'top_right':
            living_room['position'] = (self.PLOT_SIZE[0] - living_room['size'][0], 0)
            corner_clear['top_right'] = False
        elif corner == 'bottom_left':
            living_room['position'] = (0, self.PLOT_SIZE[1] - living_room['size'][1])
            corner_clear['bottom_left'] = False
        else:
            living_room['position'] = (self.PLOT_SIZE[0] - living_room['size'][0], self.PLOT_SIZE[1] - living_room['size'][1])
            corner_clear['bottom_right'] = False

        if self.check_collision(floor_plan, living_room['position'], living_room['size']):
            self.resolve_collisions(floor_plan, living_room['position'], living_room['size'])
            # add living room with its co-ordinates to the room_cords
            room_cords['living_room'] = living_room['position']
            return living_room,corner,room_cords
        return None


    def generate_random_room(self, floor_plan, room_name):
        # generate bedrroms and kitchen
        bedrooms = self.generate_bedrooms(floor_plan)
        rooms = bedrooms
        for room in rooms:
            if self.check_collision(floor_plan, room['position'], room['size']):
                self.resolve_collisions(floor_plan, room['position'], room['size'])
                return room
        return None
    
    def generate_door(self, floor_plan, room,corner,room_cords):
        # a quarter circle at one of the corners
        if corner == 'top_left':
            door_position = (room['position'][0], room['position'][1])
        elif corner == 'top_right':
            door_position = (room['position'][0] + room['size'][0], room['position'][1])

        elif corner == 'bottom_left':
            door_position = (room['position'][0], room['position'][1] + room['size'][1])

        else:
            door_position = (room['position'][0] + room['size'][0], room['position'][1] + room['size'][1])
 

        if corner == 'top_left':
            door = {'name':'door','position': (room['position'][0], room['position'][1]), 'size': (5, 5)}
        elif corner == 'top_right':
            door = {'name':'door','position': (room['position'][0] + room['size'][0], room['position'][1]), 'size': (-5, 5)}
        elif corner == 'bottom_left':
            door = {'name':'door','position': (room['position'][0], room['position'][1] + room['size'][1]), 'size': (5, -5)}
        else:
            door = {'name':'door','position': (room['position'][0] + room['size'][0], room['position'][1] + room['size'][1]), 'size': (-5,-5)}
        if self.check_collision(floor_plan, door['position'], door['size']):
            self.resolve_collisions(floor_plan, door['position'], door['size'])
            room_cords['door'] = door['position']
            return door,room_cords
        return None
    

    def calculate_area_fitness(self, floor_plan):
        total_area = 0
        # high penalty for overlapping rooms
    
        for room in floor_plan:
            total_area += room['size'][0] * room['size'][1]
            colliding_rooms = self.find_colliding_rooms(room, floor_plan)
            if colliding_rooms:
                total_area -= 100 * sum(self.overlap_area(room, colliding_room) for colliding_room in colliding_rooms)
                total_area = 0
        return total_area

    def overlap_area(self, room1, room2):
        x_overlap = max(0, min(room1['position'][0] + room1['size'][0], room2['position'][0] + room2['size'][0]) - max(room1['position'][0], room2['position'][0]))
        y_overlap = max(0, min(room1['position'][1] + room1['size'][1], room2['position'][1] + room2['size'][1]) - max(room1['position'][1], room2['position'][1]))
        return x_overlap * y_overlap

    def crossover(self, parent1, parent2):
        # change the logic
        offspring1 = {'rooms': [], 'fitness': 0}
        offspring2 = {'rooms': [], 'fitness': 0}
        for room in parent1['rooms']:
            if np.random.rand() < 0.5:
                offspring1['rooms'].append(room)
            else:
                offspring2['rooms'].append(room)
        for room in parent2['rooms']:
            if np.random.rand() > 0.5:
                offspring1['rooms'].append(room)
            else:
                offspring2['rooms'].append(room)
        return offspring1, offspring2

    def mutate(self, floor_plan):
        mutated_plan = floor_plan.copy()
        for room in mutated_plan['rooms']:

            # control if room has to be mutated
            if np.random.rand() < self.MUTATION_RATE:

                # if yes,
                # then by how much it has to be mutated
                # room cannot be mutated to a size less than the minimum room size and more than the plot size
                room['size'] = (min(room['size'][0] + self.SIZE_INCREASE_FACTOR, self.PLOT_SIZE[0]),
                                min(room['size'][1] + self.SIZE_INCREASE_FACTOR, self.PLOT_SIZE[1]))
                

        return mutated_plan
    
    def check_collision(self, floor_plan, position, size):
        x, y = position
        width, height = size
        return np.all(floor_plan[y:y + height, x:x + width] == 0)
    
    def resolve_collisions(self, floor_plan, position, size):
        # reduce the wall size till it fits
        # and till collision is resolved
        x, y = position
        width, height = size
        while not self.check_collision(floor_plan, (x, y), (width, height)):
            if width > height:
                width -= 1
            else:
                height -= 1
        return (x, y), (width, height)
    
    def plot_rooms(self, rooms):
        fig, ax = plt.subplots()
        border = Rectangle((0, 0), self.PLOT_SIZE[0], self.PLOT_SIZE[1], fill=False, color='brown')
        ax.add_patch(border)
        # rooms = [{'rooms':[{'name':'Living Room','position':(0,0),'size':(40,40)},{'name':'door','position':(0,0),'size':(5,5)}],'fitness':1600}]
        rooms1 = rooms['rooms']
        for room in rooms1:
                if(room==None):
                    continue
                position = room['position']
                size = room['size']
                color = 'black' if room.get('external', False) else 'brown'
                if room['name'] == 'Door':
                    rect = plt.Circle((position[0], position[1]), 5, color='blue', fill=True)
                else:
                    rect = Rectangle((position[0], position[1]), size[0], size[1], linewidth=5, edgecolor=color, facecolor='none')
                ax.add_patch(rect)

                room_name = room['name']
                room_center = (position[0] + size[0] / 2, position[1] + size[1] / 2)
                ax.text(room_center[0], room_center[1], room_name, fontsize=12, ha='center', va='center')

        ax.set_xlim(0, self.PLOT_SIZE[0])
        ax.set_ylim(0, self.PLOT_SIZE[1])
        ax.set_aspect('equal', adjustable='box')
        plt.show()

        # for room in rooms:
        #     # print("meri room")
        #     # print(room)
        #     # if(room['name'] == 'Door'):
        #     #     # plot circles for doors
        #     #     print("done")
        #     #     position = room['position']
        #     #     size = room['size']
        #     #     ax.add_patch(plt.Circle((position[0], position[1]), 5, color='blue'))
        #     #     continue
        #     rooms1 = room['rooms']
        #     for room in rooms1:
        #         if(room==None):
        #             continue
        #         position = room['position']
        #         size = room['size']
        #         color = 'black' if room.get('external', False) else 'brown'
        #         if room['name'] == 'Door':
        #             rect = plt.Circle((position[0], position[1]), 5, color='blue', fill=True)
        #         else:
        #             rect = Rectangle((position[0], position[1]), size[0], size[1], linewidth=5, edgecolor=color, facecolor='none')
        #         ax.add_patch(rect)

        #         room_name = room['name']
        #         room_center = (position[0] + size[0] / 2, position[1] + size[1] / 2)
        #         ax.text(room_center[0], room_center[1], room_name, fontsize=12, ha='center', va='center')

        #     ax.set_xlim(0, self.PLOT_SIZE[0])
        #     ax.set_ylim(0, self.PLOT_SIZE[1])
        #     ax.set_aspect('equal', adjustable='box')
        #     plt.show()


    def plot_room_boundaries(self, rooms):
        fig, ax = plt.subplots()
        border = Rectangle((0, 0), self.PLOT_SIZE[0], self.PLOT_SIZE[1], fill=False, color='brown')
        ax.add_patch(border)
        for room in rooms:
            position = room['position']
            size = room['size']
            ax.add_patch(Rectangle(position, size[0], size[1], fill=False, color='brown'))
        ax.set_xlim(0, self.PLOT_SIZE[0])
        ax.set_ylim(0, self.PLOT_SIZE[1])
        plt.show()


    def find_colliding_rooms(self, room, floor_plan):
        colliding_rooms = []
        for other_room in floor_plan:
            if room != other_room:
                if (room['position'][0] < other_room['position'][0] + other_room['size'][0] and
                    room['position'][0] + room['size'][0] > other_room['position'][0] and
                    room['position'][1] < other_room['position'][1] + other_room['size'][1] and
                    room['position'][1] + room['size'][1] > other_room['position'][1]):
                    colliding_rooms.append(other_room)
        return colliding_rooms
    
    def resolve_collision(self, room1, room2, expand_walls=True):
        x1, y1, w1, h1 = room1['position'][0], room1['position'][1], room1['size'][0], room1['size'][1]
        x2, y2, w2, h2 = room2['position'][0], room2['position'][1], room2['size'][0], room2['size'][1]
        x_overlap = max(0, min(x1 + w1, x2 + w2) - max(x1, x2))
        y_overlap = max(0, min(y1 + h1, y2 + h2) - max(y1, y2))
        if x_overlap < y_overlap:
            room1['size'] = (w1 - x_overlap, h1)
        else:
            room1['size'] = (w1, h1 - y_overlap)
        if expand_walls:
            room1['size'] = self.increase_room_size(room1, self.PLOT_SIZE[0], self.PLOT_SIZE[1])['size']
        return room1
    
    def increase_room_size(self, room, max_width, max_height):
        position = room['position']
        size = room['size']
        available_width = max_width - position[0] - size[0]
        available_height = max_height - position[1] - size[1]
        if available_width > 0 and available_height > 0:
            size = (min(size[0] + available_width, max_width), min(size[1] + available_height, max_height))
        return {'position': position, 'size': size}
    
    def genetic_algorithm(self):

        print("Generating initial population...")

        population = self.generate_initial_population()

        # -----------------  Genetic Algorithm -----------------

        best_floor_plan = None


        fig, ax = plt.subplots()
        ax.set_xlim(0, self.PLOT_SIZE[0])
        ax.set_ylim(0, self.PLOT_SIZE[1])


        for generation in range(self.NUM_GENERATIONS):
            print(f"Generation {generation + 1}/{self.NUM_GENERATIONS}")


            for floor_plan in population:

                # plan to add fitness to the floor plan
                if best_floor_plan is None or floor_plan['fitness'] > best_floor_plan['fitness']:
                    best_floor_plan = floor_plan
                else:
                    
                    
                 best_floor_plan = best_floor_plan

                if best_floor_plan['fitness'] == np.prod(self.PLOT_SIZE):
                    return best_floor_plan
                
                # if generation % 10 == 0:
                #     self.update_plot(best_floor_plan, ax)
                #     plt.pause(0.1)
                #     plt.draw()

                # if generation % 100 == 0:
                #     print(f"Generation {generation + 1}/{self.NUM_GENERATIONS}, Fitness: {best_floor_plan['fitness']}")

            self.update_plot(best_floor_plan, ax)
            plt.pause(0.1)
            plt.draw()
            parents = self.select_parents(population)
            offspring = []
            for i in range(0, len(parents), 2):
                if(i+1 >= len(parents)):
                    break
                offspring1, offspring2 = self.crossover(parents[i], parents[i + 1])
                offspring.append(self.mutate(offspring1))
                offspring.append(self.mutate(offspring2))

            # now population is the parents and the offspring
            population = parents + offspring


            # back to loop
            # population will keep on increasing


        return best_floor_plan
    
    def select_parents(self, population):

        fitnesses = [floor_plan['fitness'] for floor_plan in population]
        # sort the population based on fitness
        population = [x for _, x in sorted(zip(fitnesses, population), key=lambda pair: pair[0], reverse=True)]

        # choose only the top 10% or 2 parents whichever is greater
        num_parents = max(int(0.1 * self.POPULATION_SIZE), 2)
        parents = population[:num_parents]
        return parents
    
    def update_plot(self, best_floor_plan, ax):
        ax.clear()
        ax.set_xlim(0, self.PLOT_SIZE[0])
        ax.set_ylim(0, self.PLOT_SIZE[1])
        for room in best_floor_plan['rooms']:
            position = room['position']
            size = room['size']
            edge_color = 'BLACK' if room.get('external', False) else 'BROWN'
            rect = Rectangle((position[0], position[1]), size[0], size[1], linewidth=5, edgecolor=edge_color, facecolor='none')
            # ax.add_patch(rect)
        # plt.title(f'Generation {generation}, Fitness: {best_floor_plan["fitness"]}')
        plt.draw()
        return ax
    
   
    def remove_narrow_rooms(self, rooms):
        for room in rooms:
            if room['size'][0] < self.MIN_ROOM_SIZE[0] or room['size'][1] < self.MIN_ROOM_SIZE[1]:
                rooms.remove(room)
        return rooms
    
    def main(self):
        best_floor_plan = self.genetic_algorithm()
        return best_floor_plan['rooms']
    
    def draw_rooms_pygame(self, rooms, screen):
        for room in rooms:
            position = room['position']
            size = room['size']
            color = (0, 0, 0) if room.get('external', False) else (0, 0, 0)
            pygame.draw.rect(screen, color, (position[0], position[1], size[0], size[1]), 5)
        return screen
    
    def draw_rooms(self, rooms, screen):
        for room in rooms:
            position = room['position']
            size = room['size']
            color = (0, 0, 0) if room.get('external', False) else (0, 0, 0)
            pygame.draw.rect(screen, color, (position[0], position[1], size[0], size[1]), 5)
        return screen
    
    def draw_rooms(self, rooms, screen):
        for room in rooms:
            position = room['position']
            size = room['size']
            color = (0, 0, 0) if room.get('external', False) else (0, 0, 0)
            pygame.draw.rect(screen, color, (position[0], position[1], size[0], size[1]), 5)
        return screen
    
    def boundary_for_walls(self, rooms):
        for room in rooms:
            if room['position'][0] == 0 or room['position'][1] == 0:
                room['external'] = True
        return rooms
    
    def draw_rooms(self, rooms, screen):
        for room in rooms:
            position = room['position']
            size = room['size']
            color = (0, 0, 0) if room.get('external', False) else (0, 0, 0)
            pygame.draw.rect(screen, color, (position[0], position[1], size[0], size[1]), 5)
        return screen
    
    def draw_room_boundaries(self, rooms, screen):
        # draw lines for each room
        # blue lines for external walls
        # black lines for internal walls

        for room in rooms:
            position = room['position']
            size = room['size']
            if room.get('external', False):
                color = (0, 0, 255)
            else:
                color = (0, 0, 0)
            pygame.draw.line(screen, color, (position[0], position[1]), (position[0] + size[0], position[1]), 5)
            pygame.draw.line(screen, color, (position[0], position[1]), (position[0], position[1] + size[1]), 5)
            pygame.draw.line(screen, color, (position[0] + size[0], position[1]), (position[0] + size[0], position[1] + size[1]), 5)
            pygame.draw.line(screen, color, (position[0], position[1] + size[1]), (position[0] + size[0], position[1] + size[1]), 5)

if __name__ == '__main__':
    while True:
        planner = RoomPlanner()
        population = planner.generate_initial_population()
        print(population)
        print("Initial population generated")
        print("Plotting rooms...")
        print(population)

        population = planner.genetic_algorithm()
        print(population)

        planner.plot_rooms(population)
    # offspring1, offspring2 = planner.crossover(population[0], population[1])
    # planner.plot_rooms(offspring1['rooms'])
    # planner.plot_rooms(offspring2['rooms'])
    # mutated_plan = planner.mutate(population[0])
    # planner.plot_rooms(mutated_plan['rooms'])
    # best_floor_plan = planner.genetic_algorithm()
    # planner.plot_rooms(best_floor_plan['rooms'])