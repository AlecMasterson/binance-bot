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

bot = Bot(False, True)

# def normal_dist_list(seed):
#     for i in range(100):
#     yeild [np.random.normal(loc=x, scale=x**0.5) for x in seed]


def ga_evaluate_genetics(individual):
    eval_start_time = time.time()
    # print(individual)
    utilities.set_optimized(individual[0], individual[1], individual[2])
    # bot = Bot(False, True)
    # bot.print_optimize()
    fitness = bot.run_backtest(utilities.COINPAIRS[0])
    # print(fitness, time.time() - eval_start_time)
    return (fitness,)
    # bo = BayesianOptimization(lambda test: bot.run_backtest(utilities.COINPAIRS[0]), {'test': (3.0, 3.0)})


def ga_optimize(seed=False, population_size=100, generations=100):
    creator.create("FitnessMax", base.Fitness, weights=(1.0,))
    creator.create("Individual", list, fitness=creator.FitnessMax)

    toolbox = base.Toolbox()
    if seed:
        toolbox.register("individual", creator.Individual, [np.random.normal(loc=x, scale=x**0.5) for x in seed])
    else:
        toolbox.register("attr_float", random.uniform, -5.0, 5.0)
        toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_float, n=3)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)

    toolbox.register("evaluate", ga_evaluate_genetics)
    toolbox.register("mate", tools.cxTwoPoint)
    toolbox.register("mutate", tools.mutGaussian, mu=0.0, sigma=0.5, indpb=0.5)
    toolbox.register("select", tools.selSPEA2)

    # pool = multiprocessing.Pool()
    # toolbox.register("map", pool.map)

    pop = toolbox.population(n=population_size * 5)
    hof = tools.HallOfFame(3)
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", np.mean)
    stats.register("min", np.min)
    stats.register("max", np.max)

    # pop, logbook = algorithms.eaSimple(pop, toolbox, cxpb=0.8, mutpb=0.4, ngen=1000, stats=stats, halloffame=hof, verbose=True)
    pop, logbook = algorithms.eaMuPlusLambda(pop, toolbox, mu=int(population_size / 10), lambda_=population_size, cxpb=0.6, mutpb=0.25, ngen=generations, stats=stats, halloffame=hof, verbose=True)

    for b in hof:
        print("Top individual: %s\nwith fitness: %s" % (b, b.fitness))

    gen, avg, min_, max_ = logbook.select("gen", "avg", "min", "max")
    plt.plot(gen, avg, label="average")
    plt.plot(gen, min_, label="minimum")
    plt.plot(gen, max_, label="maximum")
    plt.xlabel("Generation")
    plt.ylabel("Fitness")
    plt.legend(loc="lower right")

    graph = networkx.DiGraph(history.genealogy_tree)
    graph = graph.reverse()
    colors = [toolbox.evaluate(history.genealogy_history[i])[0] for i in graph]
    networkx.draw(graph, node_color=colors)
    plt.show()


if __name__ == "__main__":
    # bot = Bot(False, True)

    # bo = BayesianOptimization(lambda test: bot.run_backtest(utilities.COINPAIRS[0]), {'test': (3.0, 3.0)})
    # bo.maximize(init_points=50, n_iter=1, kappa=2)
    #
    # print(bo.res['max'])
    # ga_evaluate_genetics([1, 2, 3])
    ga_optimize([9e5, 1.01, 0.003], 50, 50)
