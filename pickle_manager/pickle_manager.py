import itertools
import os
import pickle
import re
import sympy as sp
from tqdm.auto import tqdm
import sys
from matrixgroups import icosahedralgroup, centralizers
from virusdata import virusdata


class PickleManager:
    def __init__(self, pickle_directory):
        is_a_directory = os.path.isdir(pickle_directory)
        if not is_a_directory:
            os.mkdir(pickle_directory)

        self.pickle_directory = pickle_directory

    def get_transition_pickle_filename(self, start_tuple, end_tuple, centralizer_string):
        centralizer_string = centralizer_string.upper()
        case_filename = re.sub('[()\[\] ]', '', f"{start_tuple}_to_{end_tuple}_{centralizer_string}.pickle")
        return os.path.join(self.pickle_directory, case_filename)

    def transition_pickle_file_exists(self, start_tuple, end_tuple, centralizer_str):
        pickle_filename = self.get_transition_pickle_filename(start_tuple, end_tuple, centralizer_str)
        return os.path.exists(pickle_filename)

    def get_pickle_data(self, start_tuple, end_tuple, centralizer_string):
        with open(self.get_transition_pickle_filename(start_tuple, end_tuple, centralizer_string), 'rb') as read_file:
            return pickle.load(read_file)


class TransitionPickleManager(PickleManager):
    def save_transitions(self, start_tuple, end_tuple, centralizer_string, transitions):
        with open(self.get_transition_pickle_filename(start_tuple, end_tuple, centralizer_string), 'wb') as write_file:
            pickle.dump(transitions, write_file, protocol=pickle.HIGHEST_PROTOCOL)
            print(f"Saved {start_tuple} --> {end_tuple} under {centralizer_string} to {write_file.name}.")

    # uses one base data to determine whether a given test case is possible
    def check_case_is_possible(self, start_tuple, end_tuple, centralizer_string):
        if not has_same_number_elements(start_tuple, end_tuple):
            return False

        if type(start_tuple) in [int, str] or len(start_tuple) == 1:
            return True

        print("Check if impossible by one base...")
        for start, end in zip(start_tuple, end_tuple):
            try:
                one_base_transitions = self.get_pickle_data(start, end, centralizer_string)
                if len(one_base_transitions) == 0:
                    print(f"{[start]} --> {[end]} under {centralizer_string} is impossible.")
                    return False
            except FileNotFoundError:
                print(f"WARN: File {self.get_transition_pickle_filename(start, end, centralizer_string)} does not exist.")

        print("Possible.")
        return True


# finds what pairs of vectors can be solved by Tv_0 = v_1 while looping over their (ICO) orbits
class VectorPairPickleManager(PickleManager):
    def __init__(self, pickle_dir, centralizer_str):
        super().__init__(pickle_dir)

        self.centralizer_str = centralizer_str
        self.centralizer = centralizers.get_centralizer_from_str(self.centralizer_str)

    # overrides function in PickleManager
    def get_transition_pickle_filename(self, start_tuple, end_tuple, centralizer_string):
        case_filename = re.sub('[()\[\] ]', '', f"{start_tuple}_to_{end_tuple}_{centralizer_string}_pairs.pickle")
        return os.path.join(self.pickle_directory, case_filename)

    def get_multiple_vector_pairs(self, start_tuple, end_tuple, add_in_translation):
        if not has_same_number_elements(start_tuple, end_tuple):
            raise ValueError(f"\"{start_tuple}\" and \"{end_tuple}\" do not have the same number of elements.")

        if add_in_translation:
            start_translation = virusdata.configs[start_tuple[0]][virusdata.TRANSLATION_STR]
            end_translation = virusdata.configs[end_tuple[0]][virusdata.TRANSLATION_STR]

            start_translation_str = virusdata.get_translation_vector_str(start_translation)
            end_translation_str = virusdata.get_translation_vector_str(end_translation)

            start_tuple = [start_translation_str] + start_tuple
            end_tuple = [end_translation_str] + end_tuple

        list_of_vector_pairs = []
        for start, end in zip(start_tuple, end_tuple):
            list_of_vector_pairs.append(self.get_vector_pairs(start, end))

        return list_of_vector_pairs

    def get_vector_pairs(self, start, end):
        sys.stdout.flush()
        function_call_desc = f"{start} --> {end}"

        if self.transition_pickle_file_exists(start, end, self.centralizer_str):
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
        with open(self.get_transition_pickle_filename(start, end, self.centralizer_str), 'wb') as write_file:
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
