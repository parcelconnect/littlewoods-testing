def enum_to_choices(enum):
    """
    Convert an enum to a tuple that can be passed as a `choices` argument
    to a model.

    Args:
        enum (enum.Enum)
    Returns:
        tuple of (value, uppercase key name) tuples.

    """
    return tuple([
        (member.value, member.name.upper())
        for member in enum
    ])
