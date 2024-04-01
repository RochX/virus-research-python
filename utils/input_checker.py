def is_tuple_of_ints(var):
    if not isinstance(var, tuple):
        return False

    return all(isinstance(item, int) for item in var)


def is_generating_list(var):
    return isinstance(var, int) or is_tuple_of_ints(var)


def can_be_generating_list(var):
    """
    Checks whether `var` can be converted into a generating list
    :param var: The input to check.
    :return: True or False if `var` is an int or a tuple of ints
    """
    try:
        if isinstance(var, int):
            return True

        if is_tuple_of_ints(var):
            return True

        var = str(var)
        var = var.replace("(", "").replace(")", "")
        _ = tuple(int(x) for x in var.split(","))
        return True
    except ValueError:
        return False


def convert_to_generating_list(var):
    """
    Converts `var` to a generating list.
    :param var: Input variable.
    :return: An int or a tuple of ints to represent a generating list.
    :raise: ValueError if `var` cannot be converted to an int or a tuple of ints
    """
    if isinstance(var, int) or is_tuple_of_ints(var):
        return var
    else:
        var = str(var)
        var = var.replace("(", "").replace(")", "")

        generating_list = tuple(int(x) for x in var.split(","))

        # handle 1 element case
        if len(generating_list) == 1:
            generating_list = generating_list[0]

        return generating_list


def is_centralizer_string(user_input):
    return user_input in ["A4", "D10", "D6"]
