from locust import HttpUser, task, between, events
import os
import csv
from datetime import datetime

class CpuLoadTest(HttpUser):
    """
    Тестирование CPU-эндпоинтов.
    Каждый пользователь с равной вероятностью вызывает /cpu и /cpu_fixed.
    """
    wait_time = between(0.1, 0.5)

    @task(1)
    def test_cpu_blocking(self):
        """Тест блокирующего эндпоинта"""
        with self.client.get("/cpu", timeout=120, catch_response=True) as response:
            if response.status_code != 200:
                response.failure(f"Status: {response.status_code}")

    @task(1)
    def test_cpu_nonblocking(self):
        """Тест неблокирующего эндпоинта"""
        with self.client.get("/cpu_fixed", timeout=120, catch_response=True) as response:
            if response.status_code != 200:
                response.failure(f"Status: {response.status_code}")


@events.quitting.add_listener
def save_metrics(environment, **kwargs):
    """
    После завершения теста сохраняем метрики:
    - RPS (запросов в секунду)
    - Средняя latency (время ответа)
    - p95 (95-й перцентиль)
    - p99 (99-й перцентиль)
    - Процент ошибок
    """
    if not hasattr(environment.stats, 'entries'):
        return
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_file = f"report/csv/metrics_{timestamp}.csv"
    
    os.makedirs("report/csv", exist_ok=True)
    
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'Method',
            'Endpoint',
            'Total_Requests',
            'Failures',
            'Error_Rate_%',
            'RPS',
            'Avg_Latency_ms',
            'Min_Latency_ms',
            'Max_Latency_ms',
            'Median_Latency_ms',
            'P90_Latency_ms',
            'P95_Latency_ms',
            'P99_Latency_ms'
        ])
        
        for stat in environment.stats.entries.values():
            total = stat.num_requests
            failures = stat.num_failures
            error_rate = round((failures / total * 100), 2) if total > 0 else 0
            
            writer.writerow([
                stat.method,
                stat.name,
                total,
                failures,
                error_rate,
                round(stat.total_rps, 2),
                round(stat.avg_response_time, 2),
                round(stat.min_response_time, 2),
                round(stat.max_response_time, 2),
                round(stat.median_response_time, 2),
                round(stat.get_response_time_percentile(0.90), 2),
                round(stat.get_response_time_percentile(0.95), 2),
                round(stat.get_response_time_percentile(0.99), 2)
            ])
    
    print(f"\n{'='*60}")
    print(f"РЕЗУЛЬТАТЫ ТЕСТА СОХРАНЕНЫ:")
    print(f"  {csv_file}")
    print(f"{'='*60}")
    
    # Выводим сводку в консоль
    print(f"\n{'Endpoint':<15} {'RPS':<10} {'Avg ms':<10} {'P95 ms':<10} {'P99 ms':<10} {'Errors %':<10}")
    print("-" * 65)
    for stat in environment.stats.entries.values():
        total = stat.num_requests
        failures = stat.num_failures
        error_rate = round((failures / total * 100), 2) if total > 0 else 0
        print(f"{stat.name:<15} {stat.total_rps:<10.2f} {stat.avg_response_time:<10.2f} "
                f"{stat.get_response_time_percentile(0.95):<10.2f} "
                f"{stat.get_response_time_percentile(0.99):<10.2f} {error_rate:<10}")
