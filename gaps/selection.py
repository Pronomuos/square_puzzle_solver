import random
import bisect


def roulette_selection(population, elites=4):
    fitness_values = [1 / individual.fitness for individual in population]
    probability_intervals = [sum(fitness_values[:i + 1]) for i in range(len(fitness_values))]

    def select_individual_index():
        first_random_select = random.uniform(0, probability_intervals[-1])
        return bisect.bisect_left(probability_intervals, first_random_select)

    def select_parents():
        while True:
            first_index, second_index = select_individual_index(), select_individual_index()
            if first_index != second_index:
                return population[first_index], population[second_index]

    selected = []
    for i in range(len(population) - elites):
        first, second = select_parents()
        selected.append((first, second))

    return selected
