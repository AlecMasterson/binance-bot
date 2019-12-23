import multiprocessing
import random
from os import environ

import matplotlib.pyplot as plt
import numpy as np
from deap import algorithms, base, creator, tools
from keras.callbacks import ModelCheckpoint, TensorBoard
from keras.layers import Dense, Flatten, Input
from keras.models import Model
from keras.optimizers import Adam, Nadam, RMSprop

from trading_env.csvstream import CSVStreamer
from trading_env.trading_env import TradingEnv

environ["CUDA_VISIBLE_DEVICES"] = "-1"


def evaluate_genetics(individual):

    def build_network():
        brain_input = Input(shape=(1, 9))
        brain_output = Dense(10, activation='relu')(brain_input)
        brain_output = Dense(5, activation='relu')(brain_output)
        brain_output = Dense(2, activation='relu')(brain_output)
        brain_model = Model(inputs=brain_input, outputs=brain_output)
        brain_model.compile(optimizer=Nadam(lr=0.01), metrics=['mae', 'mse'], loss='mean_absolute_error')
        return brain_model

    def update_model_weights(model, new_weights):
        write_head = 0
        for layer in model.layers:
            current_layer_weights_list = layer.get_weights()
            new_layer_weights_list = []
            for layer_weights in current_layer_weights_list:
                layer_total = np.prod(layer_weights.shape)
                new_layer_weights_list.append(new_weights[write_head:write_head + layer_total].reshape(layer_weights.shape))
                write_head += layer_total
            layer.set_weights(new_layer_weights_list)

    done = False

    generator = CSVStreamer('data_5_min/ADABTC.csv')
    env = TradingEnv(data_generator=generator, episode_length=10e10, trading_fee=0.01, time_fee=0.0001, history_length=1, s_c1=1, s_c2=0, buy_sell_scalar=1, hold_scalar=0.001, timeout_scalar=100)

    brain = build_network()
    update_model_weights(brain, np.asarray(individual))

    observation = env.reset()
    while not done:
        observation = np.reshape(observation, (1, 1, 9))
        action = np.argmax(brain.predict(observation))
        observation, reward, done, info = env.step(action)

    hold_penalty = 3 if env.action_history.count(1) <= 5 else 0
    buy_penalty = 3 if env.action_history.count(0) <= 5 else 0
    fitness = (env.total_value + (env.iteration / env.data_generator.file_length) / 10) - hold_penalty - buy_penalty

    print('Iteration', env.iteration, '   \t\tBuy:', env.action_history.count(0), '   \t\tHold:', env.action_history.count(1), '   \t\tFitness:', fitness)

    return (fitness,)


INDIVIDUAL_SIZE = 167

creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)

toolbox = base.Toolbox()
toolbox.register("attr_float", random.uniform, -5.0, 5.0)
toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_float, n=INDIVIDUAL_SIZE)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

toolbox.register("evaluate", evaluate_genetics)
toolbox.register("mate", tools.cxUniform, indpb=0.4)
toolbox.register("mutate", tools.mutGaussian, mu=0.0, sigma=0.5, indpb=0.5)
toolbox.register("select", tools.selSPEA2)

pool = multiprocessing.Pool()
toolbox.register("map", pool.map)


def main():
    pop = toolbox.population(n=200)
    hof = tools.HallOfFame(3)
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", np.mean)
    stats.register("min", np.min)
    stats.register("max", np.max)

    # pop, logbook = algorithms.eaSimple(pop, toolbox, cxpb=0.8, mutpb=0.4, ngen=1000, stats=stats, halloffame=hof, verbose=True)
    pop, logbook = algorithms.eaMuPlusLambda(pop, toolbox, mu=10, lambda_=50, cxpb=0.7, mutpb=0.25, ngen=1000, stats=stats, halloffame=hof, verbose=True)

    return pop, logbook, hof


if __name__ == "__main__":
    pop, log, hof = main()
    for b in hof:
        print("Top individual: %s\nwith fitness: %s" % (b, b.fitness))

    gen, avg, min_, max_ = log.select("gen", "avg", "min", "max")
    plt.plot(gen, avg, label="average")
    plt.plot(gen, min_, label="minimum")
    plt.plot(gen, max_, label="maximum")
    plt.xlabel("Generation")
    plt.ylabel("Fitness")
    plt.legend(loc="lower right")

    import networkx

    graph = networkx.DiGraph(history.genealogy_tree)
    graph = graph.reverse()        # Make the grah top-down
    colors = [toolbox.evaluate(history.genealogy_history[i])[0] for i in graph]
    networkx.draw(graph, node_color=colors)
    plt.show()

    # evaluate_genetics([0] * INDIVIDUAL_SIZE)
