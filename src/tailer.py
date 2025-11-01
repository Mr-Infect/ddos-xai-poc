# src/tailer.py
import time
from watchfiles import awatch, DefaultFilter

async def tail_file(path, poll=1):
    """Simple async tail generator: yields new lines appended to file."""
    with open(path, 'r', errors='ignore') as fh:
        fh.seek(0, 2)
        while True:
            line = fh.readline()
            if line:
                yield line.rstrip('\n')
            else:
                await __async_sleep(poll)

async def __async_sleep(s):
    import asyncio
    await asyncio.sleep(s)
