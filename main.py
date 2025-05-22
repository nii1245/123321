import os
import sys
import subprocess
import importlib
import pkg_resources
import json

class ModelManager:
    def __init__(self):
        self.models_config = {
            "openai": {
                "name": "OpenAI API",
                "env_vars": {
                    "OPENAI_API_KEY": "your-openai-api-key"
                },
                "models": ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"]
            },
            "lm-studio-local": {
                "name": "LM Studio (localhost)",
                "env_vars": {
                    "OPENAI_API_KEY": "lm-studio",
                    "OPENAI_API_BASE": "http://localhost:1234/v1"
                },
                "models": ["local-model"]
            },
            "lm-studio-remote": {
                "name": "LM Studio (remote)",
                "env_vars": {
                    "OPENAI_API_KEY": "lm-studio",
                    "OPENAI_API_BASE": "http://26.224.68.101:1234/v1"
                },
                "models": ["remote-model"]
            },
            "ollama": {
                "name": "Ollama (локальный)",
                "env_vars": {
                    "OPENAI_API_KEY": "ollama",
                    "OPENAI_API_BASE": "http://localhost:11434/v1"
                },
                "models": ["llama3", "mistral", "mixtral", "gemma"]
            },
            "anthropic": {
                "name": "Anthropic API",
                "env_vars": {
                    "ANTHROPIC_API_KEY": "your-anthropic-api-key"
                },
                "models": ["claude-3-opus", "claude-3-sonnet", "claude-3-haiku"]
            },
            "together": {
                "name": "Together AI",
                "env_vars": {
                    "TOGETHER_API_KEY": "your-together-api-key"
                },
                "models": ["mistralai/Mixtral-8x7B", "meta-llama/Llama-3-70b"]
            }
        }
        
        # Загрузка сохраненной конфигурации, если она существует
        self.config_file = "llm_config.json"
        # Используем удаленную модель LM Studio по умолчанию
        self.current_provider = "lm-studio-remote"
        self.current_model = "remote-model"
        self.load_config()
    
    def load_config(self):
        """Загружает сохраненную конфигурацию LLM."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.current_provider = config.get("provider", "lm-studio")
                    self.current_model = config.get("model", "local-model")
            except Exception as e:
                print(f"Ошибка загрузки конфигурации: {str(e)}")
    
    def save_config(self):
        """Сохраняет текущую конфигурацию LLM."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump({
                    "provider": self.current_provider,
                    "model": self.current_model
                }, f)
        except Exception as e:
            print(f"Ошибка сохранения конфигурации: {str(e)}")
    
    def update_env_file(self):
        """Обновляет .env файл на основе выбранного провайдера."""
        provider_config = self.models_config.get(self.current_provider, {})
        env_vars = provider_config.get("env_vars", {})
        
        # Чтение существующего .env файла
        env_content = {}
        if os.path.exists('.env'):
            with open('.env', 'r', encoding='utf-8') as f:
                for line in f:
                    if '=' in line:
                        key, value = line.strip().split('=', 1)
                        env_content[key] = value
        
        # Обновление переменных для выбранного провайдера
        env_content.update(env_vars)
        
        # Сохранение обновленного .env файла
        with open('.env', 'w', encoding='utf-8') as f:
            for key, value in env_content.items():
                f.write(f"{key}={value}\n")
        
        print(f"Файл .env обновлен для провайдера {provider_config.get('name')}.")
    
    def select_provider(self):
        """Позволяет пользователю выбрать провайдера LLM."""
        print("\nДоступные провайдеры LLM:")
        providers = list(self.models_config.keys())
        
        for i, provider in enumerate(providers):
            config = self.models_config[provider]
            print(f"{i+1}. {config['name']}")
        
        try:
            choice = int(input("\nВыберите провайдера (номер): "))
            if 1 <= choice <= len(providers):
                self.current_provider = providers[choice-1]
                print(f"Выбран провайдер: {self.models_config[self.current_provider]['name']}")
                self.select_model()
                self.update_env_file()
                self.save_config()
                return True
            else:
                print("Неверный выбор.")
                return False
        except ValueError:
            print("Пожалуйста, введите число.")
            return False
    
    def select_model(self):
        """Позволяет пользователю выбрать модель для текущего провайдера."""
        provider_config = self.models_config.get(self.current_provider, {})
        models = provider_config.get("models", [])
        
        if not models:
            print("Для данного провайдера нет доступных моделей.")
            return False
        
        print("\nДоступные модели:")
        for i, model in enumerate(models):
            print(f"{i+1}. {model}")
        
        try:
            choice = int(input("\nВыберите модель (номер): "))
            if 1 <= choice <= len(models):
                self.current_model = models[choice-1]
                print(f"Выбрана модель: {self.current_model}")
                return True
            else:
                print("Неверный выбор.")
                return False
        except ValueError:
            print("Пожалуйста, введите число.")
            return False

