from functools import cmp_to_key


def vec_comp(v1, v2):
    for k, l in zip(v1, v2):
        if (k != l):
            return k - l
    return 0


def orbitOfVector(matrices, vector):
    orbit = []

    for M in matrices:
        if M*vector not in orbit:
            orbit.append(M * vector)

    orbit.sort(key=cmp_to_key(vec_comp))
    return orbit
