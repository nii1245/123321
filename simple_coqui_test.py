from TTS.api import TTS
import torch

def main():
    print("Доступные модели TTS:")
    print("-" * 50)
    
    # Получаем список всех доступных моделей
    models = [
        "tts_models/ru/vits",
        "tts_models/multilingual/multi-dataset/your_tts",
        "tts_models/en/ek1/tacotron2"
    ]
    
    for i, model in enumerate(models, 1):
        print(f"{i}. {model}")
    
    try:
        choice = int(input("\nВыберите модель (1-3): ")) - 1
        if 0 <= choice < len(models):
            model_name = models[choice]
            print(f"\nЗагрузка модели {model_name}...")
            
            # Инициализируем TTS
            tts = TTS(model_name=model_name, progress_bar=True, gpu=torch.cuda.is_available())
            
            # Показываем доступные голоса
            if hasattr(tts, 'speakers') and tts.speakers is not None:
                print("\nДоступные голоса:", tts.speakers)
            
            if hasattr(tts, 'language') and tts.language is not None:
                print("Язык модели:", tts.language)
                
            # Тестируем голос
            while True:
                text = input("\nВведите текст для озвучивания (или 'выход' для выбора модели): ")
                if text.lower() in ['выход', 'exit', 'quit']:
                    break
                
                output_file = "test_output.wav"
                print("Генерация речи...")
                
                try:
                    tts.tts_to_file(text=text, file_path=output_file)
                    print(f"Аудио сохранено в {output_file}")
                    
                    # Пытаемся воспроизвести
                    try:
                        import sounddevice as sd
                        import soundfile as sf
                        data, samplerate = sf.read(output_file)
                        sd.play(data, samplerate)
                        sd.wait()
                    except Exception as e:
                        print(f"Не удалось воспроизвести аудио: {e}")
                        
                except Exception as e:
                    print(f"Ошибка при генерации речи: {e}")
                    
        else:
            print("Неверный выбор модели")
            
    except (ValueError, KeyboardInterrupt):
        print("\nВыход...")

if __name__ == "__main__":
    main()
