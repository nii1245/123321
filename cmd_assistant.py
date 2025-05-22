import os
import sys
import re
import time
import json
import datetime
import colorama
from colorama import Fore, Back, Style
import shutil
from pathlib import Path
import threading
import queue
import torch
import numpy as np
import sounddevice as sd
import torch.hub
import requests
from collections import deque

# Очередь для синхронизации доступа к движку TTS
tts_queue = queue.Queue()

# Простой флаг для голосового управления
voice_enabled = True

class VoiceManager:
    def __init__(self):
        self.enabled = False
        self.current_voice = "xenia"
        self.sample_rate = 48000
        self.model = None
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.voices = {
            "xenia": "xenia",
            "aidar": "aidar",
            "baya": "baya",
            "kseniya": "kseniya",
            "eugene": "eugene",
            "random": "random"
        }
        self.load_model()
    
    def load_model(self):
        """Загружает модель для синтеза речи."""
        try:
            # Пробуем загрузить модель с разными параметрами
            torch.hub._validate_not_a_forked_repo = lambda a, b, c: True
            
            # Пробуем загрузить модель с разными параметрами
            for speaker in ['v3_1_ru', 'ru_v3', 'v3']:
                try:
                    self.model, _ = torch.hub.load(
                        repo_or_dir='snakers4/silero-models',
                        model='silero_tts',
                        language='ru',
                        speaker=speaker
                    )
                    self.model.to(self.device)
                    self.enabled = True
                    print(f"Модель TTS успешно загружена с параметром speaker='{speaker}'")
                    return True
                except Exception as e:
                    print(f"Не удалось загрузить с speaker='{speaker}': {str(e)[:200]}")
            
            # Если не удалось загрузить ни с какими параметрами
            self.enabled = False
            print("Не удалось загрузить модель TTS ни с какими параметрами")
            return False
            
        except Exception as e:
            print(f"Критическая ошибка при загрузке модели TTS: {e}")
            self.enabled = False
            return False
    
    def clean_text(self, text):
        """Очищает текст для TTS."""
        # Заменяем переносы строк на пробелы
        text = text.replace('\n', ' ').replace('\r', '')
        # Удаляем лишние пробелы
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def is_russian_text(self, text):
        """Проверяет, содержит ли текст русские символы."""
        return bool(re.search('[а-яА-ЯёЁ]', text))

    def speak(self, text):
        """Озвучивает текст."""
        if not self.enabled or not text or not self.model:
            print("Озвучка отключена или модель не загружена")
            return
            
        # Пропускаем не-русский текст
        if not self.is_russian_text(text):
            print("Пропуск озвучки: текст не содержит русских символов")
            return
            
        def _speak():
            try:
                # Очищаем текст
                clean_text = self.clean_text(text)
                if not clean_text:
                    print("Текст для озвучки пуст")
                    return
                
                print(f"Озвучиваю: {clean_text[:100]}...")
                
                # Проверяем, что текст содержит русские символы
                if not self.is_russian_text(clean_text):
                    print("Пропуск: текст не содержит русских символов после очистки")
                    return
                
                # Ограничиваем длину текста для TTS
                if len(clean_text) > 500:
                    clean_text = clean_text[:500] + '...'
                
                # Генерируем аудио
                try:
                    audio = self.model.apply_tts(
                        text=clean_text,
                        speaker=self.current_voice,
                        sample_rate=self.sample_rate,
                        put_accent=True,
                        put_yo=True
                    )
                except Exception as e:
                    print(f"Ошибка генерации TTS: {str(e)}")
                    return
                
                # Воспроизводим
                try:
                    if isinstance(audio, torch.Tensor):
                        audio = audio.cpu().numpy()
                except Exception as e:
                    print(f"Ошибка преобразования аудио: {str(e)}")
                    return
                
                if audio is not None:
                    try:
                        print(f"Воспроизведение аудио длительностью {len(audio)/self.sample_rate:.2f} сек")
                        sd.play(audio, self.sample_rate)
                        sd.wait()
                        print("Воспроизведение завершено")
                    except Exception as e:
                        print(f"Ошибка воспроизведения: {str(e)}")
                else:
                    print("Не удалось сгенерировать аудио")
                    
            except Exception as e:
                print(f"Ошибка при обработке речи: {str(e)}")
        
        # Запускаем в отдельном потоке
        threading.Thread(target=_speak, daemon=True).start()
    
    def change_voice(self, voice_name):
        """Меняет голос"""
        if voice_name in self.voices:
            self.current_voice = voice_name
            print(f"Голос изменён на: {voice_name}")
            return True
        print(f"Голос {voice_name} не найден. Доступные голоса: {', '.join(self.voices.keys())}")
        return False
        return f"Голос изменён на {voice_name}"

    def toggle(self, state=None):
        """Включает/выключает голос"""
        if state is not None:
            self.enabled = bool(state)
        else:
            self.enabled = not self.enabled
        status = "включен" if self.enabled else "выключен"
        return f"Голос {status}"

    def stop(self):
        """Останавливает текущее воспроизведение"""
        try:
            sd.stop()
            return "Воспроизведение остановлено"
        except Exception as e:
            print(f"Ошибка при остановке воспроизведения: {str(e)}")
            return "Не удалось остановить воспроизведение"

