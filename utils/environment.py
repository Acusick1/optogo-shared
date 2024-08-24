import os

from config import settings


def env_variable_set(
    required_var: str, error: bool = False, verbose: bool = True
) -> bool:
    """
    Check if an environment variable is set, checking pydantic BaseSettings and os environment
    :param required_var: Environment variable to check
    :param error: Throw error if environment variable not set
    :param verbose: Display message if environment variable not set
    :returns: Boolean defining if environment variable is set
    """
    try:
        set_var = settings.__getattribute__(required_var.lower())
    except AttributeError:
        set_var = os.environ.get(required_var.upper(), None)

    is_set = set_var is not None

    if not is_set:
        message = f"{required_var.upper()} is not set."

        if error:
            raise EnvironmentError(message)
        elif verbose:
            print(message)

    return is_set
