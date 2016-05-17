def enum_to_choices(enum):
    return tuple([
        (member.value, member.name.upper())
        for member in enum
    ])