# Глобальный экземпляр VoiceManager
voice_manager = VoiceManager()

# Настройки подключения по умолчанию
DEFAULT_BASE_URL = "http://26.224.68.101:1234/v1"
DEFAULT_MODEL = "saiga_mistral_7b_gguf"
DEFAULT_API_KEY = "lm-studio"

# Инициализация colorama
colorama.init()

# Глобальные настройки подключения
BASE_URL = DEFAULT_BASE_URL
MODEL_NAME = DEFAULT_MODEL
API_KEY = DEFAULT_API_KEY

# Кэш доступных моделей
AVAILABLE_MODELS = []

# Информация о максимальной длине контекста для разных моделей
MODEL_CONTEXT_LENGTHS = {
    'deepseek-coder-6.7b-instruct': 16384,
    'mistral-nemo-instruct-2407': 8192,
    'mathstral-7b-v0.1': 8192,
    'saiga_mistral_7b_gguf': 8192,
    'llama3': 8192,
    'mixtral': 32768,
    'gpt-4': 8192,
    'gpt-3.5-turbo': 16385,
    'claude-2': 100000,
    'claude-3-opus': 200000,
    'claude-3-sonnet': 200000,
    'default': 8000
}

# Настройки контекста
MAX_TOKENS = 8000  # Значение по умолчанию, будет обновлено при выборе модели
CURRENT_MODEL = None  # Текущая выбранная модель

SYSTEM_PROMPT = """Ты - продвинутый ИИ-ассистент. Твоя задача - давать полезные и информативные ответы, сохраняя баланс между краткостью и полнотой.

ТВОИ ПРИНЦИПЫ:
1. Отвечай по существу, но не сухо
2. Будь дружелюбным, но не навязчивым
3. Давай развернутые ответы на сложные вопросы
4. На простые вопросы отвечай кратко
5. Не используй эмодзи и специальные символы в ответах

Формат ответов:
> привет
Привет! Чем могу помочь?

> создай файл test.txt
Готово! Файл test.txt создан в текущей директории.

> покажи файлы
Содержимое текущей папки:
- file1.txt
- file2.txt

> как дела?
Всё отлично, спасибо! Готов помочь с любыми задачами. А у тебя как дела?

> объясни, как работает Python
Python - это интерпретируемый язык программирования с динамической типизацией. Вот его ключевые особенности:
- Простой и понятный синтаксис
- Большое сообщество и библиотеки
- Кроссплатформенность
- Поддержка ООП и функционального программирования

Хочешь узнать что-то конкретное о Python?"

Пользователь: как дела?
Ты: Всё работает

Пользователь: создай папку test
Ты: ✓ Папка создана

Помни: МИНИМУМ СЛОВ, МАКСИМУМ ДЕЙСТВИЙ!"""

