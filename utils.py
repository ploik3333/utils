import asyncio
import atexit
import math
import time
from typing import Generator

import dotenv
import matplotlib.pyplot as plt
import numpy as np

dotenv.load_dotenv()

flatten = lambda l: sum(map(flatten,l),[]) if isinstance(l, list | tuple) else [l]
constrain = lambda v, l, u: min(max(v, l), u)

async def prefetch(gen, buffer_size=10):
    queue = asyncio.Queue(maxsize=buffer_size)

    async def worker():
        async for item in gen:
            await queue.put(item)
        await queue.put(StopAsyncIteration)

    worker_task = asyncio.create_task(worker())
    while True:
        val = await queue.get()
        if val is StopAsyncIteration:
            break
        yield val


def window(*args, **kwargs) -> Generator[tuple[int | float, int | float], None, None]:
    def _window(start: int, end: int, size: int, overlap: int = 0, include_extra: bool = True) -> Generator[
        tuple[int, int], None, None]:
        if size <= 0 or overlap >= size: raise ValueError("Invalid size")
        i = start
        while i < end:
            if not include_extra and end - i < size: break
            yield i, min(i + size, end)
            i += size - overlap

    required = len(args) + sum([1 for x in ['start', 'end', 'size'] if x in kwargs])

    if required == 3:
        return _window(*args, **kwargs)
    elif required == 2:
        return _window(0, *args, **kwargs)
    raise NotImplementedError("Use implemented parameters: (start, end, size) OR (end, size)")


def whitespace_encode(text: str) -> str:
    b = lambda b: bin(ord(b))
    c = lambda c, b=16: chr(int(c, b))
    d = {'0': c('200B'), '1': c('200C')}
    return c('200D').join(["".join(map(d.get, b(a)[2:])) for a in text])


def whitespace_decode(text: str) -> str:
    c = lambda c, b=16: chr(int(c, b))
    d = {'0': c('200B'), '1': c('200C')}
    e = {d[a]: a for a in d}
    return "".join([*map(lambda f: c("".join([*map(e.get, f)]), 2), text.split(c('200D')))])


