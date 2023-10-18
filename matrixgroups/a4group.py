import sympy as sp

def centralizer():
    x, y, z, t, u, w, v, s = sp.symbols('x y z t u w v s', real=True)
    return sp.Matrix([
        [z, -x, -y, -t, t, -x],
        [t, z, t, x, x, y],
        [-y, -x, z, t, -t, -x],
        [x, -t, -x, z, y, t],
        [-x, -t, x, y, z, t],
        [t, y, t, -x, -x, z]])
