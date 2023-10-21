import argparse
import sympy as sp
import itertools
import multiprocessing
import re
from os.path import exists as file_exists
import pickle
import time
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
    # check whether start_tuple and end_tuple are same length
    # comparing two ints should count has same length even though len(<int>) does not work
    try:
        assert len(start_tuple) == len(end_tuple)
    except TypeError:
        assert type(start_tuple) == type(end_tuple)

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

    for pair in orbits_pairs[curr_cols]:
        v0, v1 = pair
        B0 = prevB0.col_insert(curr_cols, v0)
        B1 = prevB1.col_insert(curr_cols, v1)

        # check for linear independence within the columns of B0 and B1
        if B0.rank() != curr_cols+1 or B1.rank() != curr_cols+1:
            continue

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
def findTransition(start_tuple, end_tuple, centralizer, centralizer_str):
    orbits_pairs = findMultipleOrbitPairs(start_tuple, end_tuple, centralizer)

    results = []
    pbar = tqdm(total=len(orbits_pairs[0]), desc=f"Finding transitions for {start_tuple} --> {end_tuple} under {centralizer_str}")

    # this function is called when a parallel process is finished
    def collectResult(result):
        pbar.update(1)
        pbar.refresh()
        if result != (None, None, None):
            results.append((start_tuple,) + (end_tuple,) + result)

    with multiprocessing.Pool() as pool:
        for translation_pair in orbits_pairs[0]:
            t0, t1 = translation_pair
            B0 = sp.Matrix([]).col_insert(0, t0)
            B1 = sp.Matrix([]).col_insert(0, t1)
            pool.apply_async(findTransitionHelper, args=(centralizer, B0, B1, orbits_pairs), callback=collectResult)

        pool.close()
        pool.join()
        pbar.close()
        return results


def pickle_file_str(pickle_dir, start_tuple, end_tuple, centralizer_string):
    # add / to directory string if it is not there
    if pickle_dir[-1] != "/":
        pickle_dir = pickle_dir + "/"

    return re.sub('[()\[\] ]', '', pickle_dir + f"{start_tuple}_to_{end_tuple}_{centralizer_string}.pickle")


def save_transitions(pickle_dir, start_tuple, end_tuple, centralizer_string, transitions):
    with open(pickle_file_str(pickle_dir, start_tuple, end_tuple, centralizer_string), 'wb') as write_file:
        pickle.dump(transitions, write_file, protocol=pickle.HIGHEST_PROTOCOL)
        print(f"Saved {start_tuple} --> {end_tuple} under {centralizer_string} to {write_file.name}")


if __name__ == "__main__":
    sp.init_printing()

    centralizer_strings = ["a4", "d10", "d6"]
    parser = argparse.ArgumentParser(description="Finds icosahedral virus transitions between point arrays.", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-d", "--pickle_dir", default="./", help="Directory in which the files will be saved. Defaults to current working directory.")
    parser.add_argument("-c", "--centralizer", type=str.lower, choices=centralizer_strings, required=True, help="Select the centralizer to be used.")
    parser.add_argument("-r", "--redo", action="store_true", help="Does all cases given, even if they have already been done before.")
    cases_group = parser.add_mutually_exclusive_group(required=True)
    cases_group.add_argument("--pt-ar", type=str, nargs=2, help="Input the numerical representations of the point arrays")
    cases_group.add_argument("--case-file")
    args = parser.parse_args()

    # get centralizer
    centralizer_str = args.centralizer.upper()
    centralizer = None
    if centralizer_str == "A4":
        centralizer = a4group.centralizer()
    elif centralizer_str == "D10":
        centralizer = d10group.centralizer()
    elif centralizer_str == "D6":
        centralizer = d6group.centralizer()


    def create_tuple(arg_str):
        tup = map(int, arg_str.split(','))
        return list(tup)

    if args.pt_ar is not None:
        stime = time.time()
        start_tuple, end_tuple = list(map(create_tuple, args.pt_ar))

        transitions = findTransition(start_tuple, end_tuple, centralizer, centralizer_str)
        for res in transitions:
            sp.pprint(res)
            print()

        print(f"Number of transitions for {start_tuple} --> {end_tuple} under {centralizer_str} is {len(transitions)}")
        save_transitions(args.pickle_dir, start_tuple, end_tuple, centralizer_str, transitions)
        etime = time.time()
        print(f"Done in{etime - stime : .3f} seconds.")
    elif args.case_file is not None:
        total_stime = time.time()
        cases = []
        with open(args.case_file, 'r') as read_file:
            for line in read_file.readlines():
                # this is assuming each line in file looks like:
                # n_1, n_2, ..., n_k > m_1, m_2, ..., m_l
                start_tuple, end_tuple = list(map(create_tuple, line.strip().split(' > ')))
                cases.append((start_tuple, end_tuple))

        print(cases)
        for case in cases:
            stime = time.time()
            start_tuple, end_tuple = case

            pickle_filename = pickle_file_str(args.pickle_dir, start_tuple, end_tuple, centralizer_str)

            # if we are not redoing cases skip it if it's already done
            if not args.redo and file_exists(pickle_filename):
                print(f"Case {start_tuple} --> {end_tuple} is already done in {pickle_filename}\n")
                continue

            print(f"Starting case {start_tuple} --> {end_tuple}...")
            transitions = findTransition(start_tuple, end_tuple, centralizer, centralizer_str)
            print(f"Number of transitions for {start_tuple} --> {end_tuple} under {centralizer_str} is {len(transitions)}")
            save_transitions(args.pickle_dir, start_tuple, end_tuple, centralizer_str, transitions)
            etime = time.time()
            print(f"Case {start_tuple} --> {end_tuple} done in{etime - stime : .3f} seconds.")
            print()

        total_etime = time.time()
        print(f"All cases completed in{total_etime - total_stime : .3f} seconds.")