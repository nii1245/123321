import pyttsx3

def list_voices():
    """Показывает все доступные голоса"""
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    
    print("\nДоступные голоса:")
    for i, voice in enumerate(voices):
        print(f"\nГолос #{i+1}:")
        print(f"Имя: {voice.name}")
        print(f"ID: {voice.id}")
        if hasattr(voice, 'languages') and voice.languages:
            print(f"Языки: {voice.languages}")
    
    return voices

def test_voice(voice_id, text):
    """Тестирует голос с заданным ID"""
    try:
        engine = pyttsx3.init()
        engine.setProperty('voice', voice_id)
        engine.setProperty('rate', 150)  # Скорость речи
        engine.setProperty('volume', 0.9)  # Громкость (0.0-1.0)
        
        print(f"\nТестируем голос: {voice_id}")
        print(f"Текст: {text}")
        print("Воспроизведение...")
        
        engine.say(text)
        engine.runAndWait()
        print("Готово!")
        return True
    except Exception as e:
        print(f"Ошибка: {str(e)}")
        return False

if __name__ == "__main__":
    print("=== Тест голосового синтеза ===\n")
    
    # Показываем все доступные голоса
    voices = list_voices()
    
    while True:
        print("\nВыберите действие:")
        print("1. Протестировать голос по номеру")
        print("2. Выход")
        
        choice = input("Введите номер: ").strip()
        
        if choice == "1":
            try:
                voice_num = int(input(f"Введите номер голоса (1-{len(voices)}): ").strip())
                if 1 <= voice_num <= len(voices):
                    text = input("Введите текст для озвучивания (или нажмите Enter для тестового): ").strip()
                    if not text:
                        text = "Привет! Это тестовое сообщение для проверки голоса."
                    test_voice(voices[voice_num-1].id, text)
                else:
                    print("Неверный номер голоса")
            except ValueError:
                print("Пожалуйста, введите число")
                
        elif choice == "2":
            print("Выход...")
            break
            
        else:
            print("Неверный выбор. Пожалуйста, попробуйте снова.")
