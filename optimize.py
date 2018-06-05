import itertools
import math
import multiprocessing
import random
import time
from copy import deepcopy

import matplotlib.pyplot as plt
import numpy as np
from bayes_opt import BayesianOptimization

import utilities
from Bot import Bot

# from deap import algorithms, base, creator, tools

bot = Bot(online=False, optimize=True)


def ga_mutate(individual, mu=1):

    def rand_norm(x, lower, upper):
        nr = np.random.normal(loc=x, scale=((upper - lower) / mu))
        if nr <= lower:
            return lower
        elif nr >= upper:
            return upper
        else:
            return nr

    g0 = int(rand_norm(individual['genes'][0], 1, 12))        # [1, 12] Integers
    g1 = round(rand_norm(individual['genes'][1], 0, 1.5), 4)        # [1.0030, 1.0500] 4 Decimal places
    g2 = round(rand_norm(individual['genes'][2], 0.000, 1.5), 3)        # [0.000, 0.050] 3 Decimal places
    g3 = round(rand_norm(individual['genes'][3], 0.00, 1.5), 4)        # [0.9500, 0.9999] # 4 Decimal places
    g4 = round(rand_norm(individual['genes'][4], 0.001, 1.000), 3)        # [0.001, 1.000] 3 Decimal Places
    g5 = round(rand_norm(individual['genes'][5], 0.000, 0.999), 3)        # [0.000, 0.999] 3 Decimal Places
    g6 = round(rand_norm(individual['genes'][5], 0.000, 0.999), 3)        # [0.000, 0.999] 3 Decimal Places
    g7 = round(rand_norm(individual['genes'][5], 0.000, 0.999), 3)        # [0.000, 0.999] 3 Decimal Places
    g8 = round(rand_norm(individual['genes'][5], 0.000, 0.999), 3)        # [0.000, 0.999] 3 Decimal Places
    genes = [g0, g1, g2, g3, g4, g5, g6, g7, g8]
    individual['genes'] = genes
    return individual


def ga_randx_breed(p1, p2):
    # np.random.seed()
    p1_genes = deepcopy(p1['genes'])
    p2_genes = deepcopy(p2['genes'])
    child = p1_genes
    swaps = np.random.choice(len(p2_genes), np.random.randint(1, len(p2_genes), 1))
    for pos in swaps:
        child[pos] = p2_genes[pos]
    return {'genes': child, 'fitness': -1}


def ga_evaluate_genetics(individual, MEMOIZED_EVALS):
    genes = individual['genes']
    try:
        individual['fitness'] = MEMOIZED_EVALS[str(genes)]
    except:
        utilities.set_optimized(genes[0], genes[1], genes[2], genes[3], genes[4], genes[5], genes[6], genes[7], genes[8])
        fitness = np.mean([bot.run_backtest(pair) for pair in utilities.COINPAIRS])
        MEMOIZED_EVALS[str(genes)] = fitness
        individual['fitness'] = fitness
    return individual, MEMOIZED_EVALS


def ga_select(population):
    return list(sorted(population, key=lambda x: x['fitness'], reverse=True))[:int(len(population) / 10)]


def pop_stats(population, history, gen, MEMOIZED_EVALS, rt):
    fitnesses = []
    for ind in population:
        fitnesses += [ind['fitness']]
    print('Gen {0:4d} | Run Time {1:.3f} | Min {2:.9f} | P50 {3:.9f} | Max {4:.9f} | Num unique genes: {5:7d}'.format(gen, rt, np.min(fitnesses), np.percentile(fitnesses, 50), np.max(fitnesses),
                                                                                                                      len(MEMOIZED_EVALS[0])))
    history['min'] += np.min(fitnesses)
    history['p25'] += np.percentile(fitnesses, 25)
    history['p50'] += np.percentile(fitnesses, 50)
    history['p75'] += np.percentile(fitnesses, 75)
    history['max'] += np.max(fitnesses)
    return history