class DependencyManager:
    def __init__(self):
        self.required_packages = [
            "crewai", "langchain", "openai", "python-dotenv", "pypdf2",
            "duckduckgo-search", "sqlalchemy", "streamlit", "gitpython",
            "playwright", "beautifulsoup4", "requests", "pandas",
            "matplotlib", "pillow", "anthropic", "together"
        ]
    
    def check_and_install_dependencies(self):
        """Проверяет наличие всех зависимостей и устанавливает отсутствующие."""
        print("Проверка зависимостей...")
        missing_packages = []
        
        installed_packages = {pkg.key for pkg in pkg_resources.working_set}
        
        for package in self.required_packages:
            package_name = package.split('==')[0].lower()
            if package_name not in installed_packages:
                missing_packages.append(package)
        
        if missing_packages:
            print(f"Отсутствуют следующие пакеты: {', '.join(missing_packages)}")
            print("Установка отсутствующих пакетов...")
            
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing_packages)
                print("Все зависимости успешно установлены!")
            except Exception as e:
                print(f"Ошибка при установке пакетов: {str(e)}")
                print("Пожалуйста, установите пакеты вручную: pip install -r requirements.txt")
                return False
        else:
            print("Все зависимости уже установлены!")
        
        return True

    def check_env_file(self):
        """Проверяет наличие .env файла и создает его, если отсутствует."""
        if not os.path.exists('.env'):
            print("Файл .env не найден. Создание файла с настройками по умолчанию...")
            with open('.env', 'w', encoding='utf-8') as f:
                f.write("OPENAI_API_KEY=lm-studio\n")
                f.write("OPENAI_API_BASE=http://localhost:1234/v1\n")
                f.write("SERPER_API_KEY=your-serper-key\n")
            print("Файл .env создан. Пожалуйста, настройте API ключи при необходимости.")

from crewai_tools import BaseTool
import subprocess
import os
import requests
import sqlite3
from bs4 import BeautifulSoup
from PyPDF2 import PdfReader
from duckduckgo_search import DDGS
import git
import json
import time
from PIL import Image
from io import BytesIO
import pandas as pd
import matplotlib.pyplot as plt
import csv

class FileTool(BaseTool):
    name = "FileTool"
    description = "Создаёт или обновляет файл с переданным содержимым."

    def _run(self, content: str, filename: str = "main.py"):
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Файл {filename} создан или обновлён."

class TerminalTool(BaseTool):
    name = "TerminalTool"
    description = "Позволяет выполнять команды в терминале и получать вывод."

    def _run(self, command: str):
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            return result.stdout or result.stderr
        except Exception as e:
            return f"Ошибка выполнения: {str(e)}"

class WebSearchTool(BaseTool):
    name = "WebSearch"
    description = "Ищет в интернете с помощью DuckDuckGo."

    def _run(self, query: str):
        with DDGS() as ddgs:
            results = [r for r in ddgs.text(query, max_results=3)]
            return "\n".join([r['body'] for r in results])

class PDFReaderTool(BaseTool):
    name = "PDFReader"
    description = "Читает и анализирует PDF-файл."

    def _run(self, path: str):
        reader = PdfReader(path)
        text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
        return text[:3000]

class GitTool(BaseTool):
    name = "GitTool"
    description = "Выполняет git действия в текущем проекте."

    def _run(self, action: str):
        try:
            repo = git.Repo('.')
            if action == "commit":
                repo.git.add(A=True)
                repo.index.commit("auto-commit")
                return "Изменения закоммичены."
            elif action == "push":
                repo.git.push()
                return "Изменения отправлены."
            else:
                return f"Неизвестное действие {action}"
        except Exception as e:
            return str(e)

class SQLiteTool(BaseTool):
    name = "SQLiteTool"
    description = "Выполняет SQL-команды на локальной базе данных."

    def _run(self, query: str, db_name="local.db"):
        conn = sqlite3.connect(db_name)
        cur = conn.cursor()
        try:
            cur.execute(query)
            rows = cur.fetchall()
            conn.commit()
            return str(rows)
        except Exception as e:
            return str(e)
        finally:
            conn.close()