def clear_screen():
    """Очищает экран терминала."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_cmd_header():
    """Выводит заголовок, имитирующий CMD."""
    clear_screen()
    print(f"Microsoft Windows [Version 10.0.19045.3803]")
    print(f"(c) Microsoft Corporation. Все права защищены.")
    print()

def get_current_directory():
    """Возвращает текущую директорию в формате CMD."""
    return os.getcwd()

def print_prompt(directory):
    """Выводит приглашение командной строки."""
    print(f"{directory}>", end=" ")

def execute_system_command(command):
    """Выполняет системную команду и возвращает результат."""
    try:
        import subprocess
        result = subprocess.run(
            command,
            shell=True,
            text=True,
            capture_output=True,
            encoding='cp866'  # Кодировка для русского языка в Windows
        )
        return result.stdout if result.stdout else "Команда выполнена успешно"
    except Exception as e:
        return f"Ошибка выполнения команды: {str(e)}"

def parse_file_creation_command(text):
    """Разбирает команду создания файла с путём и содержимым"""
    import re
    
    # Паттерны для поиска путей и содержимого
    path_patterns = [
        (r'(?:в|во|inside|in)\s+(?:папк[еи]|каталоге|folder)?\s*([^\s\.]+)', 'in_folder'),
        (r'([^\s\\/]+(?:\\/[^\s\\/]+)*\.[a-zA-Z0-9]+)', 'full_path'),
    ]
    
    # Ищем шаблоны содержимого
    content_templates = {
        'крестики-нолики': 'tictactoe',
        'калькулятор': 'calculator',
        'заметки': 'notes',
        'игру': 'game',
    }
    
    # Извлекаем путь
    path = None
    content_type = None
    
    for pattern, ptype in path_patterns:
        match = re.search(pattern, text.lower())
        if match:
            if ptype == 'in_folder':
                folder = match.group(1).strip()
                filename = 'new_file.txt'
                path = f"{folder}/{filename}"
            else:
                path = match.group(1).strip()
            break
    
    # Определяем тип содержимого
    for keyword, template in content_templates.items():
        if keyword in text.lower():
            content_type = template
            break
    
    return path, content_type

def process_command(command, conversation_history):
    """Обрабатывает команды для работы с файловой системой и выполнения системных команд."""
    global BASE_URL, MODEL_NAME, API_KEY, voice_manager
    
    command = command.strip()
    response = ""
    
    # Обработка голосовых команд
    if command.lower().startswith("голос"):
        parts = command.split()
        if len(parts) > 1:
            if parts[1].lower() in ["вкл", "on"]:
                return voice_manager.toggle(True)
            elif parts[1].lower() in ["выкл", "off"]:
                return voice_manager.toggle(False)
            elif parts[1].lower() in voice_manager.voices:
                return voice_manager.change_voice(parts[1].lower())
        return "Использование: голос [вкл/выкл/мужской/женский]"
    
    # Приводим команду к нижнему регистру для остальной обработки
    command = command.lower()  # Анализируем команду на создание приложения
    if any(word in command for word in ['создай приложение', 'сделай приложение', 'создай проект']):
        # Анализируем требования к приложению
        requirements = analyze_requirements(command)
        
        # Генерируем структуру приложения
        app_structure = generate_app_structure(requirements)
        
        # Создаем файлы и папки
        results = []
        for path, content in app_structure.items():
            if path.endswith('/'):  # Это директория
                result = create_file(path, None)
            else:
                result = create_file(path, content)
            results.append(result)
        
        return "\n".join(results)
    
    # Обработка создания файлов и папок
    if any(word in command.lower() for word in ['создай', 'создать', 'напиши', 'сделай']):
        # Пытаемся извлечь путь из команды
        path, _ = parse_file_creation_command(command)
        if path:
            return create_file(path)
    
    # Обработка команд с указанием пути
    if 'внутри папки' in command.lower() or 'в папке' in command.lower():
        # Извлекаем имя папки и оставшуюся часть команды
        parts = re.split(r'внутри папки|в папке', command, flags=re.IGNORECASE)
        if len(parts) > 1:
            folder = parts[1].strip().split()[0]
            rest_command = ' '.join(parts[1].strip().split()[1:])
            
            # Создаем папку, если её нет
            if not os.path.exists(folder):
                os.makedirs(folder, exist_ok=True)
            
            # Обрабатываем команду внутри папки
            if any(cmd in rest_command.lower() for cmd in ['создай файл', 'создать файл']):
                filename = rest_command.split('файл')[-1].strip()
                return create_file(os.path.join(folder, filename))
    
    # Обработка команды меню
    if command.lower() == 'меню':
        return show_interactive_menu()
        
    # Обработка команд для работы с файлами и папками
    if command.lower().startswith("создай файл") or command.lower().startswith("создать файл"):
        try:
            # Извлекаем имя файла из команды
            parts = command.split()
            if len(parts) < 3:
                return "❌ Укажите имя файла"
                
            filename = ' '.join(parts[2:]).strip('"\'')
            
            # Добавляем расширение .txt, если не указано
            if not os.path.splitext(filename)[1]:
                filename += ".txt"
                
            # Создаем все необходимые директории
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            # Создаем пустой файл
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    pass
                return f"✓ Файл {os.path.abspath(filename)} создан"
            except Exception as e:
                return f"❌ Ошибка при создании файла: {str(e)}"
        except Exception as e:
            return f"❌ Ошибка: {str(e)}"
    
    elif command.lower().startswith("создай папку") or command.lower().startswith("создать папку"):
        try:
            # Извлекаем имя папки из команды
            parts = command.split()
            if len(parts) < 3:
                return "❌ Укажите имя папки"
                
            dirname = ' '.join(parts[2:]).strip('"\'')
            return create_folder(dirname)
            
        except Exception as e:
            return f"❌ Ошибка: {str(e)}"
    
    elif command.lower().startswith("покажи файлы") or command.lower().startswith("показать файлы"):
        try:
            # Показываем полный путь текущей директории
            result = f"Текущая папка: {os.getcwd()}\n"
            result += "Содержимое папки:\n"
            
            # Получаем список файлов и папок
            items = os.listdir()
            for item in items:
                full_path = os.path.join(os.getcwd(), item)
                if os.path.isdir(full_path):
                    result += f"[Папка] {item}"
                else:
                    result += f"[Файл]  {item}"
                
                # Добавляем размер файла
                if os.path.isfile(full_path):
                    size = os.path.getsize(full_path)
                    if size < 1024:
                        size_str = f"{size} байт"
                    elif size < 1024*1024:
                        size_str = f"{size/1024:.1f} КБ"
                    else:
                        size_str = f"{size/(1024*1024):.1f} МБ"
                    result += f" ({size_str})"
                result += "\n"
                
            return result.strip()
        except Exception as e:
            return f"❌ Ошибка при получении списка файлов: {str(e)}"
    
    elif command.lower() == 'cls' or command.lower() == 'очистить':
        os.system('cls')
        return ""
        
    elif command.lower() == 'помощь':
        show_full_help()
        return ""
        
    elif command.lower() == 'смена модели':
        global MODEL_NAME
        MODEL_NAME = select_model()
        return f"✓ Выбрана модель: {MODEL_NAME}"
    
    elif command.lower() == 'лимит токенов' or command.lower() == 'токены':
        return change_token_limit()
        
    # Если команда не распознана, отправляем запрос к AI
    return None

def count_tokens(text):
    """Приблизительный подсчет токенов (1 токен ~ 4 символа)"""
    return len(str(text)) // 4

def prepare_messages(history, user_message):
    """Подготавливает сообщения с учетом ограничения на длину"""
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    total_tokens = count_tokens(SYSTEM_PROMPT) + count_tokens(user_message)
    
    # Добавляем историю, пока не достигнем лимита
    for msg in reversed(history):
        msg_tokens = count_tokens(msg["content"])
        if total_tokens + msg_tokens > MAX_TOKENS - 500:  # Оставляем запас для ответа
            break
        messages.insert(1, msg)  # Вставляем в начало (после системного сообщения)
        total_tokens += msg_tokens
    
    messages.append({"role": "user", "content": user_message})
    return messages

def send_to_ai(message, conversation_history):
    """Отправляет сообщение к AI и получает ответ."""
    global BASE_URL, MODEL_NAME, API_KEY, voice_manager
    
    # Функция для озвучивания текста
    def speak_text(text):
        if not text.strip() or not voice_manager.enabled:
            return
            
        try:
            # Простая очистка текста
            clean_text = re.sub(r'[^\w\s.,!?-]', ' ', text)  # Оставляем только буквы, цифры и основные знаки препинания
            clean_text = ' '.join(clean_text.split())  # Удаляем лишние пробелы
            
            # Разбиваем на предложения
            sentences = re.split('(?<=[.!?]) +', clean_text)
            
            # Озвучиваем каждое предложение
            for sentence in sentences:
                if sentence.strip():
                    voice_manager.speak(sentence.strip())
                    
        except Exception as e:
            print(f"Ошибка при озвучивании текста: {e}")
    
    # Сначала проверяем, не является ли сообщение командой
    command_response = process_command(message, conversation_history)
    if command_response is not None:
        if command_response:  # Если есть ответ от команды, выводим его
            print()  # Пустая строка перед ответом
            simulate_typing(command_response, delay=0.005)
            print("\n")
            # Озвучиваем ответ команды
            speak_text(command_response)
        return command_response
        
    try:
        print("\nОбработка запроса...", end="\r")
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}"
        }
        
        # Формируем сообщения с учетом контекста
        messages = prepare_messages(conversation_history, message)
        
        data = {
            "model": MODEL_NAME,
            "messages": messages,
            "temperature": 0.8,  # Немного увеличим для большей креативности
            "top_p": 0.95,      # Ограничим выборку до 95% наиболее вероятных токенов
            "top_k": 50,        # Ограничим выборку до 50 наиболее вероятных токенов
            "repetition_penalty": 1.1,  # Штраф за повторения
            "max_tokens": 4000,  # Увеличим максимальное количество токенов
            "stream": True,      # Включаем потоковую передачу
            "presence_penalty": 0.5,  # Штраф за повторяющиеся темы
            "frequency_penalty": 0.5  # Штраф за частые слова
        }
        
        # Отправляем запрос к API с потоковой передачей
        response = requests.post(
            f"{BASE_URL}/chat/completions", 
            headers=headers,
            json=data,
            stream=True,
            timeout=60
        )
        
        if response.status_code == 200:
            full_response = ""
            buffer = ""
            print("\n")  # Две пустые строки перед ответом
            
            # Обрабатываем потоковые данные
            current_sentence = ""
            full_response = ""
            print("\n")  # Две пустые строки перед ответом
            
            for line in response.iter_lines():
                if not line:
                    continue
                    
                line = line.decode('utf-8')
                if not line.startswith('data: '):
                    continue
                    
                data = line[6:]  # Удаляем префикс 'data: '
                if data.strip() == '[DONE]':
                    if current_sentence.strip():
                        speak_text(current_sentence)
                    break
                    
                try:
                    chunk = json.loads(data)
                    if not chunk.get('choices'):
                        continue
                        
                    delta = chunk['choices'][0].get('delta', {})
                    content = delta.get('content', '')
                    
                    if content:
                        # Добавляем в полный ответ и текущее предложение
                        full_response += content
                        current_sentence += content
                        
                        # Выводим текст по мере поступления (только новое содержимое)
                        print(content, end='', flush=True)
                        
                        # Проверяем конец предложения для озвучки
                        if re.search(r'[.!?]\s*$', current_sentence):
                            speak_text(current_sentence)
                            current_sentence = ""
                            
                except json.JSONDecodeError as e:
                    print(f"Ошибка декодирования JSON: {e}")
                    continue
                    
            # Озвучиваем оставшийся текст, если он есть
            if current_sentence.strip():
                speak_text(current_sentence)
            
            # Выводим оставшийся буфер
            if buffer:
                print(buffer, end='', flush=True)
            print("\n")  # Пустая строка после ответа
            
            # Озвучиваем полный ответ
            if full_response.strip():
                speak_text(full_response)
            
            return full_response.strip()
            
        else:
            error_msg = f"Ошибка при отправке запроса. Код ответа: {response.status_code}"
            if response.text:
                error_msg += f"\nТекст ответа: {response.text}"
            print(f"\n{error_msg}\n")
            # Озвучиваем сообщение об ошибке
            speak_text(error_msg)
            return error_msg
            
    except Exception as e:
        error_msg = f"Произошла ошибка: {str(e)}"
        print(f"\n{error_msg}\n")
        # Озвучиваем сообщение об ошибке
        speak_text(error_msg)
        return error_msg

def simulate_typing(text, delay=0.01):
    """Имитирует печатание текста, как в CMD."""
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()

def get_available_models():
    """Получает список доступных моделей с сервера."""
    global AVAILABLE_MODELS
    try:
        print("\nЗагрузка списка моделей...")
        response = requests.get(f"{BASE_URL}/models")
        if response.status_code == 200:
            models_data = response.json()
            AVAILABLE_MODELS = [model["id"] for model in models_data.get("data", [])]
            return AVAILABLE_MODELS
    except Exception as e:
        print(f"Ошибка при получении списка моделей: {str(e)}")
    return []

def show_interactive_menu():
    """Показывает интерактивное меню"""
    menu = [
        "1. Создать файл",
        "2. Создать папку",
        "3. Показать файлы",
        "4. Очистить экран",
        "5. Сменить модель",
        "6. Выход"
    ]
    
    print("\nГЛАВНОЕ МЕНЮ:")
    for item in menu:
        print(f"  {item}")
    
    while True:
        choice = input("\nВыберите пункт (1-6): ")
        if choice == '1':
            filename = input("Введите имя файла: ")
            return f"создай файл {filename}"
        elif choice == '2':
            dirname = input("Введите имя папки: ")
            return f"создай папку {dirname}"
        elif choice == '3':
            return "покажи файлы"
        elif choice == '4':
            return "очистить"
        elif choice == '5':
            return "смена модели"
        elif choice == '6':
            return "выход"
        else:
            print("Неверный выбор. Попробуйте еще раз.")

def analyze_requirements(prompt):
    """Анализирует требования к приложению из запроса пользователя"""
    # Определяем тип приложения
    app_type = "console"
    if any(word in prompt.lower() for word in ['веб', 'сайт', 'web']):
        app_type = "web"
    elif any(word in prompt.lower() for word in ['gui', 'интерфейс', 'окно']):
        app_type = "gui"
    
    # Определяем основные компоненты
    components = []
    if any(word in prompt.lower() for word in ['база данных', 'бд', 'sql']):
        components.append("database")
    if any(word in prompt.lower() for word in ['файл', 'документ']):
        components.append("file_operations")
    if any(word in prompt.lower() for word in ['api', 'запрос']):
        components.append("api")
    
    # Определяем язык программирования
    language = "python"
    if any(word in prompt.lower() for word in ['javascript', 'js', 'node']):
        language = "javascript"
    elif any(word in prompt.lower() for word in ['java']):
        language = "java"
    
    return {
        "app_type": app_type,
        "components": components,
        "language": language,
        "name": "my_app"
    }

def generate_app_structure(requirements):
    """Генерирует структуру приложения на основе требований"""
    structure = {}
    app_name = requirements["name"]
    
    # Базовые файлы для любого приложения
    structure["README.md"] = f"# {app_name}\n\nОписание приложения"
    structure["requirements.txt"] = ""
    
    # Файлы в зависимости от типа приложения
    if requirements["app_type"] == "web":
        structure["app.py"] = """from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return 'Привет, мир!'

