print("=== Минимальный тест TTS ===\n")

# Проверяем базовый импорт TTS
try:
    from TTS.api import TTS
    print("[OK] TTS успешно импортирован")
except Exception as e:
    print(f"[ОШИБКА] Не удалось импортировать TTS: {e}")
    print("Попробуйте: pip install TTS==0.22.0")
    exit(1)

# Проверяем PyTorch
try:
    import torch
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"[OK] PyTorch доступен. Устройство: {device}")
except Exception as e:
    print(f"[ОШИБКА] Проблема с PyTorch: {e}")
    print("Попробуйте: pip install torch torchaudio")
    exit(1)

# Пробуем загрузить модель
try:
    print("\nПопытка загрузить модель...")
    tts = TTS(model_name="tts_models/ru/vits", progress_bar=True, gpu=('cuda' in device))
    print("[OK] Модель успешно загружена!")
    
    if hasattr(tts, 'speakers') and tts.speakers:
        print(f"Доступные голоса: {tts.speakers}")
    else:
        print("Голоса не найдены")
        
except Exception as e:
    print(f"[ОШИБКА] Не удалось загрузить модель: {e}")
    print("\nВозможные решения:")
    print("1. Удалите кэш TTS: rmdir /s /q %USERPROFILE%\\.tts")
    print("2. Удалите и переустановите TTS:")
    print("   pip uninstall -y TTS")
    print("   pip install TTS==0.22.0")
    print("3. Проверьте подключение к интернету")
    exit(1)

# Пробуем сгенерировать речь
try:
    print("\nПробуем сгенерировать речь...")
    output_file = "test_output.wav"
    tts.tts_to_file(
        text="Привет! Это тестовое сообщение для проверки голоса.",
        file_path=output_file,
        speaker=tts.speakers[0] if hasattr(tts, 'speakers') and tts.speakers else None
    )
    print(f"[OK] Аудио сохранено в {output_file}")
    
    # Пробуем воспроизвести
    try:
        import sounddevice as sd
        import soundfile as sf
        data, samplerate = sf.read(output_file)
        print("Воспроизведение... (нажмите Ctrl+C для остановки)")
        sd.play(data, samplerate)
        sd.wait()
    except Exception as e:
        print(f"Не удалось воспроизвести: {e}")
        print("Попробуйте: pip install sounddevice soundfile")
        
except Exception as e:
    print(f"[ОШИБКА] Не удалось сгенерировать речь: {e}")
    exit(1)

print("\nТест завершен успешно!")
