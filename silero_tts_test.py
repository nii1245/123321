import torch
import sounddevice as sd
import time

def main():
    print("Проверка доступности CUDA:", "Доступно" if torch.cuda.is_available() else "Не доступно")
    
    try:
        print("\nЗагрузка модели Silero TTS...")
        language = 'ru'
        model_id = 'v3_1_ru'
        sample_rate = 48000
        speaker = 'aidar'  # 'aidar', 'baya', 'kseniya', 'xenia', 'random'
        put_accent = True
        put_yo = True
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        print(f"Используется устройство: {device}")
        
        model, _ = torch.hub.load(repo_or_dir='snakers4/silero-models',
                                model='silero_tts',
                                language=language,
                                speaker=model_id)
        model.to(device)
        
        print("\nДоступные голоса:")
        print("1. aidar (мужской)")
        print("2. baya (женский)")
        print("3. kseniya (женский)")
        print("4. xenia (женский)")
        
        while True:
            choice = input("\nВыберите голос (1-4) или 'выход' для выхода: ").strip().lower()
            
            if choice in ['выход', 'exit', 'quit']:
                break
                
            voice_map = {
                '1': 'aidar',
                '2': 'baya',
                '3': 'kseniya',
                '4': 'xenia'
            }
            
            if choice not in voice_map:
                print("Неверный выбор. Пожалуйста, введите число от 1 до 4.")
                continue
                
            speaker = voice_map[choice]
            text = input("Введите текст для озвучивания: ").strip()
            
            if not text:
                text = "Привет! Это тестовое сообщение для проверки голоса."
            
            print(f"\nГенерация речи с голосом {speaker}...")
            
            try:
                audio = model.apply_tts(text=text,
                                     speaker=speaker,
                                     sample_rate=sample_rate,
                                     put_accent=put_accent,
                                     put_yo=put_yo)
                
                print("Воспроизведение... (нажмите Ctrl+C для остановки)")
                sd.play(audio.cpu().numpy(), sample_rate)
                sd.wait()
                
            except Exception as e:
                print(f"Ошибка при генерации речи: {e}")
                
    except Exception as e:
        print(f"\nОшибка: {e}")
        print("\nВозможные решения:")
        print("1. Проверьте подключение к интернету")
        print("2. Установите последнюю версию PyTorch: pip install torch torchaudio")
        print("3. Установите sounddevice: pip install sounddevice")
        print("4. Проверьте наличие CUDA, если используете видеокарту")

if __name__ == "__main__":
    print("=== Тест Silero TTS ===\n")
    main()
