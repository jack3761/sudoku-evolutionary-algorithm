import time
import numpy as np
import random
import copy

#Reads grid from the file which must be in the same directory
#Returns the initial grid to be used and indexes of all of the fixed values
def read_grid(grid_name):
    grid_file = open(grid_name, "r")
    grid = []
    fixed = set()
    pos = 0
    #Converts grid into a list to be read and printed throughot program
    for line in grid_file:
        for x in line:
            if x.isdigit():
                grid.append(int(x))
                fixed.add(pos)
                pos += 1
            elif x == ".":
                grid.append(0)
                pos+=1
    return grid, fixed

#Used to print the list into a readable sudoku grid
def print_grid(grid):
    for i in range(len(grid)):
        if i%9 == 0:
            print("")
        if i%27 == 0:
            print("")
        if i%3 == 0 and i%9 != 0:
            print(" ", end='')
        print(str(grid[i]) + " ", end='')    
        
#Fitness function returns the total amount of unique numbers, max being 243
def fitness(grid):
    f, j, k = 0,0,0
    grid_2d = np.array(grid).reshape(9,9)
    for i in range(9):
        #Counts unique characters in each row
        x = len(set(grid_2d[i]))
        #Counts unique characters in each column
        y = len(set(grid_2d[:, i]))
        #Counts unique characters in each column
        z = len(set([grid_2d[j,k], grid_2d[j,k+1], grid_2d[j,k+2], grid_2d[j+1,k], grid_2d[j+1,k+1], grid_2d[j+1,k+2], grid_2d[j+2,k], grid_2d[j+2,k+1], grid_2d[j+2,k+2]]))
        f += x + y + z
        k += 3
        if k%9 == 0:
            j += 3
            k = 0

    #Aiming for an f of 243
    return f
        
#Initialises each individual in the population, returning its grid
def init_ind(grid):
    new_grid = []
    #For each row    
    found_nums = set()
    for i in range(9):
        #Define next row
        row = grid[i*9:(i*9)+9]
        
        found_nums.clear()

        #Add fixed numbers to set to avoid duplicates
        for j in range(len(row)):
            if row[j] != 0:
                found_nums.add(row[j])        

        for j in range(len(row)):
            found = False
            #Change number until it's unique
            if row[j] == 0:                
                found = False
                while not found:
                    rand = random.randint(1,9)
                    #Check to see if generated number is already in the row
                    if rand not in found_nums:
                        row[j] = rand
                        found_nums.add(rand)
                        found = True
        new_grid.extend(row)
    return new_grid

#Creates the population, returns a list of all of the individuals initialised
def create_pop(grid, pop_size):
    population = []
    for i in range(pop_size):
        population.append(init_ind(copy.copy(grid)))
    return population

#Main evolve function
#Runs until either a successful solution is found (fitness = 243) or there have been 100 generations
#Adjustable kill_percentage and mutation_rate parameters
#Returns the generation reached and the highest fitness at that generation
def evolve(start_grid, pop_size, fixed, kill_percentage = 0.8, mutation_rate = 0.4):
    #Create starting population
    population = create_pop(start_grid, pop_size)
    population.sort(key=fitness, reverse=True)

    #Comment out when testing
    print("Gen 0: " + str(fitness(population[0])))
    finished = False
    i = 0
    while not finished:
        #Remove all individuals after the 'kill index' so only the best are left
        kill_index = int(pop_size - pop_size * kill_percentage)
        del population[kill_index:]
        while len(population) < pop_size :
            #Parents are random individuals from the remaining in the population
            parent1 = random.randint(0, kill_index -1)
            parent2 = random.randint(0, kill_index -1)

            #Cannot have two of the same parent
            if parent1 == parent2:
                continue

            #Randomly select which crossover function to use
            if random.random() > 0.5:
                child = crossover1(population[parent1], population[parent2])
            else:
               child = crossover2(population[parent1], population[parent2])

            #Randomly decide to mutate or not
            if random.random() < mutation_rate:
                child = mutate(child, fixed)

            #Add child to population
            population.append(child)
        
        #Sort the list in order of highest to lowest fitness
        population.sort(key=fitness, reverse=True)
        i += 1

        #Comment this out for testing purposes
        print("Gen " + str(i) + ": " + str(fitness(population[0])))
        
        #Stop if termination condition is met
        if fitness(population[0]) == 243 or i == 100:
            finished = True
    
    #Prints grid of solution
    #Comment out for testing purposes
    print_grid(population[0])
    return i, fitness(population[0])
        
