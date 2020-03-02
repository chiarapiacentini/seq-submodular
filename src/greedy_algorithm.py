import numpy as np


def _select_best_r(data, evaluation_function, sequence):
    evaluations = [evaluation_function(sequence + [s]) for s in data]
    index = np.argmax(evaluations)
    return sequence + [data.pop(index)], evaluations[index]


def _select_best_g(data, evaluation_function, sequence):
    evaluations = [evaluation_function(sequence[:i] + [s] + sequence[i:]) for s in data for i in
                   range(len(sequence) + 1)]
    index = int(np.argmax(evaluations))
    i = int(index / (len(sequence) + 1))
    p = index % (len(sequence) + 1)
    return sequence[:p] + [data.pop(i)] + sequence[p:], evaluations[index]


def _greedy(data, evaluation_function, n_max=None, standard=True):
    copy_input = [s for s in data]
    sequence = []
    if not n_max:
        n_max = len(data) + 1
    while len(copy_input) > 0 and len(sequence) < n_max:
        if standard:
            sequence, f = _select_best_r(copy_input, evaluation_function, sequence)
        else:
            sequence, f = _select_best_g(copy_input, evaluation_function, sequence)
    return sequence


def greedy_standard(data, evaluation_function, n_max=None):
    return _greedy(data, evaluation_function, n_max, True)


def greedy_generalized(data, evaluation_function, n_max=None):
    return _greedy(data, evaluation_function, n_max, False)
