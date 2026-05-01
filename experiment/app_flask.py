# app_flask.py
import time
from concurrent.futures import ProcessPoolExecutor
from flask import Flask, jsonify

app = Flask(__name__)

CPU_N = 15_000_000  # 15 млн для баланса скорость/нагрузка

def heavy_cpu_sum():
    return sum(range(1, CPU_N + 1))

@app.route('/cpu')
def cpu_blocking():
    start = time.time()
    result = heavy_cpu_sum()
    elapsed = time.time() - start
    return jsonify({'result': result, 'type': 'blocking', 'time': round(elapsed, 2)})

@app.route('/cpu_fixed')
def cpu_nonblocking():
    start = time.time()
    with ProcessPoolExecutor(max_workers=1) as executor:
        future = executor.submit(heavy_cpu_sum)
        result = future.result()
    elapsed = time.time() - start
    return jsonify({'result': result, 'type': 'nonblocking_process', 'time': round(elapsed, 2)})

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False, threaded=False)