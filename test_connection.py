import requests
import json

# URL для проверки подключения
base_url = "http://26.224.68.101:1234/v1"
models_url = f"{base_url}/models"

print(f"Проверка подключения к серверу LM Studio по адресу: {base_url}")

try:
    # Проверка доступности API
    response = requests.get(models_url)
    
    if response.status_code == 200:
        print("Подключение успешно!")
        print("Доступные модели:")
        models = response.json()
        print(json.dumps(models, indent=2, ensure_ascii=False))
    else:
        print(f"Ошибка при подключении. Код ответа: {response.status_code}")
        print(f"Текст ответа: {response.text}")
        
except Exception as e:
    print(f"Произошла ошибка при подключении: {str(e)}")
    print("\nПроверьте, что:")
    print("1. Сервер LM Studio запущен и работает")
    print("2. API доступен по указанному адресу")
    print("3. Нет проблем с сетевым подключением или брандмауэром")
