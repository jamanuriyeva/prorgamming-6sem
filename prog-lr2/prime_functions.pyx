# prime_functions.pyx
import math
cimport cython
from libc.math cimport sqrt

@cython.boundscheck(False)
@cython.wraparound(False)
cdef bint is_prime_cython_c(int n) nogil:
    """C-функция проверки простоты числа (без GIL)"""
    cdef int i
    cdef int limit
    
    if n < 2:
        return 0
    if n == 2:
        return 1
    if n % 2 == 0:
        return 0
    
    limit = <int>sqrt(n) + 1
    
    for i in range(3, limit, 2):
        if n % i == 0:
            return 0
    return 1


@cython.boundscheck(False)
@cython.wraparound(False)
def is_prime_cython(int n) -> bool:
    """
    Cython оптимизированная проверка простоты числа.
    """
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    
    cdef int i
    cdef int limit = int(n**0.5) + 1
    
    for i in range(3, limit, 2):
        if n % i == 0:
            return False
    return True


@cython.boundscheck(False)
@cython.wraparound(False)
def count_primes_cython(int start, int end) -> int:
    """
    Cython оптимизированный подсчет простых чисел.
    """
    cdef int num
    cdef int count = 0
    
    for num in range(start, end):
        if is_prime_cython(num):
            count += 1
    return count


@cython.boundscheck(False)
@cython.wraparound(False)
def count_primes_nogil(int start, int end, int n_jobs=4) -> int:
    """
    Оптимизированная версия с Cython (без параллелизма OpenMP).
    Для Windows использует обычную Cython оптимизацию.
    """
    cdef int num
    cdef int count = 0
    
    # Используем C-функцию без GIL для ускорения
    for num in range(start, end):
        if is_prime_cython_c(num):
            count += 1
    
    return count