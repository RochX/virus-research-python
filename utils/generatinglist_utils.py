def has_same_number_elements(start_tuple, end_tuple):
    try:
        return len(start_tuple) == len(end_tuple)
    except TypeError:
        if type(start_tuple) != type(end_tuple):
            return False

        assert type(start_tuple) in [int, str]
        return True
