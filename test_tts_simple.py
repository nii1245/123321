print("Проверка TTS...")

try:
    from TTS.api import TTS
    import torch
    
    print("TTS успешно импортирован")
    
    # Проверяем доступность CUDA
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"Используемое устройство: {device}")
    
    # Пробуем загрузить русскую модель
    print("\nПопытка загрузить русскую модель...")
    try:
        tts = TTS(model_name="tts_models/ru/vits", progress_bar=False, gpu=('cuda' in device))
        print("Русская модель успешно загружена!")
        print("Доступные голоса:", tts.speakers)
        
        # Пробуем сгенерировать речь
        print("\nПробуем сгенерировать речь...")
        tts.tts_to_file(text="Привет, это тестовое сообщение.", 
                       file_path="test_output.wav",
                       speaker=tts.speakers[0] if tts.speakers else None)
        print("Аудио сохранено в test_output.wav")
        
    except Exception as e:
        print(f"Ошибка при загрузке модели: {e}")
    
except Exception as e:
    print(f"Критическая ошибка: {e}")
    print("\nПопробуйте выполнить следующие шаги:")
    print("1. pip uninstall -y TTS")
    print("2. pip install TTS==0.22.0")
    print("3. Убедитесь, что у вас установлен PyTorch с поддержкой CUDA (если есть видеокарта)")
    print("4. Проверьте подключение к интернету для загрузки моделей")