def ga_optimize(seed=False, population_size=100, generations=100):
    MEMOIZED_EVALS = [{}]
    # np.random.seed()
    population = []
    if seed:
        for _ in range(10):
            population += [{'genes': seed, 'fitness': -1}]
        for _ in range(population_size):
            population += [ga_mutate({'genes': seed, 'fitness': -1})]
    else:
        for _ in range(population_size * 5):
            population += [ga_mutate({'genes': [1, 1, 1, 1, 1, 1, 1, 1, 1], 'fitness': -1})]

    gen = 0
    history = {'min': [], 'p25': [], 'p50': [], 'p75': [], 'max': []}
    best = population[0]
    best_bot_performance = -1
    p = multiprocessing.Pool(10)
    while gen < generations:
        gen_start_time = time.time()
        gen += 1
        result = p.starmap(ga_evaluate_genetics, itertools.product(population, MEMOIZED_EVALS))
        population = [t[0] for t in result]
        MEMOIZED_EVALS = [t[1] for t in result]
        MEMOIZED_EVALS = [{k: v for d in MEMOIZED_EVALS for k, v in d.items()}]
        history = pop_stats(population, history, gen, MEMOIZED_EVALS, time.time() - gen_start_time)
        gen_start_time = time.time()
        population = ga_select(population)
        if population[0]['fitness'] > best['fitness']:
            print('Old Best', best, best_bot_performance)
            best = deepcopy(population[0])
            utilities.set_optimized(best['genes'][0], best['genes'][1], best['genes'][2], best['genes'][3], best['genes'][4], best['genes'][5], best['genes'][6], best['genes'][7], best['genes'][8])
            best_bot_performance = list(zip(utilities.COINPAIRS, [bot.run_backtest(pair) for pair in utilities.COINPAIRS]))
            print('New Best', best, best_bot_performance)
        population += [deepcopy(best)]
        population += [ga_randx_breed(pair[0], pair[1]) for pair in zip(np.random.choice(population, int(len(population) / 2)), np.random.choice(population, int(len(population) / 2)))]
        population += [ga_mutate(deepcopy(np.random.choice(population, 1)[0]), 200) for _ in range(population_size)]
        population += [ga_mutate(deepcopy(np.random.choice(population, 1)[0]), 50) for _ in range(population_size)]
        population += [ga_mutate(deepcopy(np.random.choice(population, 1)[0]), 10) for _ in range(population_size)]
        population += [ga_mutate(deepcopy(np.random.choice(population, 1)[0]), 5) for _ in range(population_size)]
        population += [ga_mutate(deepcopy(np.random.choice(population, 1)[0]), 2) for _ in range(population_size)]

    print('Best', best, best_bot_performance)
    print('Num unique genes', len(MEMOIZED_EVALS))
    # gen, avg, min_, max_ = logbook.select("gen", "avg", "min", "max")
    # plt.plot(gen, avg, label="average")
    # plt.plot(gen, min_, label="minimum")
    # plt.plot(gen, max_, label="maximum")
    # plt.xlabel("Generation")
    # plt.ylabel("Fitness")
    # plt.legend(loc="lower right")
    # plt.show()


### BOUND
# {'genes': [2, 1.0341, 0.05, 0.9543], 'fitness': 1.3293399265950028}
### UNBOUND
# {'genes': [1, 1.087, 0.04, 0.7976], 'fitness': 1.586393404252001}
### MORE COINS
# {'genes': [1, 1.2723, 0.03, 0.7178], 'fitness': 1.058437639641258} [('BNBBTC', 1.5033769119700002), ('ADABTC', 0.6343256048600001), ('LTCBTC', 1.0173513836522903), ('ETHBTC', 0.9831574233939997), ('IOTAETH', 1.1539768743300003)]
if __name__ == "__main__":
    ga_optimize(seed=[1, 1.2723, 0.03, 0.7178, 0.085, 0.8, 0.3, 0.3, 0.3], population_size=25, generations=1000)
