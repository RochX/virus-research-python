import os
import pickle
import re


class TransitionSaverLoader:
    def __init__(self, pickle_directory):
        is_a_directory = os.path.isdir(pickle_directory)
        if not is_a_directory:
            os.mkdir(pickle_directory)

        self.pickle_directory = pickle_directory

    def save_transitions(self, start_tuple, end_tuple, centralizer_string, transitions):
        with open(self.get_pickle_filename(start_tuple, end_tuple, centralizer_string), 'wb') as write_file:
            pickle.dump(transitions, write_file, protocol=pickle.HIGHEST_PROTOCOL)
            print(f"Saved {start_tuple} --> {end_tuple} under {centralizer_string} to {write_file.name}.")

    def get_pickle_filename(self, start_tuple, end_tuple, centralizer_string):
        case_filename = re.sub('[()\[\] ]', '', f"{start_tuple}_to_{end_tuple}_{centralizer_string}.pickle")
        return os.path.join(self.pickle_directory, case_filename)

    def pickle_file_exists(self, start_tuple, end_tuple, centralizer_str):
        pickle_filename = self.get_pickle_filename(start_tuple, end_tuple, centralizer_str)
        return os.path.exists(pickle_filename)
