import sympy as sp
import itertools
from tqdm.auto import tqdm
from virusdata import virusdata
from matrixgroups import icosahedralgroup, a4group, d10group, d6group


def eqTrueOrSolvable(eq):
    return eq == True or len(sp.solve(eq)) > 0


def findOrbitPairs(orbit0, orbit1, centralizer, tqdm_desc=""):
    vector_pairs = []
    if tqdm_desc != "":
        pair_iter = tqdm(itertools.product(orbit0, orbit1), desc=tqdm_desc, total=len(orbit0)*len(orbit1))
    else:
        pair_iter = itertools.product(orbit0, orbit1)
    for v0, v1 in pair_iter:
        if eqTrueOrSolvable(sp.Eq(centralizer*v0, v1)):
            vector_pairs.append((v0, v1))

    return vector_pairs


def findMultipleOrbitPairs(start_tuple, end_tuple, centralizer):
    assert(type(start_tuple) == type(end_tuple))
    if type(start_tuple) is tuple:
        assert len(start_tuple) == len(end_tuple)

    # get generators from the table
    start_generators = virusdata.getGenerators(start_tuple)
    end_generators = virusdata.getGenerators(end_tuple)

    # create orbits
    start_orbits = icosahedralgroup.orbitsOfVectors(start_generators)
    end_orbits = icosahedralgroup.orbitsOfVectors(end_generators)

    orbits_pairs = [findOrbitPairs(start_orbits[0], end_orbits[0], centralizer, tqdm_desc="translation")]
    for start_num, start_orbit, end_num, end_orbit in zip(start_tuple, start_orbits[1:], end_tuple, end_orbits[1:]):
        orbits_pairs.append(findOrbitPairs(start_orbit, end_orbit, centralizer, tqdm_desc=f"{start_num} --> {end_num}"))

    return orbits_pairs


def findTransition(start_tuple, end_tuple, centralizer):
    orbits_pairs = findMultipleOrbitPairs(start_tuple, end_tuple, centralizer)

    total_B0 = 1
    for pairs in orbits_pairs:
        total_B0 *= len(pairs)

    # create B0 and B1
    for pairs in tqdm(itertools.product(*orbits_pairs), desc=f"{start_tuple} --> {end_tuple}", total=total_B0):
        B0, B1 = pairs[0]
        for index, pair in enumerate(pairs[1:]):
            v0, v1 = pair
            B0 = B0.col_insert(index+1, v0)
            B1 = B1.col_insert(index+1, v1)

        transition_eq = sp.Eq(centralizer*B0, B1)

        if eqTrueOrSolvable(transition_eq):
            solution = sp.solve(transition_eq)
            transition = centralizer.subs(solution.items())
            if transition.det() != 0:
                return transition, B0, B1

    return None, None, None


if __name__ == "__main__":
    sp.init_printing()

    sp.pprint(findTransition([10], [27], d6group.centralizer()))
