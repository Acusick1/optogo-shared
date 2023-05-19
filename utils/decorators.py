import asyncio
import logging
import time
import typing
from functools import partial, wraps
from time import sleep
from typing import Type
from typing import Callable

POLL_FREQUENCY = 0.5


def async_retry(ignored_exceptions: typing.Iterable[Type[Exception]], sleep_for: float = POLL_FREQUENCY):
    async def decorator(func: Callable):
        async def wrapper(*args, **kwargs):

            while True:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if isinstance(e, tuple(ignored_exceptions)):
                        await asyncio.sleep(sleep_for)
                        continue
                    else:
                        raise e

        return wrapper

    return decorator


def retry(ignored_exceptions: typing.Iterable[Type[Exception]], sleep_for: float = POLL_FREQUENCY):
    def decorator(func: Callable):
        def wrapper(*args, **kwargs):

            while True:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if isinstance(e, tuple(ignored_exceptions)):
                        sleep(sleep_for)
                        continue
                    else:
                        raise e

        return wrapper

    return decorator


def retry_backoff(func=None, exception=Exception, n_tries=5, delay=5, backoff=1, logger=False):
    """Retry decorator with exponential backoff.

    Parameters
    ----------
    func : typing.Callable, optional
        Callable on which the decorator is applied, by default None
    exception : Exception or tuple of Exceptions, optional
        Exception(s) that invoke retry, by default Exception
    n_tries : int, optional
        Number of tries before giving up, by default 5
    delay : int, optional
        Initial delay between retries in seconds, by default 5
    backoff : int, optional
        Backoff multiplier e.g. value of 2 will double the delay, by default 1
    logger : bool, optional
        Option to log or print, by default False

    Returns
    -------
    typing.Callable
        Decorated callable that calls itself when exception(s) occur.
    """

    if func is None:
        return partial(
            retry_backoff,
            exception=exception,
            n_tries=n_tries,
            delay=delay,
            backoff=backoff,
            logger=logger,
        )

    @wraps(func)
    def wrapper(*args, **kwargs):
        ntries, ndelay = n_tries, delay

        while ntries > 1:
            try:
                return func(*args, **kwargs)
            except exception as e:
                msg = f"{str(e)}, Retrying in {ndelay} seconds..."
                if logger:
                    logging.warning(msg)
                else:
                    print(msg)
                time.sleep(ndelay)
                ntries -= 1
                ndelay *= backoff

        return func(*args, **kwargs)

    return wrapper
