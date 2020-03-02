import datetime
import os
import random
import greedy_algorithm as ga
import sandt as sat
import argparse
import sys
import numpy as np

from os import listdir
from os.path import isfile, join


def generate_instance(seed, max_sp, separation, n_destination, slope, n_roads, address):
    directory = address + "/"
    if not os.path.exists(directory):
        os.makedirs(directory)
    random.seed(seed)
    text = ""
    min_t = 1
    n_roads = random.randint(1, n_roads)
    roads = []
    n = 0
    for r in range(n_roads):
        if n_destination < n_roads:
            raise ValueError("chose n_destination > n_roads")
        n_city = random.randint(1, int(n_destination/n_roads))
        roads.append(list(range(n, n_city + n)))
        n = n_city
    for i in range(max_sp):
        name = "searchpattern" + str(i)
        min_t = random.randint(min_t, min_t + separation)
        d = 2
        max_t = min_t + d
        xc = (max_sp - 1) * 0.5
        yc = 0.5
        m = slope * yc / xc
        q = yc - m * xc
        detection = min(max(m * i + q, 0.001), 0.999)
        group_city = random.randint(0, n_roads - 1)
        initial_cities = roads[group_city]
        n_cities = random.randint(max(1, int(len(initial_cities) / 2)), len(initial_cities))
        destinations = random.sample(roads[group_city], n_cities)
        roads[group_city] = destinations
        text = text + name + " " + str(min_t) + " " + str(max_t) + " " + str(detection)
        for d in destinations:
            text = text + " v" + str(d)
        text = text + "\n"

        name = "instance_" + str(seed) + ".txt"
        f = open(directory + name, "w")
        f.write(text)
        f.close()
    return text, name


def run_instance(instance, max_sequence, max_repetition):
    problem = sat.SearchProblem(text=instance, rep=max_repetition)
    problem.set_k(0)
    seq = ga.greedy_standard(problem.search_patterns, problem.calculate_probability, max_sequence)
    seq2 = ga.greedy_generalized(problem.search_patterns, problem.calculate_probability, max_sequence)
    return problem.calculate_probability(seq), problem.calculate_probability(seq2)


def experiment_from_folder(address,  max_sequence, max_repetition, log):
    y1 = {}
    y2 = {}
    new_address = address
    files = [f for f in listdir(new_address) if isfile(join(new_address, f))]
    for file in files:
        f = open(new_address + "/" + file, "r")
        instance = text=f.read()
        problem = sat.SearchProblem(text=instance, rep=max_repetition)
        s, g = run_instance(instance, max_sequence, max_repetition)
        f.close()
        m = "{:.1f}".format((-problem.search_patterns[0].detection * 2 + 1))
        log.write(file + "," + m + "," + str(max_repetition) + "," + str(s) + "," + str(g) + "\n")
        y1.setdefault(m, [])
        y1[m].append(s)
        y2.setdefault(m, [])
        y2[m].append(g)
    return y1, y2


def experiment_generate_random(n_experiments, address, n_destination, max_sequence, max_search_patterns, n_roads,
                               max_repetition, log):
    y1 = {}
    y2 = {}
    for i in range(n_experiments):
        print("run " + str(i))
        for j in [-1, -0.8, -0.6, -0.4, -0.2, 0, 0.2, 0.4, 0.6, 0.8, 1]:

            instance, name = generate_instance(random.random(), max_search_patterns, max_search_patterns, n_destination,
                                               j, n_roads,
                                               address)
            s, g = run_instance(instance, max_sequence, max_repetition)
            log.write(name + "," + str(j) + "," + str(max_repetition) + "," + str(s) + "," + str(g) + "\n")
            y1.setdefault(j, [])
            y1[j].append(s)
            y2.setdefault(j, [])
            y2[j].append(g)
    return y1, y2


def run_experiments(args):
    log = open(args.save_file, "w") if args.save_file else sys.stdout
    log.write("name" + "," + "m" + "," + "repetition" + "," + "parameter" + "," + "G_standard" + "," + "G_generalized"
              + "\n")
    if args.new.lower() == "false":
        address = args.folder
        y1, y2 = experiment_from_folder(address, args.max_sequence, args.max_repetition, log)
    else:
        now = datetime.datetime.now()
        name = now.strftime("%Y%m%d%H%M%S")
        address = args.folder + "/run_" + name + "/"
        if not os.path.exists(address):
            os.makedirs(address)
            print("created\n\t" + address)
            y1, y2 = experiment_generate_random(args.n_problems, address, args.n_destinations, args.max_sequence,
                                                args.n_search_patterns, args.n_roads, args.max_repetition, log)
            print("file saved in \n\t" + address)

    print("average greedy standard:    ", np.mean(list(y1.values())))
    print("average greedy generalized: ", np.mean(list(y2.values())))


if __name__ == '__main__':
    argparser = argparse.ArgumentParser(
                        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    argparser.add_argument('-f', '--folder', default='.')
    argparser.add_argument('-n', '--new', help="create new dataset", default="true")
    argparser.add_argument('-p', '--save_file', help="print on screen", default=False)
    argparser.add_argument('-N', '--n_problems', help="number of problems", default=1000, type=int)
    argparser.add_argument('-R', '--n_roads', help="number of problems", default=10, type=int)
    argparser.add_argument('-d', '--n_destinations', help="number of destinations", default=40, type=int)
    argparser.add_argument('-s', '--n_search_patterns', help="number of search patterns", default=20, type=int)
    argparser.add_argument('-l', '--max_sequence', help="max length of sequence", default=10, type=int)
    argparser.add_argument('-r', '--max_repetition', help="max number of repetitions", default=1, type=int)
    args = argparser.parse_args()
    run_experiments(args)



