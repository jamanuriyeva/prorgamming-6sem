"""
Асинхронное веб-приложение для поиска публикаций в Crossref API.
Использует Flask для интерфейса, httpx для асинхронных HTTP-запросов.
"""

import asyncio
import httpx
from flask import Flask, render_template, request, jsonify
import traceback

app = Flask(__name__)

# Базовый URL API Crossref
CROSSREF_API_URL = "https://api.crossref.org/works"

# Максимальное количество результатов
MAX_RESULTS = 15

# Таймаут для запросов (секунды)
REQUEST_TIMEOUT = 10.0


class CrossrefSearchError(Exception):
    """Пользовательское исключение для ошибок поиска Crossref."""
    pass


async def fetch_publications(client, params):
    """
    Асинхронный запрос к API Crossref с использованием httpx.
    
    Аргументы:
        client: httpx.AsyncClient
        params: dict - параметры запроса (query.author, query.title и т.д.)
    
    Возвращает:
        list - список публикаций или выбрасывает исключение.
    """
    params.update({
        "rows": MAX_RESULTS,      # Количество записей
        "sort": "relevance",      # Сортировка по релевантности
        "order": "desc"
    })
    
    try:
        # Асинхронный GET-запрос с таймаутом
        response = await client.get(
            CROSSREF_API_URL, 
            params=params,
            timeout=REQUEST_TIMEOUT
        )
        
        # Проверка HTTP статуса
        if response.status_code != 200:
            raise CrossrefSearchError(
                f"API вернул статус {response.status_code}: {response.text[:200]}"
            )
        
        # Парсинг JSON
        data = response.json()
        
        # Извлечение сообщения из ответа API
        items = data.get("message", {}).get("items", [])
        
        if not items:
            raise CrossrefSearchError("По вашему запросу ничего не найдено.")
        
        return items
        
    except httpx.TimeoutException:
        raise CrossrefSearchError(
            f"Превышен таймаут запроса ({REQUEST_TIMEOUT} сек.). "
            "Попробуйте позже."
        )
    except httpx.RequestError as e:
        raise CrossrefSearchError(f"Ошибка сети: {str(e)}")
    except Exception as e:
        raise CrossrefSearchError(f"Неожиданная ошибка: {str(e)}")


def extract_publication_info(item):
    """
    Извлекает необходимые поля из одной публикации.
    
    Аргументы:
        item: dict - объект публикации из API Crossref
    
    Возвращает:
        dict - структурированная информация для отображения.
    """
    # Название статьи
    title = item.get("title", ["Без названия"])[0] if item.get("title") else "Без названия"
    
    # Информация об авторах
    authors = item.get("author", [])
    first_author = authors[0] if authors else None
    
    # Имя первого автора (фамилия + имя)
    first_author_name = "Не указан"
    if first_author:
        family = first_author.get("family", "")
        given = first_author.get("given", "")
        if family or given:
            first_author_name = f"{family} {given}".strip()
    
    # Название журнала/сборника
    container_title = item.get("container-title", ["Не указано"])[0] if item.get("container-title") else "Не указано"
    
    # Год публикации
    issued = item.get("issued", {})
    date_parts = issued.get("date-parts", [[]])
    year = date_parts[0][0] if date_parts and date_parts[0] else "Год не указан"
    
    # Аффилиация первого автора
    affiliation = "Не указано"
    if first_author and "affiliation" in first_author:
        affiliations = first_author.get("affiliation", [])
        if affiliations and isinstance(affiliations, list):
            affiliation = affiliations[0].get("name", "Не указано")
    
    return {
        "title": title,
        "first_author": first_author_name,
        "container_title": container_title,
        "year": str(year),
        "affiliation": affiliation
    }


async def search_publications_async(search_type, query_text):
    """
    Асинхронный обработчик поиска.
    Поддерживает поиск по автору или названию.
    
    Аргументы:
        search_type: str - "author" или "title"
        query_text: str - поисковый запрос
    
    Возвращает:
        list - список обработанных публикаций
    """
    # Формирование параметров запроса согласно документации Crossref
    if search_type == "author":
        # query.author - для поиска по автору
        params = {"query.author": query_text}
    elif search_type == "title":
        # query.title - для поиска по названию
        params = {"query.title": query_text}
    else:
        raise ValueError(f"Неизвестный тип поиска: {search_type}")
    
    # Асинхронный HTTP-сеанс с httpx
    async with httpx.AsyncClient() as client:
        items = await fetch_publications(client, params)
        
        # Обработка каждой публикации
        results = [extract_publication_info(item) for item in items]
        return results


@app.route("/", methods=["GET", "POST"])
def index():
    """
    Основной обработчик Flask: отображает форму и результаты поиска.
    Запускает асинхронный поиск через asyncio.run().
    """
    results = []
    error = None
    search_performed = False
    search_type = None
    
    if request.method == "POST":
        search_performed = True
        search_type = request.form.get("search_type")
        query = request.form.get("query", "").strip()
        
        # Валидация ввода
        if not query:
            error = "Пожалуйста, введите поисковый запрос."
        elif search_type not in ["author", "title"]:
            error = "Выберите тип поиска (автор или название)."
        else:
            try:
                # Запуск асинхронной функции внутри синхронного Flask
                results = asyncio.run(search_publications_async(search_type, query))
                
                if not results:
                    error = "Ничего не найдено. Попробуйте изменить запрос."
                    
            except CrossrefSearchError as e:
                error = str(e)
            except Exception as e:
                app.logger.error(f"Ошибка: {traceback.format_exc()}")
                error = f"Внутренняя ошибка приложения: {str(e)}"
    
    return render_template(
        "index.html",
        results=results,
        error=error,
        search_performed=search_performed,
        search_type=search_type,
        query=request.form.get("query", "") if request.method == "POST" else ""
    )


@app.route("/batch_search", methods=["POST"])
def batch_search():
    """
    Расширенный обработчик для поиска по нескольким авторам (список через запятую).
    Показывает пример асинхронного выполнения нескольких запросов параллельно.
    """
    authors_input = request.form.get("authors", "")
    authors_list = [a.strip() for a in authors_input.split(",") if a.strip()]
    
    if not authors_list:
        return jsonify({"error": "Введите хотя бы одного автора"}), 400
    
    async def fetch_all_authors():
        """Асинхронно выполняет поиск по каждому автору параллельно."""
        async with httpx.AsyncClient() as client:
            tasks = []
            for author in authors_list:
                params = {"query.author": author, "rows": 5}
                tasks.append(fetch_publications(client, params))
            
            # Параллельное выполнение всех запросов
            all_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Обработка результатов
            response_data = {}
            for author, result in zip(authors_list, all_results):
                if isinstance(result, Exception):
                    response_data[author] = {"error": str(result)}
                else:
                    publications = [extract_publication_info(item) for item in result]
                    response_data[author] = {"count": len(publications), "items": publications}
            
            return response_data
    
    try:
        data = asyncio.run(fetch_all_authors())
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)