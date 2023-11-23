import itertools
import os
import pickle
import re
import sympy as sp
from tqdm.auto import tqdm
import sys
from matrixgroups import icosahedralgroup, centralizers
from virusdata import virusdata


class PickleFileNameGetter:
    def __init__(self, pickle_directory):
        is_a_directory = os.path.isdir(pickle_directory)
        if not is_a_directory:
            os.mkdir(pickle_directory)

        self.pickle_directory = pickle_directory

    def get_pickle_filename(self, start_tuple, end_tuple, centralizer_string):
        centralizer_string = centralizer_string.upper()
        case_filename = re.sub('[()\[\] ]', '', f"{start_tuple}_to_{end_tuple}_{centralizer_string}.pickle")
        return os.path.join(self.pickle_directory, case_filename)

    def pickle_file_exists(self, start_tuple, end_tuple, centralizer_str):
        pickle_filename = self.get_pickle_filename(start_tuple, end_tuple, centralizer_str)
        return os.path.exists(pickle_filename)

    def get_pickle_data(self, start_tuple, end_tuple, centralizer_string):
        with open(self.get_pickle_filename(start_tuple, end_tuple, centralizer_string), 'rb') as read_file:
            return pickle.load(read_file)


class TransitionSaverLoader(PickleFileNameGetter):
    def save_transitions(self, start_tuple, end_tuple, centralizer_string, transitions):
        with open(self.get_pickle_filename(start_tuple, end_tuple, centralizer_string), 'wb') as write_file:
            pickle.dump(transitions, write_file, protocol=pickle.HIGHEST_PROTOCOL)
            print(f"Saved {start_tuple} --> {end_tuple} under {centralizer_string} to {write_file.name}.")


# finds what pairs of vectors can be solved by Tv_0 = v_1 while looping over their (ICO) orbits
class VectorPairSaverLoader(PickleFileNameGetter):
    def __init__(self, pickle_dir, centralizer_str):
        super().__init__(pickle_dir)

        self.centralizer_str = centralizer_str
        self.centralizer = centralizers.get_centralizer_from_str(self.centralizer_str)

    # overrides function in PickleFileNameGetter
    def get_pickle_filename(self, start_tuple, end_tuple, centralizer_string):
        case_filename = re.sub('[()\[\] ]', '', f"{start_tuple}_to_{end_tuple}_{centralizer_string}_pairs.pickle")
        return os.path.join(self.pickle_directory, case_filename)

    def get_multiple_vector_pairs(self, start_tuple, end_tuple):
        if not has_same_number_elements(start_tuple, end_tuple):
            raise ValueError(f"\"{start_tuple}\" and \"{end_tuple}\" do not have the same number of elements.")

        list_of_vector_pairs = []
        for start, end in zip(start_tuple, end_tuple):
            list_of_vector_pairs.append(self.get_vector_pairs(start, end))

        return list_of_vector_pairs

    def get_vector_pairs(self, start, end):
        sys.stdout.flush()
        function_call_desc = f"{start} --> {end}"

        if self.pickle_file_exists(start, end, self.centralizer_str):
            print(function_call_desc + " pairs returned from file.")
            return self.get_pickle_data(start, end, self.centralizer_str)

        vector_pairs = self.generate_vector_pairs(start, end)
        self.save_vector_pairs(start, end, vector_pairs)

        return vector_pairs

    def generate_vector_pairs(self, start, end):
        function_call_desc = f"{start} --> {end}"

        start_vector = virusdata.get_single_generator_from_str(start)
        end_vector = virusdata.get_single_generator_from_str(end)

        start_orbit = icosahedralgroup.orbitOfVector(start_vector)
        end_orbit = icosahedralgroup.orbitOfVector(end_vector)

        pair_iterator = tqdm(itertools.product(start_orbit, end_orbit), desc=function_call_desc,
                             total=len(start_orbit) * len(end_orbit))

        vector_pairs = []
        for v0, v1 in pair_iterator:
            if equation_is_true_or_solvable(sp.Eq(self.centralizer * v0, v1)):
                vector_pairs.append((v0, v1))

        return vector_pairs

    def save_vector_pairs(self, start, end, vector_pairs):
        with open(self.get_pickle_filename(start, end, self.centralizer_str), 'wb') as write_file:
            pickle.dump(vector_pairs, write_file)


def equation_is_true_or_solvable(eq):
    return eq == True or len(sp.solve(eq)) > 0


def has_same_number_elements(start_tuple, end_tuple):
    try:
        return len(start_tuple) == len(end_tuple)
    except TypeError:
        if type(start_tuple) != type(end_tuple):
            return False

        assert type(start_tuple) in [int, str]
        return True
