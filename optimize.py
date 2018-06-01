import math
import multiprocessing
import random
import time

import matplotlib.pyplot as plt
import networkx
import numpy as np
from bayes_opt import BayesianOptimization
from deap import algorithms, base, creator, tools

import utilities
from Bot import Bot

eval_start_time = time.time()
bot = Bot(False, True)
print(time.time() - eval_start_time)


def ga_mutate(individual):

    def rand_norm(num):
        num = x
        mag = 0
        if x > 1:
            while (num > 1):
                mag += 1
                num /= 10
        elif x < 1:
            while (num < 1):
                mag += 1
                num *= 10
        return np.random.normal(loc=x, scale=mag)

    while True:        # [1, 12] Integers
        nr = int(rand_norm(individual[0]))
        if 1 <= nr <= 12:
            individual[0] = nr
    while True:        # [1.0030, 1.0500] 4 Decimal places
        nr = round(rand_norm(individual[1]), 4)
        if 1.0030 <= nr <= 1.0500:
            individual[1] = nr
    while True:        # [0.000, 0.050] 3 Decimal places
        nr = round(rand_norm(individual[2]), 3)
        if 0.000 <= nr <= 0.050:
            individual[2] = nr
    while True:        # [0.9500, 0.9999] # 4 Decimal places
        nr = round(rand_norm(individual[3]), 4)
        if 0.9500 <= nr <= 0.9999:
            individual[0] = nr

    return individual,


def ga_evaluate_genetics(individual):
    # print('evaluate')
    # eval_start_time = time.time()
    # print(individual)
    utilities.set_optimized(individual[0], individual[1], individual[2])
    # bot = Bot(False, True)
    # bot.print_optimize()
    fitness = bot.run_backtest(utilities.COINPAIRS[0])
    # print(fitness, time.time() - eval_start_time)
    return fitness,


def ga_optimize(seed=False, population_size=100, generations=100):
    creator.create("FitnessMax", base.Fitness, weights=(1.0,))
    creator.create("Individual", list, fitness=creator.FitnessMax)

    toolbox = base.Toolbox()
    if seed:
        toolbox.register("individual", creator.Individual, ga_mutate(seed))
    else:
        toolbox.register("attr_float", random.uniform, 0, 1.0)
        toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_float, n=4)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)

    toolbox.register("evaluate", ga_evaluate_genetics)
    toolbox.register("mate", tools.cxTwoPoint)
    toolbox.register("mutate", ga_mutate)
    toolbox.register("select", tools.selSPEA2)

    # pool = multiprocessing.Pool()
    # toolbox.register("map", pool.map)

    pop = toolbox.population(n=population_size * 2)
    hof = tools.HallOfFame(3)
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", np.mean)
    stats.register("min", np.min)
    stats.register("max", np.max)
    rt = tools.Statistics(lambda ind: ind.fitness.values)

    # pop, logbook = algorithms.eaSimple(pop, toolbox, cxpb=0.8, mutpb=0.4, ngen=1000, stats=stats, halloffame=hof, verbose=True)
    pop, logbook = algorithms.eaMuPlusLambda(pop, toolbox, mu=int(population_size / 10), lambda_=population_size, cxpb=0.2, mutpb=0.75, ngen=generations, stats=stats, halloffame=hof, verbose=True)

    for b in hof:
        print("Top individual: %s\nwith fitness: %s" % (b, b.fitness))

    gen, avg, min_, max_ = logbook.select("gen", "avg", "min", "max")
    plt.plot(gen, avg, label="average")
    plt.plot(gen, min_, label="minimum")
    plt.plot(gen, max_, label="maximum")
    plt.xlabel("Generation")
    plt.ylabel("Fitness")
    plt.legend(loc="lower right")
    plt.show()


if __name__ == "__main__":
    # bot = Bot(False, True)

    # bo = BayesianOptimization(lambda test: bot.run_backtest(utilities.COINPAIRS[0]), {'test': (3.0, 3.0)})
    # bo.maximize(init_points=50, n_iter=1, kappa=2)
    #
    # print(bo.res['max'])
    # ga_evaluate_genetics([1, 2, 3])
    ga_optimize([3, 1.01, 0.003, 0.9975], 25, 5)
