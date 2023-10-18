import sympy as sp


def centralizer():
    x, y, z, t, u, w, v, s = sp.symbols('x y z t u w v s', real=True)
    return sp.Matrix([
        [z, x, y, y, x, t],
        [x, z, x, y, y, t],
        [y, x, z, x, y, t],
        [y, y, x, z, x, t],
        [x, y, y, x, z, t],
        [u, u, u, u, u, w]])
