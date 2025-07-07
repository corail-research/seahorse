def _timeout_wrapper(q, func, args, kwargs):
    import sys
    print(f"[timeout] _timeout_wrapper: func={func}, args={args}, kwargs={kwargs}", file=sys.stderr)
    try:
        res = func(*args, **kwargs)
        print(f"[timeout] _timeout_wrapper: success, result={res}", file=sys.stderr)
        q.put((True, res))
    except Exception as e:
        import traceback
        print(f"[timeout] _timeout_wrapper: exception {e}", file=sys.stderr)
        q.put((False, traceback.format_exc()))


import sys
import multiprocessing
import traceback
import asyncio
from seahorse.utils.custom_exceptions import SeahorseTimeoutError


async def run_with_timeout(
    func,
    args=(),
    kwargs=None,
    timeout=1,
    timeout_callback=None,
    exception=SeahorseTimeoutError(),
    is_async=False
):
    """
    Run a function (sync or async) with a timeout.
    - If is_async=True, func must be an async function and will be run with asyncio.wait_for.
    - If is_async=False, func is run in a subprocess and killed if timeout is exceeded.
    Returns the result or raises exception on timeout.
    """
    if kwargs is None:
        kwargs = {}
    if is_async:
        try:
            return await asyncio.wait_for(func(*args, **kwargs), timeout=timeout)
        except asyncio.TimeoutError:
            if timeout_callback:
                timeout_callback()
            raise exception
    else:
        q = multiprocessing.Queue()
        p = multiprocessing.Process(target=_timeout_wrapper, args=(q, func, args, kwargs))
        p.start()
        p.join(timeout)
        if p.is_alive():
            p.terminate()
            p.join()
            if timeout_callback:
                timeout_callback()
            raise exception
        if not q.empty():
            success, result = q.get()
            if success:
                return result
            else:
                raise Exception(f"Exception in subprocess: {result}")
        else:
            raise Exception("Subprocess ended without returning a result. Possible crash, import error, or pickling issue.")
