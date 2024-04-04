from virusdata import virusdata


def has_same_number_elements(start_tuple, end_tuple):
    try:
        return len(start_tuple) == len(end_tuple)
    except TypeError:
        if type(start_tuple) != type(end_tuple):
            return False

        assert type(start_tuple) in [int, str]
        return True


def is_valid_generating_list(tup):
    """
    Returns True/False if a generating list represents a point array
    (i.e. they share the same translation vector).
    """
    try:
        virusdata.get_generators(tup)
        return True
    except ValueError:
        return False
