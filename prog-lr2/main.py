# main.py
import math
import time
import threading
import multiprocessing
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from typing import List, Tuple, Callable, Dict


# ИТЕРАЦИЯ 1: БАЗОВАЯ ФУНКЦИЯ (Pure Python)

def is_prime(n: int) -> bool:
    """
    Проверяет, является ли число простым.
    
    Parameters
    ----------
    n : int
        Проверяемое число
    
    Returns
    -------
    bool
        True если число простое, иначе False
    
    Examples
    --------
    >>> is_prime(17)
    True
    >>> is_prime(1)
    False
    """
    if n < 2:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True


def count_primes_sequential(start: int, end: int) -> int:
    """
    Последовательный подсчет простых чисел в диапазоне [start, end).
    
    Parameters
    ----------
    start : int
        Начало диапазона (включительно)
    end : int
        Конец диапазона (исключительно)
    
    Returns
    -------
    int
        Количество простых чисел в диапазоне
    
    Examples
    --------
    >>> count_primes_sequential(0, 10)
    4
    >>> count_primes_sequential(100, 100)
    0
    """
    count = 0
    for num in range(start, end):
        if is_prime(num):
            count += 1
    return count


# ИТЕРАЦИЯ 2: МНОГОПОТОЧНОСТЬ (Threading)

def count_primes_threads(start: int, end: int, n_jobs: int = 4) -> int:
    """
    Параллельный подсчет простых чисел с использованием потоков.
    ВНИМАНИЕ: Из-за GIL не дает ускорения для CPU-bound задач.
    
    Parameters
    ----------
    start : int
        Начало диапазона
    end : int
        Конец диапазона
    n_jobs : int, optional
        Количество потоков (по умолчанию 4)
    
    Returns
    -------
    int
        Количество простых чисел
    
    Examples
    --------
    >>> count_primes_threads(0, 10, n_jobs=2)
    4
    >>> count_primes_threads(0, 100, n_jobs=4)
    25
    """
    def worker(chunk_start: int, chunk_end: int, result: List[int], idx: int):
        result[idx] = count_primes_sequential(chunk_start, chunk_end)
    
    step = (end - start) // n_jobs
    threads = []
    results = [0] * n_jobs
    
    for i in range(n_jobs):
        chunk_start = start + i * step
        chunk_end = chunk_start + step if i < n_jobs - 1 else end
        thread = threading.Thread(target=worker, args=(chunk_start, chunk_end, results, i))
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()
    
    return sum(results)


# ИТЕРАЦИЯ 3: МНОГОПРОЦЕССНОСТЬ (Multiprocessing)

def count_primes_processes(start: int, end: int, n_jobs: int = 4) -> int:
    """
    Параллельный подсчет простых чисел с использованием процессов.
    Реальное ускорение за счет обхода GIL.
    
    Parameters
    ----------
    start : int
        Начало диапазона
    end : int
        Конец диапазона
    n_jobs : int, optional
        Количество процессов (по умолчанию 4)
    
    Returns
    -------
    int
        Количество простых чисел
    
    Examples
    --------
    >>> count_primes_processes(0, 10, n_jobs=2)
    4
    >>> count_primes_processes(0, 100, n_jobs=4)
    25
    """
    with ProcessPoolExecutor(max_workers=n_jobs) as executor:
        step = (end - start) // n_jobs
        futures = []
        
        for i in range(n_jobs):
            chunk_start = start + i * step
            chunk_end = chunk_start + step if i < n_jobs - 1 else end
            futures.append(executor.submit(count_primes_sequential, chunk_start, chunk_end))
        
        return sum(future.result() for future in futures)


# ИТЕРАЦИЯ 4: Cython ОПТИМИЗАЦИЯ

try:
    import prime_functions
    count_primes_cython = prime_functions.count_primes_cython
    count_primes_nogil = prime_functions.count_primes_nogil
    CYTHON_AVAILABLE = True
    NOGIL_AVAILABLE = True
except ImportError:
    CYTHON_AVAILABLE = False
    NOGIL_AVAILABLE = False
    
    def count_primes_cython(start: int, end: int) -> int:
        """Cython версия (недоступна, используется Python fallback)"""
        return count_primes_sequential(start, end)
    
    def count_primes_nogil(start: int, end: int, n_jobs: int = 4) -> int:
        """NOGIL версия (недоступна, используется Python fallback)"""
        return count_primes_processes(start, end, n_jobs=n_jobs)


# ОСНОВНАЯ ФУНКЦИЯ

def main():
    """Главная функция программы"""
    START = 0
    END = 2_000_000
    N_JOBS = multiprocessing.cpu_count()
    
    # Замер времени для каждого метода
    methods = [
        ("1. Последовательный", count_primes_sequential),
        ("2. Многопоточность", lambda s, e: count_primes_threads(s, e, n_jobs=N_JOBS)),
        ("3. Многопроцессность", lambda s, e: count_primes_processes(s, e, n_jobs=N_JOBS)),
        ("4. Cython", count_primes_cython),
        ("5. NOGIL", lambda s, e: count_primes_nogil(s, e, n_jobs=N_JOBS)),
    ]
    
    results = {}
    base_time = None
    
    for name, func in methods:
        print(f"\n{name}")
        print("-"*40)
        start_time = time.perf_counter()
        result = func(START, END)
        elapsed = time.perf_counter() - start_time
        
        if base_time is None:
            base_time = elapsed
            speedup = 1.0
        else:
            speedup = base_time / elapsed
        
        results[name] = {"time": elapsed, "result": result, "speedup": speedup}
        print(f"  Время: {elapsed:.4f} сек")
        print(f"  Результат: {result} простых чисел")
        print(f"  Ускорение: {speedup:.2f}x")
    
    
    
    # Вывод лучшего метода
    best = max(results.items(), key=lambda x: x[1]['speedup'])
    print(f"\n ЛУЧШИЙ МЕТОД: {best[0]} (ускорение {best[1]['speedup']:.2f}x)")


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()