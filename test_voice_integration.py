from cmd_assistant import VoiceManager
import time

def main():
    print("Тестирование голосового движка...")
    
    # Инициализируем голосовой менеджер
    voice_manager = VoiceManager()
    
    if not voice_manager.enabled:
        print("Не удалось инициализировать голосовой движок")
        return
    
    # Тестируем голоса
    test_text = "Привет! Это тестовое сообщение для проверки голосового движка."
    
    print("\nТестируем мужской голос...")
    voice_manager.current_voice = "мужской"
    voice_manager.speak(test_text)
    time.sleep(3)  # Ждем окончания воспроизведения
    
    print("\nТестируем женский голос...")
    voice_manager.current_voice = "женский"
    voice_manager.speak(test_text)
    time.sleep(3)
    
    print("\nТестируем отключение голоса...")
    print(voice_manager.toggle(False))
    voice_manager.speak("Это сообщение не должно быть озвучено")
    
    print("\nТестируем включение голоса...")
    print(voice_manager.toggle(True))
    voice_manager.speak("Голос снова включен!")
    
    print("\nТестируем смену голоса через метод...")
    print(voice_manager.change_voice("мужской"))
    voice_manager.speak("Теперь снова мужской голос")
    
    print("\nТестируем остановку воспроизведения...")
    voice_manager.speak("Это сообщение будет прервано через секунду")
    time.sleep(1)
    print(voice_manager.stop())
    
    print("\nТестирование завершено!")

if __name__ == "__main__":
    main()
