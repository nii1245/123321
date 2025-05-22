import os
import sys
import pyttsx3
import requests
import tempfile
import vlc
import time

class VoiceTester:
    def __init__(self):
        self.engine = None
        self.voices = {}
        self._initialize()
    
    def _initialize(self):
        """Инициализирует голосовой движок"""
        try:
            print("Инициализация голосового движка...")
            self.engine = pyttsx3.init()
            
            # Получаем список доступных голосов
            voices = self.engine.getProperty('voices')
            
            # Показываем все доступные голоса
            print("\nДоступные голоса:")
            for i, voice in enumerate(voices):
                print(f"{i+1}. {voice.name}")
                if hasattr(voice, 'languages') and voice.languages:
                    print(f"   Языки: {voice.languages}")
                if hasattr(voice, 'id'):
                    print(f"   ID: {voice.id}")
                print()
            
            # Находим русские голоса
            ru_voices = [v for v in voices if hasattr(v, 'languages') and any('ru' in lang.lower() for lang in getattr(v, 'languages', []))]
            
            if not ru_voices:
                print("Русские голоса не найдены, будут использованы все доступные")
                ru_voices = voices
            
            # Настраиваем голоса
            self.voices = {
                "мужской": {
                    "id": next((v.id for v in ru_voices if 'male' in v.name.lower() or 'мужск' in v.name.lower() or v == ru_voices[0]), ru_voices[0].id),
                    "rate": 150,
                    "volume": 0.9
                },
                "женский": {
                    "id": next((v.id for v in ru_voices if 'female' in v.name.lower() or 'женск' in v.name.lower() or v == ru_voices[-1]), 
                               ru_voices[-1].id if len(ru_voices) > 1 else ru_voices[0].id),
                    "rate": 170,
                    "volume": 0.9
                }
            }
            
            print("\nВыбранные голоса:")
            for name, voice in self.voices.items():
                print(f"{name}: {voice['id']}")
            
            return True
            
        except Exception as e:
            print(f"Ошибка инициализации голосового движка: {str(e)}")
            return False
    
    def test_voice(self, text, voice_type="мужской"):
        """Тестирует голос"""
        if not self.engine or voice_type not in self.voices:
            print("Ошибка: голос не инициализирован")
            return
            
        print(f"\nТестируем голос: {voice_type}")
        print(f"Текст: {text}")
        
        voice = self.voices[voice_type]
        self.engine.setProperty('voice', voice["id"])
        self.engine.setProperty('rate', voice["rate"])
        self.engine.setProperty('volume', voice["volume"])
        
        print("Воспроизведение...")
        self.engine.say(text)
        self.engine.runAndWait()
        print("Готово!")

def main():
    print("=== Тест голосового синтеза ===\n")
    
    tester = VoiceTester()
    
    while True:
        print("\nВыберите действие:")
        print("1. Тест мужского голоса")
        print("2. Тест женского голоса")
        print("3. Выход")
        
        choice = input("Введите номер: ").strip()
        
        if choice == "1":
            text = input("Введите текст для озвучивания (или нажмите Enter для тестового): ").strip()
            if not text:
                text = "Привет! Это тестовое сообщение для проверки мужского голоса."
            tester.test_voice(text, "мужской")
            
        elif choice == "2":
            text = input("Введите текст для озвучивания (или нажмите Enter для тестового): ").strip()
            if not text:
                text = "Привет! Это тестовое сообщение для проверки женского голоса."
            tester.test_voice(text, "женский")
            
        elif choice == "3":
            print("Выход...")
            break
            
        else:
            print("Неверный выбор. Пожалуйста, попробуйте снова.")

if __name__ == "__main__":
    main()
