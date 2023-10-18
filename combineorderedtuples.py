import sympy as sp
from virusdata import virusdata
from matrixgroups import icosahedralgroup, a4group, d10group, d6group

if __name__ == "__main__":
    sp.init_printing()
    sp.pprint(virusdata.configs[12])
    sp.pprint(a4group.centralizer())
    sp.pprint(d10group.centralizer())
    sp.pprint(d6group.centralizer())

    sp.pprint(icosahedralgroup.orbitOfVector(virusdata.configs[11][virusdata.TRANSLATION_STR]))
