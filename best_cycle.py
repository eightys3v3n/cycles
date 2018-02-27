import itertools
import unittest


def Reversed(l : "A list or something that reversed() can be used on.") -> "An iterator for the reversed version of the input.":
    """ Merges list.reverse() and reversed(tuple) into a single function.
    """
    if isinstance(l, tuple):
        r = tuple(reversed(l))
    elif isinstance(l, list):
        r = list(reversed(l))
    else:
        raise TypeError("Don't know how to reverse type {}".format(type(l)))
    return r

def Rotated(l : "A list/tuple to rotate",
            n : "How many times to rotate") -> "A rotated version of a thing thats indexable.":
    """ Rotates an array by n places.
        i.e. Rotated((1, 2, 3), 1) -> (2, 3, 1)
    """
    return l[n:] + l[:n]

def GenerateCosts(points : "A list/tuple containing all the points in the system",
                  costs  : "A dictionary as follows for all known relationships excluding the reverses {(point_A, point_B): cost_to_travel}"):
    """ Generates and returns two data structures containing all possible cost relationships between points based on the relationships given.
    """
    edge_costs = {}
    for edge in itertools.combinations(points, 2):
        reved_edge = tuple(Reversed(edge))
        if edge in costs:
            edge_costs[edge] = costs[edge]
            edge_costs[reved_edge] = costs[edge]
        elif reved_edge in costs:
            edge_costs[edge] = costs[reved_edge]
            edge_costs[reved_edge] = costs[reved_edge]
        else:
            print("Missing a cost between points", edge)
            continue
    point_costs = {}
    for (src, dst), cost in edge_costs.items():
        if src not in point_costs:
            point_costs[src] = {}
        point_costs[src][dst] = cost

    for point, costs in point_costs.items():
        costs = list(costs.items())
        costs.sort(key=lambda x:x[1])
        costs = dict(costs)
        point_costs[point] = costs
    edge_costs = list(edge_costs.items())
    edge_costs.sort(key=lambda x:x[1])
    edge_costs = dict(edge_costs)

    return edge_costs, point_costs

def SanitizeCycle(cycle):
    cycle = list(cycle)
    cycle.reverse()
    for point in cycle:
        while cycle.count(point) > 1:
            cycle.remove(point)
    cycle.reverse()
    cycle = tuple(cycle)
    return cycle

def AreSamePath(path, other):
    if path == other:
        return True
    if tuple(Reversed(path)) == other:
        return True
    return False

def ContainsPath(paths, path):
    for p in paths:
        if AreSamePath(p, path):
            return True
    return False

def CondensePaths(paths):
    paths.reverse()
    for path in paths:
        paths_dupe = paths.copy()
        paths_dupe.remove(path)
        if ContainsPath(paths_dupe, path):
            paths.remove(path)
    paths.reverse()
    return paths

def AllPaths(points):
    paths = list(itertools.permutations(points))
    CondensePaths(paths)
    return paths

def AreSameCycle(cycle, other):
    if AreSamePath(cycle, other):
        return True
    for i in range(1, len(cycle)):
        rotated_cycle = Rotated(cycle, i)
        if AreSamePath(other, rotated_cycle):
            return True
    return False

def ContainsCycle(cycles, cycle):
    for c in cycles:
        if AreSameCycle(c, cycle):
            return True
    return False

def CondenseCycles(cycles):
    cycles.reverse()
    c = 0
    while c < len(cycles):
        cycle = cycles[c]
        cycles_dupe = cycles.copy()
        cycles_dupe.remove(cycle)
        if ContainsCycle(cycles_dupe, cycle):
            cycles.remove(cycle)
        else:
            c += 1
    cycles.reverse()
    return cycles

def AllCycles(points):
    cycles = AllPaths(points)
    CondenseCycles(cycles)
    return cycles

# def EdgeCost(src, dst):
#     if isinstance(src, (tuple, list)):
#         print("EdgeCost(src, dst): src shouldn't be a tuple or list: {}".format(src))
#     if isinstance(dst, (tuple, list)):
#         print("EdgeCost(src, dst): dst shouldn't be a tuple or list: {}".format(dst))
#     if src == dst:
#         return None
#     return costs[(src, dst)]

def EdgeCosts(cycle, point_costs):
    assert isinstance(cycle, (tuple, list))

    edge_costs = []
    for src, dst in zip(cycle, cycle[1:] + cycle[:1]):
        try:
            edge_cost = point_costs[src][dst]
        except KeyError as e:
            print("Missing point cost for {} -> {}".format(src, dst))
        if edge_cost is not None:
            edge_costs.append(edge_cost)
    return edge_costs

def CycleCost(cycle, point_costs):
    cost = sum(EdgeCosts(cycle, point_costs))
    return cost

