import os
import sys
import subprocess
import importlib.util

# Настройка переменных окружения для удаленной модели
os.environ["OPENAI_API_KEY"] = "lm-studio"
os.environ["OPENAI_API_BASE"] = "http://26.224.68.101:1234/v1"

def check_package(package_name):
    """Проверяет, установлен ли пакет."""
    return importlib.util.find_spec(package_name) is not None

def install_package(package_name):
    """Устанавливает пакет."""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        return True
    except:
        return False

def check_and_install_dependencies():
    """Проверяет и устанавливает основные зависимости."""
    required_packages = ["openai", "python-dotenv"]
    
    for package in required_packages:
        if not check_package(package):
            print(f"Установка пакета {package}...")
            if not install_package(package):
                print(f"Не удалось установить {package}")
                return False
    
    return True

def run_simple_agent():
    """Запускает простого агента с использованием только OpenAI API."""
    try:
        import openai
        
        # Настройка клиента OpenAI для работы с удаленной моделью
        client = openai.OpenAI(
            api_key=os.environ["OPENAI_API_KEY"],
            base_url=os.environ["OPENAI_API_BASE"]
        )
        
        print("\n" + "="*50)
        print("ПРОСТОЙ AI-АГЕНТ".center(50))
        print("="*50)
        print(f"\nИспользуется модель: LM Studio (remote)")
        print(f"URL: {os.environ['OPENAI_API_BASE']}")
        print("\nВыберите задачу:")
        print("1. Создать консольную адресную книгу на Python")
        print("2. Создать Telegram-бота для сохранения ссылок")
        print("3. Анализ данных из CSV файла")
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
            
            Все результаты сохрани в папку 'results'.
            """
        
        elif choice == "4":
            print("\nВведите описание своей задачи:")
            task_description = input("> ")
        
        else:
            print("Неверный выбор. Пожалуйста, выберите снова.")
            return
        
        # Отправка запроса к модели
        print(f"\nЗапуск выполнения задачи с удаленной моделью LM Studio...")
        
        response = client.chat.completions.create(
            model="saiga_mistral_7b_gguf",  # Используем модель saiga_mistral_7b_gguf
            messages=[
                {"role": "system", "content": "Ты универсальный автономный агент, способный работать с файлами, кодом, данными, API и многим другим. Твоя задача - выполнить запрос пользователя и предоставить подробное решение."},
                {"role": "user", "content": task_description}
            ],
            temperature=0.7,
            max_tokens=4000
        )
        
        result = response.choices[0].message.content
        
        print("\n" + "="*50)
        print("РЕЗУЛЬТАТ ВЫПОЛНЕНИЯ:".center(50))
        print("="*50)
        print(result)
        print("="*50)
        
        # Спросим, хочет ли пользователь сохранить результат в файл
        save_choice = input("\nСохранить результат в файл? (y/n): ")
        if save_choice.lower() == 'y':
            filename = input("Введите имя файла (например, result.txt): ")
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(result)
            print(f"Результат сохранен в файл {filename}")
        
    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")
        print(f"Проверьте, доступен ли сервер LM Studio по адресу: {os.environ['OPENAI_API_BASE']}")

if __name__ == "__main__":
    if check_and_install_dependencies():
        run_simple_agent()
    else:
        print("Не удалось установить необходимые зависимости. Выход...")
