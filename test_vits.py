from TTS.api import TTS
import torch
import time

def main():
    print("Инициализация русской VITS модели...")
    
    try:
        # Инициализируем русскую VITS модель
        tts = TTS(model_name="tts_models/ru/vits", progress_bar=True)
        
        # Показываем доступные голоса
        print("\nДоступные голоса:")
        for i, speaker in enumerate(tts.speakers):
            print(f"{i+1}. {speaker}")
        
        # Тестируем голоса
        test_text = "Привет! Это тестовое сообщение для проверки голоса."
        
        for i, speaker in enumerate(tts.speakers):
            print(f"\nТестирую голос: {speaker}")
            output_file = f"output_{i+1}.wav"
            
            try:
                tts.tts_to_file(
                    text=test_text,
                    file_path=output_file,
                    speaker=speaker
                )
                print(f"Аудио сохранено в {output_file}")
                
            except Exception as e:
                print(f"Ошибка с голосом {speaker}: {str(e)}")
    
    except Exception as e:
        print(f"Ошибка при инициализации модели: {str(e)}")
        print("\nПопробуйте выполнить следующие шаги:")
        print("1. Удалите кэш TTS: rm -r ~/.local/share/tts")
        print("2. Переустановите TTS: pip install --force-reinstall TTS")
        print("3. Проверьте подключение к интернету")

if __name__ == "__main__":
    main()
