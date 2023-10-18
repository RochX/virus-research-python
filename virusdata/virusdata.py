from sympy import Matrix, Rational

TRANSLATION_STR = "translation"
BASE_STR = "base"

# the use of Rational(1, 2) over 1/2 is used in order for sympy to keep our equations symbolic
configs = {}
TwoD = Matrix([[1, 1, -1, -1, 1, 1],
               [1, 1, 1, -1, -1, 1],
               [-1, 1, 1, 1, -1, 1],
               [-1, -1, 1, 1, 1, 1],
               [1, -1, -1, 1, 1, 1],
               [1, 1, 1, 1, 1, 1]])
D = Rational(1, 2) * TwoD
Dinv = D ** -1
s = Matrix([1, 0, 0, 0, 0, 0])
b = Matrix([Rational(1, 2), Rational(-1, 2), Rational(1, 2), Rational(1, 2), Rational(-1, 2), Rational(1, 2)])
f = Matrix([Rational(1, 2), 0, 0, Rational(-1, 2), 0, 0])

configs[1] = {BASE_STR: D * s, TRANSLATION_STR:  f}
configs[2] = {BASE_STR: Rational(1, 2) * D * D * s, TRANSLATION_STR:  f}
configs[3] = {BASE_STR: s, TRANSLATION_STR:  f}
configs[4] = {BASE_STR: Rational(1, 2) * D * s, TRANSLATION_STR:  f}
configs[5] = {BASE_STR: Rational(1, 2) * s, TRANSLATION_STR:  f}
configs[6] = {BASE_STR: Rational(1, 2) * Dinv * s, TRANSLATION_STR:  f}
configs[7] = {BASE_STR: D * s, TRANSLATION_STR:  b}
configs[8] = {BASE_STR: s, TRANSLATION_STR:  b}
configs[9] = {BASE_STR: Dinv * s, TRANSLATION_STR:  b}
configs[10] = {BASE_STR: Dinv * Dinv * s, TRANSLATION_STR:  b}
configs[11] = {BASE_STR: D * s, TRANSLATION_STR:  s}
configs[12] = {BASE_STR: s, TRANSLATION_STR:  s}
configs[13] = {BASE_STR: Dinv * s, TRANSLATION_STR:  s}
configs[14] = {BASE_STR: D * D * b, TRANSLATION_STR:  f}
configs[15] = {BASE_STR: Rational(1, 2) * D * D * D * b, TRANSLATION_STR:  f}
configs[16] = {BASE_STR: D * b, TRANSLATION_STR:  f}
configs[17] = {BASE_STR: Rational(1, 2) * D * D * b, TRANSLATION_STR:  f}
configs[18] = {BASE_STR: b, TRANSLATION_STR:  f}
configs[19] = {BASE_STR: Rational(1, 2) * D * b, TRANSLATION_STR:  f}
configs[20] = {BASE_STR: Rational(1, 2) * b, TRANSLATION_STR:  f}
configs[21] = {BASE_STR: Rational(1, 2) * Dinv * b, TRANSLATION_STR:  f}
configs[22] = {BASE_STR: D * D * b, TRANSLATION_STR:  b}
configs[23] = {BASE_STR: D * b, TRANSLATION_STR:  b}
configs[24] = {BASE_STR: b, TRANSLATION_STR:  b}
configs[25] = {BASE_STR: Dinv * b, TRANSLATION_STR:  b}
configs[26] = {BASE_STR: Dinv * Dinv * b, TRANSLATION_STR:  b}
configs[27] = {BASE_STR: D * D * b, TRANSLATION_STR:  s}
configs[28] = {BASE_STR: D * b, TRANSLATION_STR:  s}
configs[29] = {BASE_STR: b, TRANSLATION_STR:  s}
configs[30] = {BASE_STR: Dinv * b, TRANSLATION_STR:  s}
configs[31] = {BASE_STR: 2 * D * f, TRANSLATION_STR:  f}
configs[32] = {BASE_STR: D * D * f, TRANSLATION_STR:  f}
configs[33] = {BASE_STR: 2 * f, TRANSLATION_STR:  f}
configs[34] = {BASE_STR: D * f, TRANSLATION_STR:  f}
configs[35] = {BASE_STR: 2 * Dinv * f, TRANSLATION_STR:  f}
configs[36] = {BASE_STR: f, TRANSLATION_STR:  f}
configs[37] = {BASE_STR: Rational(1, 2) * D * f, TRANSLATION_STR:  f}
configs[38] = {BASE_STR: Dinv * f, TRANSLATION_STR:  f}
configs[39] = {BASE_STR: Rational(1, 2) * f, TRANSLATION_STR:  f}
configs[40] = {BASE_STR: Dinv * Dinv * f, TRANSLATION_STR:  f}
configs[41] = {BASE_STR: Rational(1, 2) * Dinv * f, TRANSLATION_STR:  f}
configs[42] = {BASE_STR: 2 * D * f, TRANSLATION_STR:  b}
configs[43] = {BASE_STR: 2 * f, TRANSLATION_STR:  b}
configs[44] = {BASE_STR: 2 * Dinv * f, TRANSLATION_STR:  b}
configs[45] = {BASE_STR: f, TRANSLATION_STR:  b}
configs[46] = {BASE_STR: 2 * Dinv * Dinv * f, TRANSLATION_STR:  b}
configs[47] = {BASE_STR: Dinv * f, TRANSLATION_STR:  b}
configs[48] = {BASE_STR: 2 * Dinv * Dinv * Dinv * f, TRANSLATION_STR:  b}
configs[49] = {BASE_STR: Dinv * Dinv * f, TRANSLATION_STR:  b}
configs[50] = {BASE_STR: 2 * D * f, TRANSLATION_STR:  s}
configs[51] = {BASE_STR: 2 * f, TRANSLATION_STR:  s}
configs[52] = {BASE_STR: 2 * Dinv * f, TRANSLATION_STR:  s}
configs[53] = {BASE_STR: f, TRANSLATION_STR:  s}
configs[54] = {BASE_STR: 2 * Dinv * Dinv * f, TRANSLATION_STR:  s}
configs[55] = {BASE_STR: Dinv * f, TRANSLATION_STR:  s}


def getGenerators(tuple):
    generators = []
    for index, curr in enumerate(tuple):
        # add translation if it doesn't exist
        if index == 0:
            generators.append(configs[curr][TRANSLATION_STR])

        # check if the translation vectors match
        if configs[curr][TRANSLATION_STR] != generators[0]:
            raise ValueError(f"Translation vectors of {curr} and {tuple[0]} do not match.")

        generators.append(configs[curr][BASE_STR])

    return generators
