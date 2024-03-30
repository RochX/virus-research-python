import argparse
import itertools
import re


def create_tuple(arg_str):
    tup = map(int, arg_str.split(','))
    return list(tup)


def tuple_to_case(start_tuple, end_tuple):
    case_str = ""
    case_str += re.sub("[\[\]\(\)]", '', str(start_tuple))
    case_str += " > "
    case_str += re.sub("[\[\]\(\)]", '', str(end_tuple))
    return case_str


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Permutes the transition test cases within a given file.",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("case_file", help="File to permute test cases of.")
    args = parser.parse_args()

    # add "_permuted" before the extension
    filename_split = args.case_file.split(".")
    filename_split[-2] += "_permuted"
    permute_filename = ".".join(filename_split)

    cases = []

    # read in the cases
    with open(args.case_file, 'r') as read_file:
        for line in read_file.readlines():
            # this is assuming each line in file looks like:
            # n_1, n_2, ..., n_k > m_1, m_2, ..., m_l
            start_tuple, end_tuple = list(map(create_tuple, line.strip().split(' > ')))
            cases.append((start_tuple, end_tuple))
            print("case str:", tuple_to_case(cases[-1][0], cases[-1][1]))

    with open(permute_filename, 'w') as write_file:
        for case in cases:
            start_tuple, end_tuple = case
            assert (len(start_tuple) == len(end_tuple))

            if len(start_tuple) == 1:
                one_base = tuple_to_case(start_tuple, end_tuple)
                print(f"Writing {one_base} to {write_file.name}")
                write_file.write(one_base + "\n")
                continue

            done_permutations = []
            for permuted_end in itertools.permutations(end_tuple):
                if permuted_end in done_permutations:
                    continue

                permuted_case = tuple_to_case(start_tuple, permuted_end)
                print(f"Writing {permuted_case} to {write_file.name}")
                write_file.write(permuted_case + "\n")
                done_permutations.append(permuted_end)
