import requests
import json
import time
import sys

# Настройки подключения
base_url = "http://26.224.68.101:1234/v1"
model_name = "saiga_mistral_7b_gguf"
api_key = "lm-studio"  # Для LM Studio это значение обычно не важно

def print_step(step, message):
    """Выводит информацию о текущем шаге отладки."""
    print(f"\n[Шаг {step}] {message}")
    time.sleep(0.5)  # Небольшая пауза для лучшей читаемости

# Начинаем отладку
print("="*60)
print("ОТЛАДКА ПОДКЛЮЧЕНИЯ К API LM STUDIO".center(60))
print("="*60)

# Шаг 1: Проверка доступности сервера
print_step(1, "Проверка доступности сервера")
try:
    response = requests.get(f"{base_url}/models")
    if response.status_code == 200:
        print("✓ Сервер доступен")
        models = response.json()
        print("Доступные модели:")
        for model in models.get("data", []):
            print(f"  - {model['id']}")
        
        # Проверяем, доступна ли нужная модель
        available_models = [model["id"] for model in models.get("data", [])]
        if model_name in available_models:
            print(f"✓ Модель {model_name} доступна")
        else:
            print(f"✗ Модель {model_name} не найдена среди доступных моделей")
            print(f"  Пожалуйста, выберите одну из доступных моделей")
            sys.exit(1)
    else:
        print(f"✗ Ошибка при подключении к серверу. Код ответа: {response.status_code}")
        print(f"  Текст ответа: {response.text}")
        sys.exit(1)
except Exception as e:
    print(f"✗ Ошибка при подключении к серверу: {str(e)}")
    sys.exit(1)

# Шаг 2: Проверка возможности отправки запроса
print_step(2, "Проверка возможности отправки запроса")
try:
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    data = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": "Ты помощник."},
            {"role": "user", "content": "Привет! Как дела?"}
        ],
        "temperature": 0.7,
        "max_tokens": 100
    }
    
    print("Отправка тестового запроса...")
    response = requests.post(
        f"{base_url}/chat/completions", 
        headers=headers,
        json=data
    )
    
    if response.status_code == 200:
        result = response.json()
        print("✓ Запрос успешно обработан")
        print("\nОтвет модели:")
        print("-" * 40)
        print(result["choices"][0]["message"]["content"])
        print("-" * 40)
    else:
        print(f"✗ Ошибка при отправке запроса. Код ответа: {response.status_code}")
        print(f"  Текст ответа: {response.text}")
        sys.exit(1)
except Exception as e:
    print(f"✗ Ошибка при отправке запроса: {str(e)}")
    sys.exit(1)

# Шаг 3: Проверка возможности отправки сложного запроса
print_step(3, "Проверка возможности отправки сложного запроса")
try:
    data = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": "Ты универсальный автономный агент, способный работать с файлами, кодом, данными, API и многим другим."},
            {"role": "user", "content": "Напиши простую функцию на Python для подсчета факториала числа."}
        ],
        "temperature": 0.7,
        "max_tokens": 500
    }
    
    print("Отправка сложного запроса...")
    response = requests.post(
        f"{base_url}/chat/completions", 
        headers=headers,
        json=data
    )
    
    if response.status_code == 200:
        result = response.json()
        print("✓ Сложный запрос успешно обработан")
        print("\nОтвет модели:")
        print("-" * 40)
        print(result["choices"][0]["message"]["content"])
        print("-" * 40)
        
        print("\n✓ Все проверки пройдены успешно!")
        print("API LM Studio работает корректно и готово к использованию.")
        print("\nТеперь вы можете запустить скрипт simple_run.py для выполнения задач.")
    else:
        print(f"✗ Ошибка при отправке сложного запроса. Код ответа: {response.status_code}")
        print(f"  Текст ответа: {response.text}")
        sys.exit(1)
except Exception as e:
    print(f"✗ Ошибка при отправке сложного запроса: {str(e)}")
    sys.exit(1)
