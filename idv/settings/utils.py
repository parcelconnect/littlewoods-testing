import os


def env_as_bool(var, default=False):
    """
    Read the variable from the environment as a bool.
    """
    if var not in os.environ:
        return default

    try:
        value = os.environ[var].lower()
    except KeyError:
        return default
    return value in ['true', '1', 'yes']
