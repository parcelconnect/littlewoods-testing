import time
from functools import wraps


def retry(tries=3, delay=10, logger=None):
    """
    Retry function. Example:
    @retry(tries=5, delay=60)
    def tmp():
        do something that may raise an exception

    Args:
        tries (int): maximum number of attempts
        delays (int): sleep time between attempts
        logger (logging.Logger obj): logger to be used for logging failures
    """
    def decorator_retry(func):
        @wraps(func)
        def retry_func(*args, **kwargs):
            nonlocal logger
            # rebinding so that we can mutate them
            mtries = tries
            mdelay = delay
            while mtries > 0:
                try:
                    return func(*args, **kwargs)
                except Exception as exc:
                    if logger:
                        msg = "%(exc)s; Retrying in %(delay)s seconds"
                        logger.warning(msg, dict(exc=str(exc), delay=mdelay))
                time.sleep(mdelay)
                mtries -= 1
            if logger:
                logger.error("%s failed after retrying %s times", func, mtries)
        return retry_func
    return decorator_retry
