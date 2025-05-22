import os
import sys
import subprocess
from dotenv import load_dotenv
from crewai import Agent, Task, Crew
from tools import FileTool, TerminalTool, WebSearchTool, PDFReaderTool, GitTool, SQLiteTool, HTMLScraperTool

# Настройка переменных окружения для удаленной модели
os.environ["OPENAI_API_KEY"] = "lm-studio"
os.environ["OPENAI_API_BASE"] = "http://26.224.68.101:1234/v1"

def check_dependencies():
    """Проверяет наличие необходимых зависимостей."""
    required_packages = [
        "crewai", "langchain", "openai", "python-dotenv", "pypdf2",
        "duckduckgo-search", "sqlalchemy", "gitpython",
        "beautifulsoup4", "requests"
    ]
    
    print("Проверка зависимостей...")
    missing_packages = []
    
    try:
        import pkg_resources
        installed_packages = {pkg.key for pkg in pkg_resources.working_set}
        
        for package in required_packages:
            package_name = package.split('==')[0].lower()
            if package_name not in installed_packages:
                missing_packages.append(package)
    except:
        print("Не удалось проверить установленные пакеты.")
        return False
    
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

def run_agent():
    """Создает и запускает агента с удаленной моделью."""
    # Инициализация инструментов
    tools = [
        FileTool(), TerminalTool(), WebSearchTool(),
        PDFReaderTool(), GitTool(), SQLiteTool(), HTMLScraperTool()
    ]
    
    # Создание агента
    agent = Agent(
        role="Full-Stack Autonomous Agent",
        goal="Выполнять различные задачи по запросу пользователя",
        backstory="Ты универсальный автономный агент, способный работать с файлами, кодом, данными, API и многим другим.",
        tools=tools,
        verbose=True
    )
    
    # Меню выбора задачи
    print("\n" + "="*50)
    print("АВТОНОМНЫЙ AI-АГЕНТ".center(50))
    print("="*50)
    print(f"\nИспользуется модель: LM Studio (remote)")
    print(f"URL: http://26.224.68.101:1234/v1")
    print("\nВыберите задачу:")
    print("1. Создать консольную адресную книгу на Python с базой SQLite")
    print("2. Создать Telegram-бота для сохранения и анализа ссылок")
    print("3. Анализ данных из CSV файла и создание отчета")
    print("4. Своя задача (ввести описание)")
    print("0. Выход")
    print("="*50)
    
    choice = input("\nВаш выбор: ")
    
    if choice == "0":
        print("Выход из программы...")
        return
    
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
    
    elif choice == "2":
        task_description = """
        Создай Telegram-бота на Python с использованием библиотеки python-telegram-bot.
        Бот должен:
        1. Сохранять ссылки, которые отправляет пользователь, в базу данных SQLite
        2. Парсить HTML-содержимое этих ссылок и сохранять заголовок и краткое описание
        3. Позволять пользователю просматривать сохраненные ссылки
        4. Иметь команду для поиска по сохраненным ссылкам
        
        Создай все необходимые файлы, включая telegram_bot.py и schema.sql.
        """
    
    elif choice == "3":
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
    
    elif choice == "4":
        print("\nВведите описание своей задачи:")
        task_description = input("> ")
    
    else:
        print("Неверный выбор. Пожалуйста, выберите снова.")
        return
    
    # Создание и запуск задачи
    print(f"\nЗапуск выполнения задачи с удаленной моделью LM Studio...")
    try:
        task = Task(
            description=task_description,
            expected_output="Результат выполнения задачи",
            agent=agent
        )
        
        crew = Crew(
            agents=[agent],
            tasks=[task]
        )
        
        result = crew.kickoff()
        print("\n" + "="*50)
        print("РЕЗУЛЬТАТ ВЫПОЛНЕНИЯ:".center(50))
        print("="*50)
        print(result)
        print("="*50)
        
    except Exception as e:
        print(f"Произошла ошибка при выполнении задачи: {str(e)}")
        print(f"Проверьте, доступен ли сервер LM Studio по адресу: http://26.224.68.101:1234")

if __name__ == "__main__":
    if check_dependencies():
        run_agent()
