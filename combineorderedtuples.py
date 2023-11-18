import argparse
import sympy as sp
import itertools
import multiprocessing
import re
import os
from os.path import exists as file_exists
import pickle
import time
import sys
from tqdm.auto import tqdm
from virusdata import virusdata
from matrixgroups import icosahedralgroup, centralizers


# checks if a sympy equation is either true or solvable
def equation_is_true_or_solvable(eq):
    return eq == True or len(sp.solve(eq)) > 0


def get_vector_pair_filename(dir, start_num, end_num, centralizer):
    centralizer_str = centralizers.get_centralizer_str_from_matrix(centralizer)

    if dir[-1] != "/":
        dir = dir + "/"

    return dir + f"{start_num}_to_{end_num}_{centralizer_str}_pairs.pickle"


# finds what pairs of vectors can be solved by Tv_0 = v_1 while looping over their (ICO) orbits
def find_orbit_pairs(start_num, orbit0, end_num, orbit1, centralizer, tqdm_desc=""):
    PAIR_DIRECTORY = "vector_pairs/"
    vector_pair_filename = get_vector_pair_filename(PAIR_DIRECTORY, start_num, end_num, centralizer)

    # force stdout to flush first, so an empty tqdm bar doesn't appear before the stdout print
    sys.stdout.flush()

    # if a vector pair file exists, return it
    if start_num != -1 and file_exists(vector_pair_filename):
        with open(vector_pair_filename, 'rb') as pickle_file:
            print(tqdm_desc + " returned from file.", flush=True)
            return pickle.load(pickle_file)

    vector_pairs = []
    if tqdm_desc != "":
        pair_iter = tqdm(itertools.product(orbit0, orbit1), desc=tqdm_desc, total=len(orbit0) * len(orbit1))
    else:
        pair_iter = itertools.product(orbit0, orbit1)
    for v0, v1 in pair_iter:
        if equation_is_true_or_solvable(sp.Eq(centralizer * v0, v1)):
            vector_pairs.append((v0, v1))

    # write vector pairs to file
    if start_num != -1:
        # create the directory if it doesn't exist
        if not os.path.exists(PAIR_DIRECTORY):
            os.makedirs(PAIR_DIRECTORY)

        with open(vector_pair_filename, 'wb') as pickle_file:
            pickle.dump(vector_pairs, pickle_file, protocol=pickle.HIGHEST_PROTOCOL)

    return vector_pairs


# runs findOrbitPairs on multiple generators at once
def find_multiple_orbit_pairs(start_tuple, end_tuple, centralizer):
    # check whether start_tuple and end_tuple are same length
    # comparing two ints should count has same length even though len(<int>) does not work
    try:
        assert len(start_tuple) == len(end_tuple)
    except TypeError:
        assert type(start_tuple) == type(end_tuple)

    # get generators from the table
    start_generators = virusdata.get_generators(start_tuple)
    end_generators = virusdata.get_generators(end_tuple)

    start_translation_str = virusdata.get_translation_vector_str(start_generators[0])
    end_translation_str = virusdata.get_translation_vector_str(end_generators[0])

    # create orbits
    start_orbits = icosahedralgroup.orbitsOfVectors(start_generators)
    end_orbits = icosahedralgroup.orbitsOfVectors(end_generators)

    orbits_pairs = [find_orbit_pairs(start_translation_str, start_orbits[0], end_translation_str, end_orbits[0], centralizer, tqdm_desc=f"translation {start_translation_str} --> {end_translation_str}")]
    for start_num, start_orbit, end_num, end_orbit in zip(start_tuple, start_orbits[1:], end_tuple, end_orbits[1:]):
        orbits_pairs.append(find_orbit_pairs(start_num, start_orbit, end_num, end_orbit, centralizer, tqdm_desc=f"{start_num} --> {end_num}"))

    return orbits_pairs


# recursive helper function for finding transitions
# builds up the columns of B0 and B1 in a depth first manner
def find_transition_helper(prevCentralizer, prevB0, prevB1, orbits_pairs, tqdm_desc=""):
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
        if equation_is_true_or_solvable(curr_eq):
            curr_solution = sp.solve(curr_eq)
            if len(curr_solution) == 0:
                curr_centralizer = prevCentralizer
            else:
                curr_centralizer = prevCentralizer.subs(curr_solution.items())

            if curr_centralizer.det() != 0:
                curr_centralizer, B0, B1 = find_transition_helper(curr_centralizer, B0, B1, orbits_pairs)
                if curr_centralizer is not None and B0.shape[1] == len(orbits_pairs):
                    return curr_centralizer, B0, B1

    return None, None, None


# find a transition from (n_1, n_2, ..., n_k) to (m_1, m_2, ..., m_k)
def find_transition(start_tuple, end_tuple, centralizer, centralizer_str):
    orbits_pairs = find_multiple_orbit_pairs(start_tuple, end_tuple, centralizer)

    results = []
    pbar = tqdm(total=len(orbits_pairs[0]), desc=f"Finding transitions for {start_tuple} --> {end_tuple} under {centralizer_str}")

    # this function is called when a parallel process is finished
    def collect_result(result):
        pbar.update(1)
        pbar.refresh()
        if result != (None, None, None):
            results.append((start_tuple,) + (end_tuple,) + result)

    with multiprocessing.Pool() as pool:
        for translation_pair in orbits_pairs[0]:
            t0, t1 = translation_pair
            B0 = sp.Matrix([]).col_insert(0, t0)
            B1 = sp.Matrix([]).col_insert(0, t1)
            pool.apply_async(find_transition_helper, args=(centralizer, B0, B1, orbits_pairs), callback=collect_result)

        pool.close()
        pool.join()
        pbar.close()
        return results


def get_pickle_filename(pickle_dir, start_tuple, end_tuple, centralizer_string):
    # add / to directory string if it is not there
    if pickle_dir[-1] != "/":
        pickle_dir = pickle_dir + "/"

    return re.sub('[()\[\] ]', '', pickle_dir + f"{start_tuple}_to_{end_tuple}_{centralizer_string}.pickle")


def save_transitions(pickle_dir, start_tuple, end_tuple, centralizer_string, transitions):
    with open(get_pickle_filename(pickle_dir, start_tuple, end_tuple, centralizer_string), 'wb') as write_file:
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
    centralizer = centralizers.get_centralizer_from_str(centralizer_str)


    def create_tuple(arg_str):
        tup = map(int, arg_str.split(','))
        return list(tup)

    if args.pt_ar is not None:
        stime = time.time()
        start_tuple, end_tuple = list(map(create_tuple, args.pt_ar))

        transitions = find_transition(start_tuple, end_tuple, centralizer, centralizer_str)
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

            pickle_filename = get_pickle_filename(args.pickle_dir, start_tuple, end_tuple, centralizer_str)

            # if we are not redoing cases skip it if it's already done
            if not args.redo and file_exists(pickle_filename):
                print(f"Case {start_tuple} --> {end_tuple} is already done in {pickle_filename}\n")
                continue

            print(f"Starting case {start_tuple} --> {end_tuple}...")
            transitions = find_transition(start_tuple, end_tuple, centralizer, centralizer_str)
            print(f"Number of transitions for {start_tuple} --> {end_tuple} under {centralizer_str} is {len(transitions)}")
            save_transitions(args.pickle_dir, start_tuple, end_tuple, centralizer_str, transitions)
            etime = time.time()
            print(f"Case {start_tuple} --> {end_tuple} done in{etime - stime : .3f} seconds.")
            print()

        total_etime = time.time()
        print(f"All cases completed in{total_etime - total_stime : .3f} seconds.")