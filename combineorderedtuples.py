import sympy as sp
from virusdata import virusconfigurations

if __name__ == "__main__":
    sp.init_printing()
    sp.pprint(virusconfigurations.configs[1])