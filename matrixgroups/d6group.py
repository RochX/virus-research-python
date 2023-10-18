import sympy as sp


def centralizer():
    x, y, z, t, u, w, v, s = sp.symbols('x y z t u w v s', real=True)
    return sp.Matrix([
        [u, w, -w, x, s, s],
        [-t, y, v, -v, z, -t],
        [t, v, y, v, t, -z],
        [z, -v, v, y, -t, -t],
        [s, x, -w, w, u, s],
        [s, w, -x, w, s, u]])