class HTMLScraperTool(BaseTool):
    name = "HTMLScraper"
    description = "Скачивает страницу по URL и парсит содержимое."

    def _run(self, url: str):
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            return soup.get_text()[:3000]
        except Exception as e:
            return str(e)

class JSONTool(BaseTool):
    name = "JSONTool"
    description = "Работает с JSON данными - чтение, запись, преобразование."

    def _run(self, action: str, data=None, filename=None):
        if action == "read" and filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                return f"Ошибка чтения JSON: {str(e)}"
        elif action == "write" and data and filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                return f"JSON успешно записан в {filename}"
            except Exception as e:
                return f"Ошибка записи JSON: {str(e)}"
        else:
            return "Неверные параметры для JSONTool"

class APITool(BaseTool):
    name = "APITool"
    description = "Выполняет HTTP запросы к API."

    def _run(self, url: str, method="GET", headers=None, data=None, params=None):
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, params=params)
            elif method.upper() == "POST":
                response = requests.post(url, headers=headers, json=data, params=params)
            elif method.upper() == "PUT":
                response = requests.put(url, headers=headers, json=data, params=params)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=headers, params=params)
            else:
                return f"Неподдерживаемый метод: {method}"
            
            return {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "content": response.text[:3000]  # Ограничиваем вывод
            }
        except Exception as e:
            return f"Ошибка API запроса: {str(e)}"

class DataAnalysisTool(BaseTool):
    name = "DataAnalysisTool"
    description = "Анализирует данные из CSV/Excel файлов."

    def _run(self, filename: str, action="summary"):
        try:
            if filename.endswith('.csv'):
                df = pd.read_csv(filename)
            elif filename.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(filename)
            else:
                return "Неподдерживаемый формат файла. Используйте CSV или Excel."
            
            if action == "summary":
                return {
                    "shape": df.shape,
                    "columns": list(df.columns),
                    "dtypes": str(df.dtypes),
                    "head": df.head(5).to_dict(),
                    "describe": df.describe().to_dict()
                }
            elif action == "plot" and len(df.columns) >= 2:
                plt.figure(figsize=(10, 6))
                plt.scatter(df[df.columns[0]], df[df.columns[1]])
                plt.title(f"{df.columns[0]} vs {df.columns[1]}")
                plt.xlabel(df.columns[0])
                plt.ylabel(df.columns[1])
                plot_file = "data_plot.png"
                plt.savefig(plot_file)
                plt.close()
                return f"График сохранен в {plot_file}"
            else:
                return "Неизвестное действие или недостаточно столбцов для построения графика"
        except Exception as e:
            return f"Ошибка анализа данных: {str(e)}"

class ImageTool(BaseTool):
    name = "ImageTool"
    description = "Работает с изображениями - скачивание, базовая обработка."

    def _run(self, action: str, url=None, path=None, width=None, height=None):
        try:
            if action == "download" and url:
                response = requests.get(url)
                img = Image.open(BytesIO(response.content))
                save_path = path or f"image_{int(time.time())}.jpg"
                img.save(save_path)
                return f"Изображение сохранено в {save_path}"
            
            elif action == "resize" and path:
                img = Image.open(path)
                if width and height:
                    resized = img.resize((width, height))
                    save_path = f"resized_{os.path.basename(path)}"
                    resized.save(save_path)
                    return f"Изображение изменено и сохранено в {save_path}"
                else:
                    return "Для изменения размера укажите width и height"
            else:
                return "Неверные параметры для ImageTool"
        except Exception as e:
            return f"Ошибка обработки изображения: {str(e)}"

class CSVTool(BaseTool):
    name = "CSVTool"
    description = "Работает с CSV файлами - чтение, запись, обработка."

    def _run(self, action: str, filename=None, data=None):
        try:
            if action == "read" and filename:
                rows = []
                with open(filename, 'r', newline='', encoding='utf-8') as csvfile:
                    reader = csv.DictReader(csvfile)
                    for row in reader:
                        rows.append(dict(row))
                return rows
            
            elif action == "write" and filename and data:
                if not data or not isinstance(data, list) or not isinstance(data[0], dict):
                    return "Данные должны быть списком словарей"
                
                fieldnames = data[0].keys()
                with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(data)
                return f"CSV успешно записан в {filename}"
            
            else:
                return "Неверные параметры для CSVTool"
        except Exception as e:
            return f"Ошибка работы с CSV: {str(e)}"

from crewai import Agent, Task, Crew
from dotenv import load_dotenv
import os

