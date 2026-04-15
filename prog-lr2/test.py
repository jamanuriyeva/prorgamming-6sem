# test_prime_simple.py - максимально простой вариант
import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import is_prime, count_primes_sequential


class TestPrime(unittest.TestCase):
    """Тесты для функций поиска простых чисел"""
    
    def test_is_prime(self):
        """Ситуация 1: Проверка простых и составных чисел"""
        # Простые числа
        primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
        for p in primes:
            self.assertTrue(is_prime(p), f"{p} должно быть простым")
        
        # Составные числа
        non_primes = [0, 1, 4, 6, 8, 9, 10, 12, 14, 15, 16, 18, 20]
        for np in non_primes:
            self.assertFalse(is_prime(np), f"{np} не должно быть простым")
    
    def test_count_primes(self):
        """Ситуация 2: Проверка подсчета в разных диапазонах"""
        # Известные значения
        self.assertEqual(count_primes_sequential(0, 10), 4)    # 2,3,5,7
        self.assertEqual(count_primes_sequential(0, 100), 25)  # 25 простых
        self.assertEqual(count_primes_sequential(0, 1000), 168) # 168 простых
        
        # Граничные случаи
        self.assertEqual(count_primes_sequential(10, 10), 0)    # пустой диапазон
        self.assertEqual(count_primes_sequential(2, 3), 1)      # только 2


if __name__ == "__main__":
    print("\n" + "="*50)
    print("🧪 ЗАПУСК UNITTEST")
    print("="*50)
    unittest.main(verbosity=2)