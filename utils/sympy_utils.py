import sympy as sp


def equation_is_true_or_solvable(eq):
    return eq == True or len(sp.solve(eq)) > 0