def toBase(num: int, base: int, digits: str = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
    if num == 0: return "0"
    if base == 1:
        return "1" * num
    assert base > 0
    result = ""
    digits = digits.upper()
    for i in range(math.floor(math.log(num, base)), -1, -1):
        j, num = divmod(num, base ** i)
        result += digits[j]
    return result


def fromBase(num, base, digits="0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
    num = num.upper()
    digits = digits.upper()
    assert base > 0
    if num == "0": return 0
    d = {digits[i]: i for i in range(len(digits))}
    output = 0
    for i in range(len(num)):
        output += d[num[i]] * base ** (len(num) - i - 1)

    return output


def toAscii(text: str, base: int = 2, sep: str = " ", pad=8):
    return sep.join(f"{toBase(ord(x), base):>0{pad}}" for x in text)


def fromAscii(text: str, base: int = 2, sep: str = " "):
    return "".join(chr(fromBase(x, base)) for x in text.split(sep))


def get(arr, indexes):
    if len(indexes) > 1:
        return get(arr[indexes.pop(0)], indexes)
    return arr[indexes[0]]


def primes_documentation():
    print("""
    import cyprimes
    print(f"{cyprimes.max_ulong = :_}")
    
    cyprimes.Primes(max_value).
    index(number): Returns the index of number. Raises ValueError if number is not prime.
    next(number): Returns the next prime number after number or None if their is none in the given range.
    previous(number): Returns the previous prime number before number or None if their is none in the given range.
    between(start, end): Returns a tuple with all prime numbers in the closed interval [start, end].
    
    # SPEEEEEEEEEDY !!!
    cyprimes.is_prime(number)
    cyprimes.next_prime(number):
    cyprimes.previous_prime(number)
    cyprimes.primes_between(start, end)
    """)


def discord_log(text):
    import requests
    import os

    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    data = {"content": text}
    response = requests.post(webhook_url, json=data)


def log_time_setup():
    start = time.time()

    def log_time(start):
        print(f"Took {time.time() - start} seconds.")

    def stop():
        atexit.unregister(log_time)
        log_time(start)

    log_time_setup.stop = stop
    atexit.register(log_time, start)

def rangef(*args):
    def _rangef(start, stop, step:int|float = 1):
        while start < stop if step > 0 else start > stop:
            yield start
            start = step  + start
    if len(args) == 1:
        return _rangef(0, args[0])
    elif len(args) == 2 or len(args) == 3:
        return _rangef(*args)
    else:
        raise ValueError("Invalid number of arguments")

class Timer:
    def __init__(self, _func: Callable|None = None, trials:int = 1):
        self._func = _func
        self.trials = trials
        self.time = None

        if _func is not None:
            update_wrapper(self, _func)

    def wrapper(self, *args, **kwargs):
        self.time = time.perf_counter()
        for _ in range(self.trials):
            result = self._func(*args, **kwargs)
        print(f"{self._func.__name__} took {(time.perf_counter() - self.time) / self.trials} seconds" + (" on avg" if self.trials > 1 else ""))
        return result
    def log(self, text):
        if self.time is None:
            raise UserWarning("Calling log before initialized")
        try:
            print(text % (time.perf_counter() - self.time))
        except TypeError:
            print(text)

    def __call__(self, *args, **kwargs):
        if self._func is None:
            return self.__class__(*args, trials=self.trials, **kwargs)
        return self.wrapper( *args, **kwargs)

class SlopeField:
    def __init__(self, function, *args, dx=None, dy=None):
        self.f = function
        self.setBounds(*args)


    def setBounds(self, *args):
        match len(args):
            case 1:
                self.minx = args[0][0]
                self.maxx = args[0][1]
                self.miny = args[0][0]
                self.maxy = args[0][1]
            case 2:
                self.minx = args[0][0]
                self.maxx = args[0][1]
                self.miny = args[1][0]
                self.maxy = args[1][1]
            case 4:
                self.minx = args[0]
                self.maxx = args[1]
                self.miny = args[2]
                self.maxy = args[3]
            case _:
                raise ValueError(f"Invalid number of arguments for bounds. Given {len(args)}")
    def getPoint(self, x,y=None):
        if y is None:
            return x
        return (x,y)

    def slopefield(self, dx: float = 0.5, dy: float = .5) -> SlopeField:
        """
        f = lambda x,y:x*y-np.cos(x)
        SlopeField(f, [-10, 10]).slopefield(1, 1).plotcase(2,2)

        plt.show()
        """
        t = np.arange(self.minx, self.maxx, dx)
        y = np.arange(self.miny, self.maxy, dy)
        L = 0.7*min(dx, dy)
        for i in range(len(t)):
            for j in range(len(y)):
                slope = self.f(t[i],y[j])
                theta = np.arctan(slope)
                dt = L*np.cos(theta)
                dy = L*np.sin(theta)
                plt.plot([t[i] - dt/2,t[i] + dt/2],[y[j] - dy/2,y[j] + dy/2], 'b')
        return self

    def plotcase(self, *args, dx: float = 0.1) -> SlopeField:
        points = []

        x, y = self.getPoint(*args)
        while x > self.minx if dx > 0 else x < self.minx:
            if self.maxy > y > self.miny: points.append((x, y))
            if np.isnan(x) or np.isnan(y): break
            dydx = self.f(x, y)
            y -= dydx * dx
            x -= dx

        points = list(reversed(points))

        x, y = self.getPoint(*args)
        while x < self.maxx if dx > 0 else x > self.maxx:
            if self.maxy > y > self.miny: points.append((x, y))
            if np.isnan(x) or np.isnan(y): break

            dydx = self.f(x, y)
            y += dydx * dx
            x += dx

        if len(points) > 0:
            plt.plot( *zip(*points), c='black')
        return self

class dotdict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


import typing

class Threads:
    _threads = []

    @classmethod
    def add(cls, other):
        other.start()
        return cls._threads.append(other)

    @classmethod
    def stop(cls):
        for t in cls._threads:
            if hasattr(t, 'stop') and isinstance(t.stop, typing.Callable):
                t.stop() # assume a .stop method for each thread with cleanup
        for t in cls._threads:
            t.join()