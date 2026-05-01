# plot_results.py
import pandas as pd
import matplotlib.pyplot as plt
import glob
import os

def parse_results():
    """Парсим CSV-файлы из папки results/"""
    data = []
    
    for csv_file in glob.glob("report/results/*_stats.csv"):
        # Извлекаем имя фреймворка и количество пользователей из имени файла
        basename = os.path.basename(csv_file)
        parts = basename.replace('.csv', '').split('_')
        
        # Пример: flask_users50_stats.csv
        framework = parts[0]
        users = int(parts[1].replace('users', ''))
        
        df = pd.read_csv(csv_file)
        
        # Добавляем метаданные
        df['Framework'] = framework
        df['Users'] = users
        
        data.append(df)
    
    return pd.concat(data, ignore_index=True)

def plot_comparison():
    """Строим сравнительные графики"""
    df = parse_results()
    
    if df.empty:
        print("Нет данных для построения графиков!")
        return
    
    # Фильтруем только ключевые метрики
    metrics = ['Average', 'P95', 'P99', 'RPS']
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.flatten()
    
    for i, metric in enumerate(metrics):
        ax = axes[i]
        
        for framework in df['Framework'].unique():
            fw_data = df[df['Framework'] == framework]
            
            if metric == 'RPS':
                ax.plot(fw_data['Users'], fw_data[metric], 
                       marker='o', label=framework, linewidth=2)
            else:
                ax.plot(fw_data['Users'], fw_data[metric], 
                       marker='s', label=framework, linewidth=2)
        
        ax.set_title(f'{metric} vs Number of Users', fontsize=14)
        ax.set_xlabel('Concurrent Users', fontsize=12)
        ax.set_ylabel(metric, fontsize=12)
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    plt.suptitle('Framework Performance Comparison', fontsize=16, y=1.02)
    plt.tight_layout()
    plt.savefig('report/results/performance_comparison.png', dpi=150, bbox_inches='tight')
    plt.show()
    
    # Сохраняем сводную таблицу
    summary = df.groupby(['Framework', 'Users']).agg({
        'RPS': 'mean',
        'Average': 'mean',
        'P95': 'mean',
        'P99': 'mean',
        'Failures': 'sum'
    }).round(2)
    
    summary.to_csv('report/results/summary.csv')
    print("Сводная таблица сохранена в report/results/summary.csv")
    print(summary)

if __name__ == '__main__':
    plot_comparison()