import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

class RoomPlanner(object):
    def __init__(self, PLOT_SIZE=(50, 100), MIN_ROOM_SIZE=(10, 10), NUM_BEDROOMS=2,
                 POPULATION_SIZE=50, NUM_GENERATIONS=500, MUTATION_RATE=2,
                 MAX_MUTATION_PERCENTAGE=0.1, SIZE_INCREASE_FACTOR=1000,
                 COLLISION_RESOLUTION_STEPS=4, MIN_NUM_ROOMS=2,
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

    def generate_zero_array_for_complete_floorplan(self):
        # numpy array to store the population
        # each individual is a 2D array of room coordinates
        # 1 represents a wall, 0 represents empty space
        self.population = np.ones((self.POPULATION_SIZE, self.PLOT_SIZE[0], self.PLOT_SIZE[1]))
        self.new_population = np.ones((self.POPULATION_SIZE, self.PLOT_SIZE[0], self.PLOT_SIZE[1]))
                                       

    def check_if_pixel_covered_by_some_room(self, x, y, room):
        return room[x, y] == 1

    def generate_initial_population_after_checking_pixels(self):
        for i in range(self.POPULATION_SIZE):
            num_rooms = np.random.randint(self.MIN_NUM_ROOMS, self.MIN_NUM_ROOMS + 3)
            for j in range(num_rooms):
                room_size = (np.random.randint(self.MIN_ROOM_SIZE[0], self.PLOT_SIZE[0] // 2),
                             np.random.randint(self.MIN_ROOM_SIZE[1], self.PLOT_SIZE[1] // 2))
                room_x = np.random.randint(0, self.PLOT_SIZE[0] - room_size[0])
                room_y = np.random.randint(0, self.PLOT_SIZE[1] - room_size[1])
                # Set 0 to represent empty space and 1 to represent walls
                self.population[i, room_x:room_x + room_size[0], room_y:room_y + room_size[1]] = 0
                self.population[i, room_x, room_y:room_y + room_size[1]] = 1
                            
    def calculate_fitness(self):
        # fitness is 
        # total area of all the rooms in the floor plan
        # divided by the total area of the floor plan
        self.fitness = np.zeros(self.POPULATION_SIZE)
        for i in range(self.POPULATION_SIZE):
            self.fitness[i] = np.sum(self.population[i]) / (self.PLOT_SIZE[0] * self.PLOT_SIZE[1])

    def select_parents(self):
        # select the parents for the next generation
        self.parents = np.zeros((2, self.PLOT_SIZE[0], self.PLOT_SIZE[1]))
        for i in range(2):
            self.parents[i] = self.population[np.random.choice(range(self.POPULATION_SIZE), p=self.fitness / np.sum(self.fitness))]
        return self.parents

    def crossover(self):
        # crossover the parents to create a child
        self.child = np.zeros((self.PLOT_SIZE[0], self.PLOT_SIZE[1]))
        for i in range(self.PLOT_SIZE[0]):
            for j in range(self.PLOT_SIZE[1]):
                self.child[i, j] = self.parents[np.random.randint(2), i, j]
        return self.child

    def mutate(self):
        # mutate the child
        for i in range(self.PLOT_SIZE[0]):
            for j in range(self.PLOT_SIZE[1]):
                if np.random.randint(100) < self.MUTATION_RATE:
                    self.child[i, j] = 1 - self.child[i, j]
        return self.child

    def resolve_collisions(self):
        # resolve collisions in the child
        for i in range(self.COLLISION_RESOLUTION_STEPS):
            for j in range(self.PLOT_SIZE[0]):
                for k in range(self.PLOT_SIZE[1]):
                    if self.child[j, k] == 1:
                        if j > 0 and k > 0 and j < self.PLOT_SIZE[0] - 1 and k < self.PLOT_SIZE[1] - 1:
                            if self.child[j - 1, k] == 0 and self.child[j + 1, k] == 0 and self.child[j, k - 1] == 0 and self.child[j, k + 1] == 0:
                                self.child[j, k] = 0
        return self.child

    def generate_next_generation(self):
        # generate the next generation
        for i in range(self.POPULATION_SIZE):
            self.parents = self.select_parents()
            self.child = self.crossover()
            self.child = self.mutate()
            self.child = self.resolve_collisions()
            self.new_population[i] = self.child

    def plot_floor_plan(self, floor_plan):
        # plot the floor plan
        fig, ax = plt.subplots()
        for i in range(self.PLOT_SIZE[0]):
            for j in range(self.PLOT_SIZE[1]):
                if floor_plan[i, j] == 1:
                    ax.add_patch(Rectangle((i, j), 1, 1, facecolor='black'))
                else:
                    ax.add_patch(Rectangle((i, j), 1, 1, facecolor='white', edgecolor='black'))
        ax.set_xlim(0, self.PLOT_SIZE[0])
        ax.set_ylim(0, self.PLOT_SIZE[1])
        plt.show()

    def genetic_algorithm(self):
    
        self.generate_zero_array_for_complete_floorplan()
        self.generate_initial_population_after_checking_pixels()
        for generation in range(self.NUM_GENERATIONS):
            self.calculate_fitness()
            self.parents = self.select_parents()
            self.child = self.crossover()
            self.child = self.mutate()
            self.child = self.resolve_collisions()
            self.new_population[generation] = self.child
            self.population = self.new_population
            self.plot_floor_plan(self.population[0])

def main():

    room_planner = RoomPlanner()
    room_planner.genetic_algorithm()

if __name__ == '__main__':
    main()
        