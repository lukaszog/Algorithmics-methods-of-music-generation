# coding: utf-8

import matplotlib.pyplot as plt
from scipy import stats
import numpy as np

class RandomVar:
    def __init__(self, name, values, probability):
        self.name = name
        self.values = values
        self.probability = probability
        if all(type(item) is np.int64 for item in values):
            self.var_type = 1
            self.rv = stats.rv_discrete(name=name, values=(values, probability))
        elif all(type(item) is str for item in values):
            self.var_type = 2
            self.rv = stats.rv_discrete(name=name, values=(np.arange(len(values)), probability))
            self.symbolic_values = values
            print self.rv

    def sample(self, size):

        numeric = self.rv.rvs(size=size)
        mapped = [self.values[x] for x in numeric]
        return mapped

    def prob(self):
        return self.probability

    def vals(self):
        print self.type
        return self.values


values = ['S', 'C']
probabilities = [0.5, 0.5]
weather = RandomVar('weater', values, probabilities)

samples = weather.sample(365)

state2color = {}
state2color['S'] = 'yellow'
state2color['C'] = 'grey'


def plot(samples, state2color):
    colors = [state2color[x] for x in samples]
    x = np.arange(0, len(colors))
    y = np.ones(len(colors))
    plt.figure(figsize=(10, 1))
    plt.bar(x, y, color=colors, width=1)
    plt.show()


samples = weather.sample(365)
plot(samples, state2color)

def markov_chain(transition_matrix, state, state_names, samples):
    (row, cols) = transition_matrix.shape
    rvs = []
    values = list(np.arange(0, row))
    print "Values {}".format(values)

    # stworz losowa wartosc dla kazdego wiersza macierzy przejscia
    for r in xrange(row):
        rv = RandomVar("row" + str(r), values, transition_matrix[r])
        print "rv {} r {}".format(rv, transition_matrix[r])
        rvs.append(rv)

    # zacznij ze stanu poczatkowego
    states = []
    for n in range(samples):
        state = rvs[state].sample(1)[0]
        states.append(state_names[state])
    return states

transition_matrix = np.array([[0.7, 0.3],
                              [0.2, 0.8]])
samples = weather.sample(365)
plot(samples, state2color)
samples_markov = markov_chain(transition_matrix, 0, ['S', 'C'], 365)
plot(samples_markov, state2color)
