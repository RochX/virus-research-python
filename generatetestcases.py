from virusdata import virusdata
import itertools
from permutetestcases import tuple_to_case


def main():
    writeOneBaseCases()
    writeTwoBaseCases()


def writeOneBaseCases():
    print("Writing One Base Cases...")
    with open('one_base_cases.txt', 'w') as one_base_file:
        for a, b in itertools.product(range(1, 56), range(1, 56)):
            one_base_file.write(f"{a} > {b}\n")

    print("Done.")


def writeTwoBaseCases():
    two_base_point_arrays = getAllTwoBasePointArrays()
    print("Writing Two Base Cases...")
    with open('two_base_cases.txt', 'w') as two_base_file:
        for p0, p1 in itertools.product(two_base_point_arrays, two_base_point_arrays):
            if twoBasePointArrayIsRedundant(p0, p1):
                continue

            two_base_file.write(tuple_to_case(p0, p1))
            two_base_file.write("\n")

    print("Done.")


def getAllTwoBasePointArrays():
    two_base_point_arrays = []
    for a, b in itertools.product(range(1, 56), range(1, 56)):
        if isValidPointArray((a, b)):
            two_base_point_arrays.append((a, b))

    return two_base_point_arrays


def twoBasePointArrayIsRedundant(p0, p1):
    a, b = p0
    c, d = p1

    # two base point array is actually one base
    if a == b and c == d:
        return True

    # point array maps to itself
    if p0 == p1:
        return True

    # only need to check when the first point array has a < b
    if a >= b:
        return True

    return False


def isValidPointArray(point_array):
    try:
        virusdata.getGenerators(point_array)
        return True
    except ValueError:
        return False


if __name__ == "__main__":
    main()
