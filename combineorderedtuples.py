import sympy as sp
from virusdata import virusconfigurations
from matrixgroups import a4group, d10group, d6group

if __name__ == "__main__":
    sp.init_printing()
    sp.pprint(virusconfigurations.configs[1])
    sp.pprint(a4group.centralizer())
    sp.pprint(d10group.centralizer())
    sp.pprint(d6group.centralizer())