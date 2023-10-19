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


if __name__ == "__main__":
    sp.init_printing()
    sp.pprint(virusdata.configs[12])
    sp.pprint(a4group.centralizer())
    sp.pprint(d10group.centralizer())
    sp.pprint(d6group.centralizer())

    # sp.pprint(virusdata.getGenerators((4, 5, 6, 7)))

    BASE_STR = virusdata.BASE_STR
    TRANSLATION_STR = virusdata.TRANSLATION_STR

    # testOrbit0 = icosahedralgroup.orbitOfVector(virusdata.configs[36][TRANSLATION_STR])
    # testOrbit1 = icosahedralgroup.orbitOfVector(virusdata.configs[36][TRANSLATION_STR])
    #
    # testPairs = findOrbitPairs(testOrbit0, testOrbit1, d6group.centralizer())
    #
    # sp.pprint(testPairs)
    # sp.pprint(len(testPairs))

    pairs = findMultipleOrbitPairs((1, 1), (2, 3), d6group.centralizer())

    for index, lst in enumerate(pairs):
        print(f"Pair list {index} with length {len(lst)}")
        sp.pprint(lst[:10])
