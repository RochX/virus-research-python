import fabric
import patchwork.files
import sys
import os
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

    os.makedirs("downloads", exist_ok=True)
    connection.get(filepath, local="downloads/")
    return True


if __name__ == "__main__":
    jigwe_hostname = "jigwe.kzoo.edu"

    try:
        ssh_config_setup = verify_ssh_config_is_setup(jigwe_hostname)
    except FileNotFoundError as e:
        ssh_config_setup = False
        print(e)

    if not ssh_config_setup:
        print(f"Host '{jigwe_hostname}' is not set up within the SSH configuration file.\n"
              f"See README for details on how to set it up.")
        sys.exit(0)

    with fabric.Connection(host=jigwe_hostname) as jigwe:
        # this raises FileNotFoundError
        download_from_remote(jigwe, "/scratch/xavier/virus_research/python/two_base_b0_b1_pickles/doesntexist")
