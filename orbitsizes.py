# this program computes the ICO orbit sizes of the 55 standard 1 base point arrays
from matrixgroups import icosahedralgroup
from virusdata import virusdata

if __name__ == "__main__":
    BASE_STR = virusdata.BASE_STR
    TRANSLATION_STR = virusdata.TRANSLATION_STR
    for i in range(1, 56):
        base_ico_orbit = icosahedralgroup.orbitOfVector(virusdata.configs[i][BASE_STR])
        translation_ico_orbit = icosahedralgroup.orbitOfVector(virusdata.configs[i][TRANSLATION_STR])
        print(f"{i} orbit sizes (t, v):\t{len(translation_ico_orbit)}\t{len(base_ico_orbit)}")
