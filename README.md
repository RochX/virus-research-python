# virus-research-python
This repository is for the research that I (Xavier Silva) am doing from Summer 2023 - Summer 2024.

## The Research
The research involves finding transitions between states of icosahedral viruses that preserve various types of icosahedral symmetry.
Finding these transitions involves solving matrix equations of the form `TB_0 = B_1` for `T`.
`T` is a general form of a 6x6 matrix which depends on which symmetry we are searching for.

## How To Use The Program
This repository consists of one main python script to run and two helper python scripts.
The main script is `combineorderedtuples.py`.

The two helper scripts are `permutetestcases.py` and `picklestocsv.py`.

Running any of them with the `-h` or `--help` flag with give more information on how to use them.

## SSH Getter
This code has been running remotely on the Kalamazoo College supercomputing cluster Jigwe (pronouced 'Cheekua', Potawatomi for Thunderbird).
In order to retrieve results from Jigwe in a user-friendly fashion, the `ssh_getter.py` code allows one to get results from Jigwe.
However, it order to use it, one must set up the SSH configuration file.
This file is typically located in `~/.ssh/config`.
If this file does not exist then create it (e.g. `touch ~/.ssh/config`).
Then add the following lines to the SSH configuration file:
```
Host jigwe.kzoo.edu
    AddKeysToAgent yes
    IdentityFile ~/.ssh/MY_PRIVATE_KEY
    User MY_USER
```
and replacing `MY_PRIVATE_KEY` with the path to your private key for Jigwe and `MY_USER` with the username you logon to Jigwe with.
After doing this the program should work as expected.
Note that one can manually verify that this worked by running `ssh jigwe.kzoo.edu`.
If you have set up the configuration file correctly, this will now have the same effect as running `ssh USER@jigwe.kzoo.edu -i ~/.ssh/MY_PRIVATE_KEY`.

See [https://linuxize.com/post/using-the-ssh-config-file/](https://linuxize.com/post/using-the-ssh-config-file/) for more information on setting up the SSH configuration file.

IMPORTANT NOTE: Because the `fabric` module relies on the `imp` module, the SSH getter **will not** work with Python 3.12 (at least until `fabric` is updated).

### GUI
The `gui.py` folder is a graphical interface for the SSH getter.
It uses the `tkinter` module for creating the interface.