class AIAgent:
    def __init__(self, model_manager):
        # Загрузка переменных окружения
        load_dotenv()
        
        # Сохраняем ссылку на менеджер моделей
        self.model_manager = model_manager
        
        # Инициализация всех инструментов
        self.tools = [
            FileTool(), TerminalTool(), WebSearchTool(),
            PDFReaderTool(), GitTool(), SQLiteTool(), HTMLScraperTool(),
            JSONTool(), APITool(), DataAnalysisTool(), ImageTool(), CSVTool()
        ]
        
        # Создание агента с учетом выбранной модели
        self.create_agent()
    
    def create_agent(self):
        """Создает агента с учетом выбранного провайдера и модели."""
        provider = self.model_manager.current_provider
        model = self.model_manager.current_model
        
        # Настройки для разных провайдеров
        if provider == "openai":
            self.agent = Agent(
                role="Full-Stack Autonomous Agent",
                goal="Выполнять различные задачи по запросу пользователя",
                backstory="Ты универсальный автономный агент, способный работать с файлами, кодом, данными, API и многим другим.",
                tools=self.tools,
                verbose=True,
                llm=model
            )
        elif provider == "anthropic":
            from langchain.llms import Anthropic
            llm = Anthropic(model=model)
            self.agent = Agent(
                role="Full-Stack Autonomous Agent",
                goal="Выполнять различные задачи по запросу пользователя",
                backstory="Ты универсальный автономный агент, способный работать с файлами, кодом, данными, API и многим другим.",
                tools=self.tools,
                verbose=True,
                llm=llm
            )
        elif provider in ["lm-studio-local", "lm-studio-remote", "ollama"]:
            from langchain.llms import OpenAI
            # Для локальных и удаленных моделей используем OpenAI-совместимый интерфейс
            base_url = os.getenv("OPENAI_API_BASE")
            api_key = os.getenv("OPENAI_API_KEY")
            
            model_name = "local-model"
            if provider == "ollama":
                model_name = model
            elif provider == "lm-studio-remote":
                model_name = "remote-model"
                
            llm = OpenAI(
                base_url=base_url,
                api_key=api_key,
                model_name=model_name
            )
            
            self.agent = Agent(
                role="Full-Stack Autonomous Agent",
                goal="Выполнять различные задачи по запросу пользователя",
                backstory="Ты универсальный автономный агент, способный работать с файлами, кодом, данными, API и многим другим.",
                tools=self.tools,
                verbose=True,
                llm=llm
            )
        elif provider == "together":
            from langchain.llms import Together
            llm = Together(model=model)
            self.agent = Agent(
                role="Full-Stack Autonomous Agent",
                goal="Выполнять различные задачи по запросу пользователя",
                backstory="Ты универсальный автономный агент, способный работать с файлами, кодом, данными, API и многим другим.",
                tools=self.tools,
                verbose=True,
                llm=llm
            )
        else:
            # По умолчанию используем OpenAI-совместимый интерфейс
            self.agent = Agent(
                role="Full-Stack Autonomous Agent",
                goal="Выполнять различные задачи по запросу пользователя",
                backstory="Ты универсальный автономный агент, способный работать с файлами, кодом, данными, API и многим другим.",
                tools=self.tools,
                verbose=True
            )
    
    def create_task(self, description, expected_output="Результат выполнения задачи"):
        """Создает задачу для агента."""
        return Task(
            description=description,
            expected_output=expected_output,
            agent=self.agent
        )
    
    def run_task(self, task_description):
        """Запускает выполнение задачи."""
        task = self.create_task(task_description)
        crew = Crew(
            agents=[self.agent],
            tasks=[task]
        )
        
        result = crew.kickoff()
        return result

def display_menu():
    """Отображает главное меню с доступными опциями."""
    print("\n" + "="*50)
    print("АВТОНОМНЫЙ AI-АГЕНТ".center(50))
    print("="*50)
    print("\nГлавное меню:")
    print("1. Выбрать LLM модель")
    print("2. Запустить задачу")
    print("0. Выход")
    print("="*50)

def display_tasks_menu():
    """Отображает меню с доступными примерами задач."""
    print("\n" + "="*50)
    print("ВЫБОР ЗАДАЧИ".center(50))
    print("="*50)
    print("\nВыберите пример задачи или введите свою:")
    print("1. Создать консольную адресную книгу на Python с базой SQLite")
    print("2. Создать Telegram-бота для сохранения и анализа ссылок")
    print("3. Анализ данных из CSV файла и создание отчета")
    print("4. Своя задача (ввести описание)")
    print("0. Вернуться в главное меню")
    print("="*50)

