import torch
import sounddevice as sd

def main():
    print("Инициализация Silero TTS...")
    
    # Доступные голоса
    speakers = {
        'aidar': 'мужской',
        'baya': 'женский',
        'kseniya': 'женский',
        'xenia': 'женский'
    }
    
    try:
        # Загружаем модель
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"Используется устройство: {device}")
        
        model, _ = torch.hub.load(repo_or_dir='snakers4/silero-models',
                                model='silero_tts',
                                language='ru',
                                speaker='v3_1_ru')
        model.to(device)
        
        while True:
            print("\nВыберите голос:")
            for i, (speaker_id, gender) in enumerate(speakers.items(), 1):
                print(f"{i}. {speaker_id} ({gender})")
            print("0. Выход")
            
            choice = input("\nВаш выбор: ").strip()
            
            if choice == '0':
                break
                
            try:
                speaker_id = list(speakers.keys())[int(choice)-1]
                text = input("Введите текст для озвучивания: ")
                
                if not text:
                    text = "Привет! Это тестовое сообщение."
                
                print(f"\nГенерация речи голосом {speaker_id}...")
                
                # Генерируем речь
                audio = model.apply_tts(text=text,
                                     speaker=speaker_id,
                                     sample_rate=48000)
                
                # Воспроизводим
                print("Воспроизведение...")
                sd.play(audio.cpu().numpy(), 48000)
                sd.wait()
                
            except (ValueError, IndexError):
                print("Неверный выбор. Пожалуйста, попробуйте снова.")
            except Exception as e:
                print(f"Ошибка: {str(e)}")
    
    except Exception as e:
        print(f"\nОшибка при инициализации: {str(e)}")
        print("\nУбедитесь, что у вас установлены все зависимости:")
        print("pip install torch torchaudio sounddevice")

if __name__ == "__main__":
    print("=== Тест Silero TTS ===\n")
    main()
