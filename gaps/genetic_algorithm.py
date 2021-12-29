from __future__ import print_function
from operator import attrgetter

from piece import Piece
from selection import roulette_selection
from crossover import Crossover
from chromosome import Chromosome
from analize import ImageAnalysis


class GeneticAlgorithm(object):
    W = 1200
    H = 900
    TERMINATION_THRESHOLD = 5

    def __init__(self, pieces, population_size, generations, elite_size=2):
        self._generations = generations
        self._elite_size = elite_size
        piece_size = pieces[0].shape[0]
        self.n_rows, self.n_col = self.H // piece_size, self.W // piece_size
        pieces = [Piece(value, index) for index, value in enumerate(pieces)]
        self._population = [Chromosome(pieces, self.n_rows, self.n_col) for _ in
                            range(population_size)]
        self._pieces = pieces
        self._population_size = population_size

    def start_evolution(self):
        fittest = None
        best_fitness_score = float("-inf")
        termination_counter = 0

        analyze = ImageAnalysis()
        analyze.analyze_image(self._pieces)

        for generation in range(self._generations):

            new_population = []

            elite = self._get_elite_individuals(elites=self._elite_size)
            new_population.extend(elite)

            selected_parents = roulette_selection(self._population, elites=self._elite_size)
            for first_parent, second_parent in selected_parents:
                crossover = Crossover(first_parent, second_parent, self._pieces)
                crossover.run()
                child = crossover.child()
                new_population.append(child)

            fittest = self._best_individual()
            print(fittest.fitness)

            if fittest.fitness >= best_fitness_score:
                termination_counter += 1
            else:
                best_fitness_score = fittest.fitness

            if termination_counter == self.TERMINATION_THRESHOLD:
                return fittest.to_image().reshape(self.H, self.W, 3)

            self._population = new_population

        return fittest.to_image().reshape(self.H, self.W, 3)

    def _get_elite_individuals(self, elites):
        return sorted(self._population, key=attrgetter("fitness"))[:elites]

    def _best_individual(self):
        return min(self._population, key=attrgetter("fitness"))