def RankCycles(cycles, point_costs):
    ranked_cycles = []
    for cycle in cycles:
        cost = CycleCost(cycle, point_costs)
        ranked_cycles.append((cycle, cost))
    ranked_cycles.sort(key=lambda x:x[-1])
    return ranked_cycles

def AllCyclesRanked(points, point_costs):
    cycles = AllCycles(points)
    ranked_cycles = RankCycles(cycles, point_costs)
    return ranked_cycles

def BestCycles(points, point_costs):
    best_cycles = []
    ranked_cycles = AllCyclesRanked(points, point_costs)
    ranks = [ranked_cycle[-1] for ranked_cycle in ranked_cycles]
    best_rank = min(ranks)
    for ranked_cycle in ranked_cycles:
        if ranked_cycle[-1] <= best_rank:
            best_cycles.append(ranked_cycle[0])
    return best_cycles

def PrintCycle(cycle):
    cycle = SanitizeCycle(cycle)
    edge_costs = EdgeCosts(cycle)
    cycle_str = ['{}:{}'.format(p, c) for p, c in zip(cycle, edge_costs)]
    cycle_str = ':'.join(cycle_str)
    cycle_str += ' = {}'.format(CycleCost(cycle))
    print(cycle_str)

class Tests(unittest.TestCase):

    def TestRotated(self):
        self.assertEqual([2, 3, 1], Rotated([1, 2, 3], 1))
        self.assertEqual([3, 1, 2], Rotated([1, 2, 3], 2))

    def TestSanitizeCycle(self):
        self.assertEqual((1, 2, 3), SanitizeCycle((1, 2, 2, 3, 1)))

    def TestAreSamePath(self):
        self.assertTrue(AreSamePath((1, 2, 3, 4), (4, 3, 2, 1)))
        self.assertFalse(AreSamePath((1, 2, 3, 4), (3, 4, 2, 1)))

    def TestContainsPath(self):
        self.assertTrue(ContainsPath([(1, 2, 3, 4), (3, 2, 4, 1)], (1, 4, 2, 3)))
        self.assertFalse(ContainsPath([(1, 2, 3, 4), (3, 1, 4, 2)], (1, 4, 2, 3)))

    def TestCondensePaths(self):
        self.assertEqual([(1, 2, 3, 4), (1, 2, 4, 3)], CondensePaths([(1, 2, 3, 4), (4, 3, 2, 1), (1, 2, 4, 3), (4, 3, 2, 1)]))

    def TestAllPaths(self):
        self.assertCountEqual([
                (0, 1, 2), (0, 2, 1), (1, 0, 2), (2, 0, 1)
            ], AllPaths(range(3)))

    def TestAreSameCycle(self):
        self.assertTrue(AreSameCycle((0, 1, 2, 3), (1, 2, 3, 0)))
        self.assertFalse(AreSameCycle((0, 1, 2, 3), (1, 2, 0, 3)))

    def TestContainsCycle(self):
        self.assertTrue(ContainsCycle([(0, 1, 2, 3), (0, 1, 3, 2)], (2, 3, 0, 1)))
        self.assertTrue(ContainsCycle([(0, 1, 2, 3), (0, 1, 3, 2)], (3, 1, 0, 2)))
        self.assertFalse(ContainsCycle([(0, 1, 2, 3), (0, 1, 3, 2)], (3, 1, 2, 0)))

    def TestCondenseCycles(self):
        self.assertCountEqual([(0, 1, 2, 3)], CondenseCycles([(0, 1, 2, 3), (1, 2, 3, 0), (3, 2, 1, 0)]))

    def TestAllCycles(self):
        self.assertCountEqual([
                (0, 1, 2)
            ], AllCycles(range(3)))
        self.assertCountEqual([
                (0, 1, 2, 3), (0, 1, 3, 2), (0, 2, 1, 3)
            ], AllCycles(range(4)))

    def TestEdgeCost(self):
        pass

points = tuple('ABCDE')
edge_costs, point_costs = GenerateCosts(points, {
    (points[0], points[1]): 185, (points[0], points[2]): 119, (points[0], points[3]): 152, (points[0], points[4]): 133,
    (points[1], points[2]): 121, (points[1], points[3]): 150, (points[1], points[4]): 200,
    (points[2], points[3]): 174, (points[2], points[4]): 120,
    (points[3], points[4]): 199,
})
#costs = {(points[src], points[dsBest   t]): cost for (src, dst), cost in costs.items()}

def main():
    testLoader = unittest.loader.defaultTestLoader
    testLoader.testMethodPrefix = 'Test'
    unittest.main(
        verbosity=2,
        testLoader=testLoader)

if __name__ == '__main__':
    main()