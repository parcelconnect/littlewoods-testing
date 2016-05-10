import os


def env_as_bool(var, default=False):
    """Read the variable from the environment as a bool."""
    if var not in os.environ:
        return default

    try:
        value = os.environ[var].lower()
    except KeyError:
        return default
    return value in ['true', '1', 'yes']


def env_as_list(var, default=[]):
    """Read the variable from the environment as a a list."""
    value = os.getenv(var, '')
    if not value:
        return default
    return value.split()
