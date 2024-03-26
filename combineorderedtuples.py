import argparse
import sys
import sympy as sp
import multiprocessing
import time
from tqdm.auto import tqdm
from matrixgroups import centralizers
from pickle_manager.pickle_manager import TransitionPickleManager, VectorPairPickleManager


# checks if a sympy equation is either true or solvable
def equation_is_true_or_solvable(eq):
    return eq == True or len(sp.solve(eq)) > 0


# recursive helper function for finding transitions
# builds up the columns of B0 and B1 in a depth first manner
def find_transition_helper(prevCentralizer, prevB0, prevB1, orbits_pairs, tqdm_desc=""):
    num_curr_b0_cols = prevB0.shape[1]
    assert (prevB0.shape[1] == prevB1.shape[1])

    if num_curr_b0_cols == len(orbits_pairs):
        return prevCentralizer, prevB0, prevB1

    for pair in orbits_pairs[num_curr_b0_cols]:
        v0, v1 = pair
        B0 = prevB0.col_insert(num_curr_b0_cols, v0)
        B1 = prevB1.col_insert(num_curr_b0_cols, v1)

        # check for linear independence within the columns of B0 and B1
        if B0.rank() != num_curr_b0_cols+1 or B1.rank() != num_curr_b0_cols+1:
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
    sys.stdout.flush()

    PAIR_DIR = "vector_pairs"
    vector_pair_pickle_manager = VectorPairPickleManager(PAIR_DIR, centralizer_str)
    orbits_pairs = vector_pair_pickle_manager.get_multiple_vector_pairs(start_tuple, end_tuple, add_in_translation=True)

    results = []
    pbar = tqdm(total=len(orbits_pairs[0]),
                desc=f"Finding transitions for {start_tuple} --> {end_tuple} under {centralizer_str}")

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


def create_generating_list(arg_str):
    tup = map(int, arg_str.split(','))
    return list(tup)


def find_transitions_from_cmd_line(args, transition_pickle_manager):
    stime = time.time()
    start_generating_list, end_generating_list = list(map(create_generating_list, args.pt_ar))
    transitions = find_transition(start_generating_list, end_generating_list, centralizer, centralizer_str)
    for res in transitions:
        sp.pprint(res)
        print()
    print(
        f"Number of transitions for {start_generating_list} --> {end_generating_list} under {centralizer_str} is {len(transitions)}")
    transition_pickle_manager.save_transitions(start_generating_list, end_generating_list, centralizer_str, transitions)
    etime = time.time()
    print(f"Done in{etime - stime : .3f} seconds.")


def find_transitions_from_case_file(args, transition_pickle_manager):
    total_stime = time.time()
    cases = []
    with open(args.case_file, 'r') as read_file:
        for line in read_file.readlines():
            # this is assuming each line in file looks like:
            # n_1, n_2, ..., n_k > m_1, m_2, ..., m_l
            start_generating_list, end_generating_list = list(map(create_generating_list, line.strip().split(' > ')))
            cases.append((start_generating_list, end_generating_list))
    for case in cases:
        stime = time.time()
        start_generating_list, end_generating_list = case

        # if we are not redoing cases skip it if it's already done
        if not args.redo and transition_pickle_manager.transition_pickle_file_exists(start_generating_list,
                                                                                     end_generating_list,
                                                                                     centralizer_str):
            transition_pickle_filename = transition_pickle_manager.get_transition_pickle_filename(start_generating_list,
                                                                                                  end_generating_list,
                                                                                                  centralizer_str)
            print(
                f"Case {start_generating_list} --> {end_generating_list} is already done in {transition_pickle_filename}\n")
            continue

        print(f"Starting case {start_generating_list} --> {end_generating_list}...")
        if transition_pickle_manager.check_case_is_possible(start_generating_list, end_generating_list,
                                                            centralizer_str):
            transitions = find_transition(start_generating_list, end_generating_list, centralizer, centralizer_str)
        else:
            print(f"{start_generating_list} --> {end_generating_list} impossible by one base.")
            transitions = []
        print(
            f"Number of transitions for {start_generating_list} --> {end_generating_list} under {centralizer_str} is {len(transitions)}")
        transition_pickle_manager.save_transitions(start_generating_list, end_generating_list, centralizer_str,
                                                   transitions)
        etime = time.time()
        print(f"Case {start_generating_list} --> {end_generating_list} done in{etime - stime : .3f} seconds.")
        print()
    total_etime = time.time()
    print(f"All cases completed in{total_etime - total_stime : .3f} seconds.")


if __name__ == "__main__":
    sp.init_printing()

    centralizer_strings = ["a4", "d10", "d6"]
    parser = argparse.ArgumentParser(description="Finds icosahedral virus transitions between point arrays.", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-d", "--pickle_dir", default="transitions", help="Directory in which the files will be saved. Creates a default \"transitions\" directory if none specified.")
    parser.add_argument("-c", "--centralizer", type=str.lower, choices=centralizer_strings, required=True, help="Select the centralizer to be used.")
    parser.add_argument("-r", "--redo", action="store_true", help="Does all cases given, even if they have already been done before.")
    cases_group = parser.add_mutually_exclusive_group(required=True)
    cases_group.add_argument("--pt-ar", type=str, nargs=2, help="Input the numerical representations of the point arrays")
    cases_group.add_argument("--case-file")
    args = parser.parse_args()

    # initialize the pickle manager class
    transition_pickle_manager = TransitionPickleManager(args.pickle_dir)

    # get centralizer
    centralizer_str = args.centralizer.upper()
    centralizer = centralizers.get_centralizer_from_str(centralizer_str)

    if args.pt_ar is not None:
        find_transitions_from_cmd_line(args, transition_pickle_manager)
    elif args.case_file is not None:
        find_transitions_from_case_file(args, transition_pickle_manager)