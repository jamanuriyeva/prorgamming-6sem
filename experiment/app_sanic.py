# app_sanic.py
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
from sanic import Sanic
from sanic.response import json

app = Sanic("CpuTest")

CPU_N = 15_000_000

def heavy_cpu_sum():
    return sum(range(1, CPU_N + 1))

@app.get('/cpu')
async def cpu_blocking(request):
    start = time.time()
    result = heavy_cpu_sum()  # Блокирует event loop
    elapsed = time.time() - start
    return json({'result': result, 'type': 'blocking', 'time': round(elapsed, 2)})

@app.get('/cpu_fixed')
async def cpu_nonblocking(request):
    start = time.time()
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(None, heavy_cpu_sum)
    elapsed = time.time() - start
    return json({'result': result, 'type': 'nonblocking_thread', 'time': round(elapsed, 2)})

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=False, single_process=True)