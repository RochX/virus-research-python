import argparse
import csv
from os import listdir
from os.path import isfile, join
from os.path import exists as file_exists
import pickle


def get_elements_from_pickle_filename(f):
    vals = f[:-7].split("_")
    vals.remove("to")
    return vals


if __name__ == "__main__":
    centralizer_strings = ["a4", "d10", "d6"]
    parser = argparse.ArgumentParser(description="Interprets icosahedral virus transitions pickle files and produces a CSV file showing what is and isn't possible under various symmetries.",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("output_file", help="Name of output csv file.")
    parser.add_argument("-d", "--pickle-dir", default="./",
                        help="Directory in which the files will be read from. Defaults to current working directory.")
    args = parser.parse_args()

    pickles = [f for f in listdir(args.pickle_dir) if isfile(join(args.pickle_dir, f)) and f.endswith(".pickle")]

    cases = list(map(get_elements_from_pickle_filename, pickles))

    results_dict = {}
    for case, pickle_file in zip(cases, pickles):
        start, end, centralizer_str = case
        results_dict.setdefault(start, {})
        results_dict[start].setdefault(end, {})
        with open(join(args.pickle_dir, pickle_file), 'rb') as read_pickle:
            transitions = pickle.load(read_pickle)

            # eventually it may be useful to replace this line with the commented one below:
            results_dict[start][end][centralizer_str] = len(transitions) != 0
            # results_dict[start][end][centralizer_str] = len(transitions)

    csv_header = ("start", "end", "A4", "D10", "D6")
    csv_lst = [csv_header]
    
    for start_key in results_dict.keys():
        for end_key in results_dict[start_key].keys():
            A4_status = results_dict[start_key][end_key].get("A4")
            D10_status = results_dict[start_key][end_key].get("D10")
            D6_status = results_dict[start_key][end_key].get("D6")

            csv_lst.append((start_key, end_key, A4_status, D10_status, D6_status))

    csv_lst[1:] = sorted(csv_lst[1:])

    with open(args.output_file, 'w') as csv_file:
        csv_writer = csv.writer(csv_file)
        for data in csv_lst:
            csv_writer.writerow(data)
            print(data)

        print(f"\nThe above was written to {csv_file.name}.")