def main():
    # Проверка и установка зависимостей
    dependency_manager = DependencyManager()
    if not dependency_manager.check_and_install_dependencies():
        print("Не удалось установить все необходимые зависимости. Выход...")
        return
    
    # Создание менеджера моделей и установка удаленной модели по умолчанию
    model_manager = ModelManager()
    model_manager.current_provider = "lm-studio-remote"
    model_manager.current_model = "remote-model"
    model_manager.save_config()
    
    # Обновление .env файла для использования удаленной модели
    model_manager.update_env_file()
    
    # Создание агента с удаленной моделью
    agent = AIAgent(model_manager)
    
    # Сразу переходим к выбору задачи
    print(f"\nИспользуется модель: {model_manager.models_config[model_manager.current_provider]['name']} ({model_manager.current_model})")
    print(f"URL: {model_manager.models_config[model_manager.current_provider]['env_vars']['OPENAI_API_BASE']}")
    
    # Переходим сразу к выбору задачи
    while True:
        display_tasks_menu()
        choice = input("\nВаш выбор: ")
        
        if choice == "0":
            print("Выход из программы...")
            break
        
        elif choice == "1":
            task_description = """
            Создай консольную адресную книгу на Python с базой SQLite и CLI интерфейсом.
            Программа должна уметь:
            1. Добавлять контакты (имя, телефон, email)
            2. Удалять контакты
            3. Искать контакты по имени
            4. Отображать все контакты
            5. Сохранять данные в SQLite базу
            
            Создай файл address_book.py с полным кодом программы.
            """
                
                elif task_choice == "1":
                    task_description = """
                    Создай консольную адресную книгу на Python с базой SQLite и CLI интерфейсом.
                    Программа должна уметь:
                    1. Добавлять контакты (имя, телефон, email)
                    2. Удалять контакты
                    3. Искать контакты по имени
                    4. Отображать все контакты
                    5. Сохранять данные в SQLite базу
                    
                    Создай файл address_book.py с полным кодом программы.
                    """
                
                elif task_choice == "2":
                    task_description = """
                    Создай Telegram-бота на Python с использованием библиотеки python-telegram-bot.
                    Бот должен:
                    1. Сохранять ссылки, которые отправляет пользователь, в базу данных SQLite
                    2. Парсить HTML-содержимое этих ссылок и сохранять заголовок и краткое описание
                    3. Позволять пользователю просматривать сохраненные ссылки
                    4. Иметь команду для поиска по сохраненным ссылкам
                    
                    Создай все необходимые файлы, включая telegram_bot.py и schema.sql.
                    """
                
                elif task_choice == "3":
                    task_description = """
                    Выполни следующие задачи:
                    
                    1. Создай CSV файл с данными о 5 городах (название, население, страна)
                    2. Проанализируй этот CSV файл и создай отчет
                    3. Сохрани результаты анализа в JSON файл
                    4. Создай SQL базу данных и импортируй туда данные из CSV
                    5. Выполни SQL запрос для получения городов с населением > 1 млн
                    6. Скачай изображение города с наибольшим населением
                    
                    Все результаты сохрани в папку 'results'.
                    """
                
                elif task_choice == "4":
                    print("\nВведите описание своей задачи:")
                    task_description = input("> ")
                
                else:
                    print("Неверный выбор. Пожалуйста, выберите снова.")
                    continue
                
                # Запуск задачи с выбранной моделью
                print(f"\nЗапуск выполнения задачи с моделью: {model_manager.models_config[model_manager.current_provider]['name']} ({model_manager.current_model})...")
                try:
                    result = agent.run_task(task_description)
                    print("\n" + "="*50)
                    print("РЕЗУЛЬТАТ ВЫПОЛНЕНИЯ:".center(50))
                    print("="*50)
                    print(result)
                    print("="*50)
                    
                    input("\nНажмите Enter для продолжения...")
                    break
                
                except Exception as e:
                    print(f"Произошла ошибка при выполнении задачи: {str(e)}")
                    if model_manager.current_provider in ["lm-studio", "ollama"]:
                        print(f"Проверьте, запущен ли локальный сервер {model_manager.current_provider} на правильном порту.")
                    else:
                        print("Проверьте правильность API ключей в файле .env")
                    input("\nНажмите Enter для продолжения...")
                    break
        
        else:
            print("Неверный выбор. Пожалуйста, выберите снова.")
            continue

if __name__ == "__main__":
    main()
