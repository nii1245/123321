import os
import sys
from TTS.api import TTS

def main():
    print("Проверка установки TTS...")
    print("Версия TTS:", TTS.__version__)
    
    print("\nДоступные модели:")
    try:
        # Получаем список всех доступных моделей
        models = [
            "tts_models/ru/vits",
            "tts_models/en/ljspeech/tacotron2-DDC"
        ]
        
        for model in models:
            print(f"\nПроверка модели: {model}")
            try:
                tts = TTS(model_name=model, progress_bar=False, gpu=False)
                print(f"Модель загружена: {model}")
                
                if hasattr(tts, 'speakers') and tts.speakers:
                    print(f"Доступные голоса: {tts.speakers}")
                
                print("Тестовая фраза...")
                tts.tts_to_file(text="Привет, это тест", file_path="test_output.wav")
                print("Файл сохранен: test_output.wav")
                
            except Exception as e:
                print(f"Ошибка с моделью {model}: {str(e)}")
    
    except Exception as e:
        print(f"Критическая ошибка: {str(e)}")
        print("\nВозможные решения:")
        print("1. Удалите кэш TTS: rm -r ~/.local/share/tts")
        print("2. Переустановите TTS: pip install --force-reinstall TTS")
        print("3. Проверьте подключение к интернету при первом запуске")

if __name__ == "__main__":
    main()
