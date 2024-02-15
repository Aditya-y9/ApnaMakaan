import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

class RoomPlanner(object):
    def __init__(self, PLOT_SIZE=(50, 100), MIN_ROOM_SIZE=(10, 10), NUM_BEDROOMS=2,
                 POPULATION_SIZE=50, NUM_GENERATIONS=50, MUTATION_RATE=2,
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

    def generate_initial_population(self):
        # numpy array to store the population
        # each individual is a 2D array of room coordinates
        # 1 represents a room, 0 represents empty space
        self.population = np.zeros((self.POPULATION_SIZE, self.PLOT_SIZE[0], self.PLOT_SIZE[1]))
        self.new_population = np.zeros((self.POPULATION_SIZE, self.PLOT_SIZE[0], self.PLOT_SIZE[1]))

        for i in range(self.POPULATION_SIZE):
            num_rooms = np.random.randint(self.MIN_NUM_ROOMS, self.MIN_NUM_ROOMS + 3)
            for j in range(num_rooms):
                room_size = (np.random.randint(self.MIN_ROOM_SIZE[0], self.PLOT_SIZE[0] // 2),
                             np.random.randint(self.MIN_ROOM_SIZE[1], self.PLOT_SIZE[1] // 2))
                room_x = np.random.randint(0, self.PLOT_SIZE[0] - room_size[0])
                room_y = np.random.randint(0, self.PLOT_SIZE[1] - room_size[1])
                self.population[i, room_x:room_x + room_size[0], room_y:room_y + room_size[1]] = 1

    def calculate_fitness(self):
        # calculate the fitness of each individual in the population
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
            for j in range(1, self.PLOT_SIZE[0] - 1):
                for k in range(1, self.PLOT_SIZE[1] - 1):
                    if self.child[j, k] == 1:
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
        self.population = self.new_population

    def plot_population(self):
            # plot the population
            fig, ax = plt.subplots()
            for i in range(self.POPULATION_SIZE):
                for j in range(self.PLOT_SIZE[0]):
                    for k in range(self.PLOT_SIZE[1]):
                        if self.population[i, j, k] == 1:
                            rect = Rectangle((k, j), 1, 1, facecolor='black', edgecolor='black', linewidth=1)
                            ax.add_patch(rect)
            plt.xlim(0, self.PLOT_SIZE[1])
            plt.ylim(0, self.PLOT_SIZE[0])
            plt.gca().set_aspect('equal', adjustable='box')  # Make the aspect ratio of the plot equal
            plt.show()

    def run(self):
        # run the genetic algorithm
        print('Running genetic algorithm...')
        self.generate_initial_population()
        print('Initial population generated...')
        for i in range(self.NUM_GENERATIONS):
            self.calculate_fitness()
            self.generate_next_generation()
            self.plot_population()

if __name__ == '__main__':
    room_planner = RoomPlanner()
    room_planner.run()