if __name__ == '__main__':
    app.run(debug=True)"""
        structure["requirements.txt"] += "flask==2.0.1\n"
        
        # Создаем структуру папок для веб-приложения
        structure["templates/"] = ""
        structure["static/"] = ""
        structure["static/css/"] = ""
        structure["static/js/"] = ""
        
    elif requirements["app_type"] == "gui":
        structure["main.py"] = """import tkinter as tk
from tkinter import ttk

class App:
    def __init__(self, root):
        self.root = root
        self.root.title(\"\"\"My App\"\"\")
        self.setup_ui()
    
    def setup_ui(self):
        # Создаем и размещаем элементы интерфейса
        self.label = ttk.Label(self.root, text=\"Привет, мир!\")
        self.label.pack(padx=20, pady=20)
        
        self.button = ttk.Button(self.root, text=\"Нажми меня\", command=self.on_click)
        self.button.pack(pady=10)
    
    def on_click(self):
        self.label.config(text=\"Кнопка нажата!\")

if __name__ == \"__main__\":
    root = tk.Tk()
    app = App(root)
    root.mainloop()"""
        structure["requirements.txt"] += "customtkinter==5.2.0\n"
    
    else:  # console app
        structure["main.py"] = """def main():
    print(\"Привет, мир!\")

if __name__ == \"__main__\":
    main()"""
    
    # Добавляем компоненты
    if "database" in requirements["components"]:
        structure["models/"] = ""
        structure["models/__init__.py"] = ""
        structure["models/database.py"] = """from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = \"sqlite:///./app.db\"

engine = create_engine(DATABASE_URL, connect_args={\"check_same_thread\": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()"""
        structure["requirements.txt"] += "sqlalchemy==2.0.0\n"
    
    if "api" in requirements["components"]:
        structure["api/"] = ""
        structure["api/__init__.py"] = ""
        structure["api/routes.py"] = """from fastapi import APIRouter, Depends, HTTPException

router = APIRouter()

@router.get(\"/items/\")
async def read_items():
    return [{\"id\": 1, \"name\": \"Item 1\"}]"""
        structure["requirements.txt"] += "fastapi==0.104.0\nuvicorn==0.23.2\n"
    
    return structure

def create_file(filename, content=None):
    """Создает файл с указанным именем и содержимым"""
    try:
        # Создаем директорию, если её нет
        dirname = os.path.dirname(filename)
        if dirname and not os.path.exists(dirname):
            os.makedirs(dirname, exist_ok=True)
        
        # Если это директория, просто создаем её
        if filename.endswith('/'):
            os.makedirs(filename, exist_ok=True)
            return f"✓ Папка {os.path.abspath(filename)} создана"
        
        # Записываем содержимое в файл
        with open(filename, 'w', encoding='utf-8') as f:
            if content is not None:
                f.write(content)
        
        return f"✓ Файл {os.path.abspath(filename)} успешно создан"
    except Exception as e:
        return f"❌ Ошибка при создании {filename}: {str(e)}"

def create_folder(dirname):
    """Создает папку с указанным именем"""
    try:
        os.makedirs(dirname, exist_ok=True)
        return f"✓ Папка {os.path.abspath(dirname)} создана"
    except Exception as e:
        return f"❌ Ошибка при создании папки: {str(e)}"

def show_help():
    """Показывает справку по доступным командам."""
    help_text = """
ДОСТУПНЫЕ КОМАНДЫ:

Работа с файлами:
  создай папку [имя]    - Создать новую папку
  создай файл [имя]     - Создать новый файл
  покажи файлы          - Показать содержимое текущей папки
  меню                  - Показать интерактивное меню

Шаблоны для создания:
  создай игру крестики-нолики
  создай калькулятор
  создай приложение для заметок

Примеры команд:
  создай папку проект
  создай файл main.py в папке проект
  создай игру крестики-нолики в папке игры

Системные команды:
  очистить / cls        - Очистить экран
  смена модели          - Сменить модель ИИ
  лимит токенов / токены - Изменить максимальное количество токенов
  помощь                - Показать эту справку
  выход / exit          - Выйти из программы

СОВЕТ: Вы можете просто написать, что хотите создать, и ассистент предложит это сделать!
"""
    print(help_text)

def update_max_tokens_for_model(model_name):
    """Обновляет максимальное количество токенов в зависимости от выбранной модели."""
    global MAX_TOKENS, CURRENT_MODEL
    
    CURRENT_MODEL = model_name.lower()
    
    # Находим максимальную длину контекста для текущей модели
    for model_pattern, context_length in MODEL_CONTEXT_LENGTHS.items():
        if model_pattern.lower() in CURRENT_MODEL.lower():
            MAX_TOKENS = context_length
            return
    
    # Если модель не найдена в списке, используем значение по умолчанию
    MAX_TOKENS = MODEL_CONTEXT_LENGTHS['default']

def change_token_limit():
    """Позволяет изменить максимальное количество токенов вручную."""
    global MAX_TOKENS, CURRENT_MODEL
    
    if CURRENT_MODEL:
        model_max = next((length for pattern, length in MODEL_CONTEXT_LENGTHS.items() 
                        if pattern.lower() in CURRENT_MODEL.lower()),
                       MODEL_CONTEXT_LENGTHS['default'])
        print(f"\nТекущая модель: {CURRENT_MODEL}")
        print(f"Рекомендуемый максимум: {model_max} токенов")
    else:
        model_max = MODEL_CONTEXT_LENGTHS['default']
    
    print("\nТекущий лимит токенов:", MAX_TOKENS)
    print(f"Максимально возможное значение: {min(100000, model_max)}")
    
    while True:
        try:
            new_limit = input("\nВведите новое значение (или нажмите Enter для отмены): ").strip()
            if not new_limit:
                return "Отменено"
                
            new_limit = int(new_limit)
            if new_limit <= 0:
                print("Лимит должен быть положительным числом")
            elif new_limit > 100000:
                print("Максимально допустимое значение: 100000 токенов")
            else:
                MAX_TOKENS = min(new_limit, model_max)
                return f"Установлен лимит в {MAX_TOKENS} токенов"
                
        except ValueError:
            print("Пожалуйста, введите число")

def select_model():
    """Позволяет пользователю выбрать модель из списка доступных."""
    global MODEL_NAME, AVAILABLE_MODELS, MAX_TOKENS
    
    if not AVAILABLE_MODELS:
        print("\nЗагрузка списка моделей...")
        AVAILABLE_MODELS = get_available_models()
        
        if not AVAILABLE_MODELS:
            print("Не удалось загрузить список моделей. Используется модель по умолчанию.")
            return MODEL_NAME
    
    print("\nДоступные модели:")
    for i, model in enumerate(AVAILABLE_MODELS, 1):
        # Показываем максимальный контекст для каждой модели
        context_length = next((length for pattern, length in MODEL_CONTEXT_LENGTHS.items() 
                             if pattern.lower() in model.lower()), 
                            MODEL_CONTEXT_LENGTHS['default'])
        print(f"{i}. {model} (до {context_length} токенов)")
    
    while True:
        try:
            choice = input("\nВведите номер модели (или нажмите Enter для отмены): ")
            if not choice.strip():
                return MODEL_NAME
                
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(AVAILABLE_MODELS):
                MODEL_NAME = AVAILABLE_MODELS[choice_idx]
                update_max_tokens_for_model(MODEL_NAME)
                print(f"\nВыбрана модель: {MODEL_NAME}")
                print(f"Максимальный контекст: {MAX_TOKENS} токенов")
                return MODEL_NAME
            else:
                print("\nНеверный номер модели. Пожалуйста, попробуйте снова.")
        except ValueError:
            print("\nПожалуйста, введите число.")

def save_conversation_history(history):
    """Сохраняет историю разговора в файл"""
    try:
        with open('conversation_history.json', 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Не удалось сохранить историю: {e}")

def load_conversation_history():
    """Загружает историю разговора из файла"""
    try:
        if os.path.exists('conversation_history.json'):
            with open('conversation_history.json', 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"Не удалось загрузить историю: {e}")
    return []

def main():
    """Основная функция программы."""
    # Инициализация
    print_cmd_header()
    
    # Загрузка истории
    conversation_history = load_conversation_history()
    
    # Выбор модели
    global MODEL_NAME
    MODEL_NAME = select_model()
    
    current_dir = get_current_directory()
    
    # Приветственное сообщение
    print("\n" + "="*60)
    print("AI-АССИСТЕНТ ЗАПУЩЕН".center(60))
    print("="*60)
    print(f"Модель: {MODEL_NAME}")
    print(f"Текущая папка: {current_dir}")
    print("-"*60)
    show_help()
    print("-"*60)
    
    while True:
        # Выводим приглашение командной строки
        print_prompt(current_dir)
        
        # Получаем ввод пользователя
        user_input = input()
        
        # Обработка выхода
        if user_input.lower() in ['exit', 'quit', 'выход']:
            print("Выход из программы...")
            save_conversation_history(conversation_history[-100:])  # Сохраняем последние 100 сообщений
            break
        
        try:
            # Добавляем сообщение пользователя в историю
            if user_input.strip():
                conversation_history.append({"role": "user", "content": user_input.strip()})
            
            # Отправка запроса к AI
            response = send_to_ai(user_input.strip(), conversation_history)
            
            # Добавляем ответ ассистента в историю, если он есть и не пустой
            if response and response.strip():
                conversation_history.append({"role": "assistant", "content": response.strip()})
            
            # Автосохранение истории каждые 5 сообщений
            if len(conversation_history) % 5 == 0:
                save_conversation_history(conversation_history[-100:])
                
        except Exception as e:
            error_msg = f"Ошибка: {str(e)}"
            print(f"\n{error_msg}\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nРабота программы прервана пользователем.")
    except Exception as e:
        print(f"\nПроизошла непредвиденная ошибка: {str(e)}")
    finally:
        colorama.deinit()  # Сбрасываем настройки colorama
