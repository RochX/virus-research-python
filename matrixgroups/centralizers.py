from matrixgroups import a4group, d10group, d6group


def get_centralizer_str_from_matrix(centralizer):
    if centralizer == d6group.centralizer():
        return "D6"
    elif centralizer == d10group.centralizer():
        return "D10"
    elif centralizer == a4group.centralizer():
        return "A4"
    else:
        raise ValueError("Centralizer is not A4, D10, or D6")


def get_centralizer_from_str(centralizer_str):
    centralizer_str = centralizer_str.upper()

    if centralizer_str == "A4":
        return a4group.centralizer()
    elif centralizer_str == "D10":
        return d10group.centralizer()
    elif centralizer_str == "D6":
        return d6group.centralizer()
    else:
        raise ValueError("Centralizer String is not A4, D10, or D6")


def is_centralizer(matrix):
    if matrix in [a4group.centralizer(), d10group.centralizer(), d6group.centralizer()]:
        return True

    return False
