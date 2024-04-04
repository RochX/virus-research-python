import fabric
import patchwork.files
import sys
import os

from utils import generatinglist_utils, input_checker
from pickle_manager.pickle_manager import TransitionPickleManager
DOWNLOAD_DIR = "downloads/"


# NOTE: requires ~/.ssh/config to be set up...
# Host jigwe.kzoo.edu
#     AddKeysToAgent yes
#     IdentityFile ~/.ssh/xavier_macbook_jigwe
#     User xavier
def verify_ssh_config_is_setup(hostname, ssh_dir="~/.ssh/", ssh_config_filename="config"):
    """
    Returns True/False if hostname is within the ssh config file.
    Defaults to searching for '~/.ssh/config'.
    Raises a FileNotFoundError if the ssh config file does not exist.
    """
    ssh_config_path = os.path.join(os.path.expanduser(ssh_dir), ssh_config_filename)

    if not os.path.exists(ssh_config_path):
        raise FileNotFoundError(f"The SSH config file at path {ssh_config_path} does not exist.")

    with open(ssh_config_path, 'r') as ssh_config:
        ssh_config_contents = ssh_config.read()

        return hostname in ssh_config_contents


def download_from_remote(connection: fabric.Connection, filepath: str):
    """
    Downloads a file from remote.
    Raises a FileNotFoundError if the file doesn't exist on remote.
    :param connection: Fabric connection object.
    :param filepath: Path of file to download from remote.
    :return: True if file successfully downloads.
    """
    if not patchwork.files.exists(connection, filepath):
        raise FileNotFoundError(f"File '{filepath}' doesn't exist on remote '{connection.host}'.")

    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    connection.get(filepath, local=DOWNLOAD_DIR)
    return True


def run_ssh_config_verification(hostname, ssh_dir="~/.ssh/", ssh_config_filename="config"):
    try:
        ssh_config_setup = verify_ssh_config_is_setup(hostname, ssh_dir=ssh_dir, ssh_config_filename=ssh_config_filename)
    except FileNotFoundError as e:
        ssh_config_setup = False
        print(e)

    if not ssh_config_setup:
        print(f"Host '{jigwe_hostname}' is not set up within the SSH configuration file.\n"
              f"See README for details on how to set it up.")
        sys.exit(0)


def get_transitions_from_remote(start_gen_list, end_gen_list, centralizer_str, hostname):
    run_ssh_config_verification(hostname)

    transition_pickle_manager = TransitionPickleManager(pickle_directory=DOWNLOAD_DIR)

    remote_file = transition_pickle_manager.get_transition_pickle_filename(start_gen_list, end_gen_list, centralizer_str, exclude_dir=True)
    remote_path = os.path.join("/scratch/xavier/virus_research/python/two_base_b0_b1_pickles/", remote_file)

    with fabric.Connection(host=hostname) as remote:
        download_from_remote(remote, remote_path)

    return transition_pickle_manager.load_transitions(start_gen_list, end_gen_list, centralizer_str)


def get_centralizer_string_input(input_msg):
    while True:
        user_input = input(input_msg).upper()
        # Check the input condition
        if input_checker.is_centralizer_string(user_input):
            return user_input
        else:
            print("Invalid input. Please try again.")


def get_generating_list_input(input_msg):
    while True:
        user_input = input(input_msg)
        # check if input can be converted properly
        if input_checker.can_be_int_tuple(user_input):
            # check input is an actual point array
            possible_gen_list = input_checker.convert_to_generating_list(user_input)
            if generatinglist_utils.is_valid_generating_list(possible_gen_list):
                return possible_gen_list
            else:
                print("Point array is invalid (translation vector is not shared).")
        else:
            print("Invalid input. Please try again.")


if __name__ == "__main__":
    jigwe_hostname = "jigwe.kzoo.edu"
    run_ssh_config_verification(jigwe_hostname)

    start_gen_list = get_generating_list_input("Enter starting generating list as 'x,y,z,...'\n")
    end_gen_list = get_generating_list_input("Enter ending generating list as 'x,y,z,...'\n")
    centralizer_str = get_centralizer_string_input("Enter centralizer string (A4, D10, D6)\n")

    print(f"Getting transitions from {jigwe_hostname} for desired inputs...")
    print(get_transitions_from_remote(start_gen_list, end_gen_list, centralizer_str, jigwe_hostname))
