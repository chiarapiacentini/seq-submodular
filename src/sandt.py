class SearchPattern:

    name = "sp"
    t_min = 0
    t_max = 0
    destinations = []
    detection = 0

    def get_time(self):
        return (self.t_min + self.t_max) * 0.5

    def __init__(self, n="", t_m=0, t_M=0, ds=[], d=0, **kwargs):
        if "line" in kwargs:
            tokens = kwargs["line"].split()
            if len(tokens) >= 1:
                self.name = tokens[0] + "_" + str(kwargs["rep"]) if "rep" in kwargs else tokens[0]
            else:
                self.name = "empty"
            if len(tokens) >= 2:
                self.t_min = float(tokens[1])
            else:
                self.t_min = 0

            if len(tokens) >= 3:
                self.t_max = float(tokens[2])
            else:
                self.t_max = 0
            if len(tokens) >= 4:
                self.detection = float(tokens[3])
            else:
                self.detection = 0
            if len(tokens) >= 5:
                self.destinations = tokens[4:]
            else:
                self.destinations = []
        else:
            self.name = n
            self.t_min = t_m
            self.t_max = t_M
            self.destinations = ds
            self.detection = d

    def __str__(self):
        return self.name + " [" + str(self.t_min) + ", " + str(self.t_max) + "]" + " det = " + str(self.detection)

    def __repr__(self):
        return self.name

    def __lt__(self, other):
        return self.get_time() < other.get_time()


class SearchProblem:
    search_patterns = []
    destinations = {}
    T_MAX = 0
    k = 0.0

    def __init__(self, sp_list=[], **kwargs):
        self.destinations = {}
        self.search_patterns = []
        self.T_MAX = 0
        self.k = 0.0
        for sp in sp_list:
            self.add_search_pattern(sp)
        if "text" in kwargs:
            for line in kwargs["text"].split("\n"):
                if line != "":
                    n = int(kwargs["rep"]) if "rep" in kwargs else 1
                    for i in range(n):
                        sp = SearchPattern(line=line, rep=i)
                        self.add_search_pattern(sp)

    def __str__(self):
        f = ""
        for sp in self.search_patterns:
            f = f + str(sp) + "\n"
        return f

    def __repr__(self):
        f = ""
        for sp in self.search_patterns:
            f = f + str(sp) + "\n"
        return f

    def add_search_pattern(self, sp):
        self.search_patterns.append(sp)
        if (sp.t_max + sp.t_min) * 0.5 > self.T_MAX:
            self.T_MAX = (sp.t_max + sp.t_min) * 0.5
        for d in sp.destinations:
            if d in self.destinations:
                self.destinations[d].append(sp)
            else:
                self.destinations[d] = [sp]

    def sum_destinations(self):
        return sum([len(s.destinations) for s in self.search_patterns])

    def set_k(self, k):
        self.k = k

    def calculate_probability(self, sequence=[], debug=False):
        prob_d = dict((d, 1. / len(self.destinations)) for d in self.destinations)
        prob = 0
        previous_time = 0
        tot = 0
        for s in sequence:
            if s.get_time() < previous_time:
                return prob
            ps = s.detection * sum([prob_d[d] for d in s.destinations])
            prob_p = prob
            prob = prob + (1 - prob) * ps
            last_t = s.get_time()
            tot = tot + (self.T_MAX + self.k - last_t) * (prob - prob_p)
            for d in self.destinations:
                if d in s.destinations:
                    prob_d[d] = prob_d[d] * (1 - s.detection) / (1 - ps)
                else:
                    prob_d[d] = prob_d[d] * 1. / (1 - ps)
            if debug:
                print("\t", s, prob, ps, tot)
            previous_time = last_t
        return tot
