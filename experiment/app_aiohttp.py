# app_aiohttp.py
import asyncio
import time
from concurrent.futures import ProcessPoolExecutor
from aiohttp import web

CPU_N = 15_000_000

def heavy_cpu_sum():
    return sum(range(1, CPU_N + 1))

async def cpu_blocking(request):
    start = time.time()
    result = heavy_cpu_sum()
    elapsed = time.time() - start
    return web.json_response({'result': result, 'type': 'blocking', 'time': round(elapsed, 2)})

async def cpu_nonblocking(request):
    start = time.time()
    loop = asyncio.get_running_loop()
    with ProcessPoolExecutor(max_workers=1) as pool:
        result = await loop.run_in_executor(pool, heavy_cpu_sum)
    elapsed = time.time() - start
    return web.json_response({'result': result, 'type': 'nonblocking_process', 'time': round(elapsed, 2)})

app = web.Application()
app.router.add_get('/cpu', cpu_blocking)
app.router.add_get('/cpu_fixed', cpu_nonblocking)

if __name__ == '__main__':
    web.run_app(app, host='127.0.0.1', port=8080)