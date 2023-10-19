import sympy as sp
import itertools
from tqdm.auto import tqdm
from virusdata import virusdata
from matrixgroups import icosahedralgroup, a4group, d10group, d6group


# checks if a sympy equation is either true or solvable
def eqTrueOrSolvable(eq):
    return eq == True or len(sp.solve(eq)) > 0


# finds what pairs of vectors can be solved by Tv_0 = v_1 while looping over their (ICO) orbits
def findOrbitPairs(orbit0, orbit1, centralizer, tqdm_desc=""):
    vector_pairs = []
    if tqdm_desc != "":
        pair_iter = tqdm(itertools.product(orbit0, orbit1), desc=tqdm_desc, total=len(orbit0) * len(orbit1))
    else:
        pair_iter = itertools.product(orbit0, orbit1)
    for v0, v1 in pair_iter:
        if eqTrueOrSolvable(sp.Eq(centralizer * v0, v1)):
            vector_pairs.append((v0, v1))

    return vector_pairs


# runs findOrbitPairs on multiple generators at once
def findMultipleOrbitPairs(start_tuple, end_tuple, centralizer):
    assert (type(start_tuple) == type(end_tuple))
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


# recursive helper function for finding transitions
# builds up the columns of B0 and B1 in a depth first manner
def findTransitionHelper(prevCentralizer, prevB0, prevB1, orbits_pairs, tqdm_desc=""):
    curr_cols = prevB0.shape[1]
    assert (prevB0.shape[1] == prevB1.shape[1])

    if curr_cols == len(orbits_pairs):
        return prevCentralizer, prevB0, prevB1

    if curr_cols == 0:
        orbit_iter = tqdm(orbits_pairs[curr_cols], desc=tqdm_desc)
    else:
        orbit_iter = orbits_pairs[curr_cols]

    for pair in orbit_iter:
        v0, v1 = pair
        B0 = prevB0.col_insert(curr_cols, v0)
        B1 = prevB1.col_insert(curr_cols, v1)
        curr_eq = sp.Eq(prevCentralizer * B0, B1)
        if eqTrueOrSolvable(curr_eq):
            curr_solution = sp.solve(curr_eq)
            if len(curr_solution) == 0:
                curr_centralizer = prevCentralizer
            else:
                curr_centralizer = prevCentralizer.subs(curr_solution.items())

            if curr_centralizer.det() != 0:
                curr_centralizer, B0, B1 = findTransitionHelper(curr_centralizer, B0, B1, orbits_pairs)
                if curr_centralizer is not None and B0.shape[1] == len(orbits_pairs):
                    return curr_centralizer, B0, B1

    return None, None, None


# find a transition from (n_1, n_2, ..., n_k) to (m_1, m_2, ..., m_k)
def findTransition(start_tuple, end_tuple, centralizer):
    orbits_pairs = findMultipleOrbitPairs(start_tuple, end_tuple, centralizer)

    total_B0 = 1
    for pairs in orbits_pairs:
        total_B0 *= len(pairs)

    return findTransitionHelper(centralizer, sp.Matrix([]), sp.Matrix([]), orbits_pairs, tqdm_desc=f"Find transition {start_tuple} --> {end_tuple}")


if __name__ == "__main__":
    sp.init_printing()

    sp.pprint(findTransition([1, 1], [2, 3], d6group.centralizer()))