#Mutate function, returns child after mutations are applied
def mutate(child, fixed):
    #Run through each row in the child
    for i in range(9):
        #Randomly decide whether a swap will be made
        if random.random() < 0.1:
            swap1 = random.randint(0,8) + i*9
            swap2 = random.randint(0,8) + i*9
            #Ensure that it is not the same number or a fixed number
            if swap1 in fixed or swap2 in fixed:
                continue
            else:
                temp = child[swap1]
                child[swap1] = child[swap2]
                child[swap2] = temp

    return child

#Create child that is the same as one parent with a row swapped from another
def crossover1(parent1, parent2):
    parent1_2d = np.array(parent1).reshape(9,9)
    parent2_2d = np.array(parent2).reshape(9,9)

    #Randomly select which row to swap
    row_swap = random.randint(0,8)

    child = parent1_2d
    child[row_swap] = parent2_2d[row_swap]
    return child.reshape(-1)

#Create child that is the same as one parent with all rows after index from other parent
def crossover2(parent1, parent2):
    parent1_2d = np.array(parent1).reshape(9,9)
    parent2_2d = np.array(parent2).reshape(9,9)

    #Randomly select which row to start swapping from
    row_swap = random.randint(0,8)

    child = parent1_2d
    for i in range(row_swap):
        child[i] = parent2_2d[i]

    return child.reshape(-1)

#Runs the evolution program with the parameters given
#Returns the results from evolve() so it can be used in tests
def run(population_size, grid_name, kill_percentage = 0.8, mutation_rate = 0.4):
    x = read_grid(grid_name)
    start_grid = x[0]
    fixed = x[1]
    population_size = population_size
    return(evolve(start_grid, population_size, fixed, kill_percentage, mutation_rate))

#Testing the different population sizes to find what can reach a successful solution
def test_pop_size():    
    #Population 10
    gen_reached = []
    print("Testing: 10")
    start_time = time.time()
    for i in range(5):
        gen_reached.append(run(10, "Grid1.ss"))
    for i in range(5):
        gen_reached.append(run(10, "Grid2.ss"))
    for i in range(5):
        gen_reached.append(run(10, "Grid3.ss"))
    print("Time taken: " + str(round(time.time()-start_time, 3)) + " seconds")
    print(gen_reached)
    gen_reached.clear()
    start_time = time.time()

    print("Testing: 100")
    for i in range(5):
        gen_reached.append(run(100, "Grid1.ss"))
    for i in range(5):
        gen_reached.append(run(100, "Grid2.ss"))
    for i in range(5):
        gen_reached.append(run(100, "Grid3.ss"))
    print("Time taken: " + str(round(time.time()-start_time, 3)) + " seconds")
    print(gen_reached)
    gen_reached.clear()
    start_time = time.time()

    print("Testing: 1000")
    for i in range(5):
        gen_reached.append(run(1000, "Grid1.ss"))
    for i in range(5):
        gen_reached.append(run(1000, "Grid2.ss"))
    for i in range(5):
        gen_reached.append(run(1000, "Grid3.ss"))
    print("Time taken: " + str(round(time.time()-start_time, 3)) + " seconds")
    print(gen_reached)
    gen_reached.clear()
    start_time = time.time()
    
    print("Testing: 10000")
    for i in range(5):
        gen_reached.append(run(10000, "Grid1.ss"))
    for i in range(5):
        gen_reached.append(run(10000, "Grid2.ss"))
    for i in range(5):
        gen_reached.append(run(10000, "Grid3.ss"))
    print("Time taken: " + str(round(time.time()-start_time, 3)) + " seconds")
    print(gen_reached)
    gen_reached.clear()
    start_time = time.time()

    """
        Indexes:
        10: 0-14
        100: 15-29
        1000: 30-44
        10000: 45-59
    
    """
#Tests different mutation rates to see how they affect the speed at which a successful solution is found
def test_mutation():
    results = []
    for i in range(5):
        results.append(run(10000, "Grid2.ss", 0.8, 0.2))
    for i in range(5):
        results.append(run(10000, "Grid2.ss", 0.8, 0.4))
    for i in range(5):
        results.append(run(10000, "Grid2.ss", 0.8, 0.6))
    for i in range(5):
        results.append(run(10000, "Grid2.ss", 0.8, 0.8))

    print(results)
    
#TO RUN:

#Uncomment any of the following (may take a long time to run for the larger tests)

#run(10000, "Grid2.ss")
#run(10000, "Grid1.ss", 0.7, 0.8)

#It is suggested that the print functions in evolve() are commented out before running these to avoid spam of terminal
#test_pop_size()
#test_mutation()
