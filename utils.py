Prefetch
generator


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


Whitespace
Encoder






def window(*args, **kwargs) -> Generator[tuple[int | float, int | float], None, None]:
    def _window(start: int, end: int, size: int, overlap: int = 0, include_extra: bool = True) -> Generator[
        tuple[int, int], None, None]:
        if size <= 0 or overlap >= size: raise ValueError("Invalid size")
        i = start
        while i < end:
            if not include_extra and end - i < size: break
            yield (i, min(i + size, end))
            i += size - overlap

    required = len(args) + sum([1 for x in ['start', 'end', 'size'] if x in kwargs])

    if required == 3:
        return _window(*args, **kwargs)
    elif required == 2:
        return _window(0, *args, **kwargs)
    raise NotImplementedError("Use implemented parameters: (start, end, size) OR (end, size)")
def whitespace_encode(text:str) -> str:
    b = lambda b: bin(ord(b))
    c = lambda c, b=16: chr(int(c, b))
    d = {'0': c('200B'), '1': c('200C')}
    return c('200D').join(["".join(map(d.get, b(a)[2:])) for a in text])
def whitespace_decode(text: str) -> str:
    c = lambda c, b=16: chr(int(c, b))
    d = {'0': c('200B'), '1': c('200C')}
    e = {d[a]: a for a in d}
    return "".join([*map(lambda f: c("".join([*map(e.get, f)]), 2), text.split(c('200D')))])


def toBase(num, base, precision=5):
    k = math.floor(math.log(num) / math.log(base)) + 1;
    k = max(0, k)

    digits = []

    for i in range(k - 1, (-1 * precision) - 1, -1):  # (i = k-1; i > (-1*precision)-1; i--):
        digit = math.floor((num / base ** i) % base)
        num -= digit * math.pow(base, i)
        digits.append("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"[digit])

        if (num < 0.1 ** (precision + 1) and i <= 0):
            break

    if (len(digits) > k):
        digits.insert(k, ".")

    return "".join(map(str, digits))


def fromBase(num, base):
    numberSplit = num.split(".")
    numberLength = len(numberSplit[0])

    output = 0
    digits = "".join(numberSplit)

    for i in range(len(digits)):
        output += int("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ".find(digits[i])) * base ** (numberLength - i - 1)

    return output

base = 2 ** .5
a = convert_from_decimal(7, base)
print(a)
print(convert_to_decimal(a, base))


print((lambda: ' '.join(format(ord(c), '08b') for c in "Symbolism in TKAM"))())
print("".join(chr(int(x, 2)) for x in
              "01110100 01101011 01100001 01101101 00100000 01110111 01100001 01110011 00100000 01101010 01110101 01110011 01110100 00100000 01101101 01100101 01101000".split()))

