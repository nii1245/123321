import os
import torch
from TTS.api import TTS
import sounddevice as sd
import numpy as np
import soundfile as sf
import tempfile

def test_coqui_tts():
    print("Инициализация Coqui TTS...")
    
    # Используем русскую VITS модель
    model_name = "tts_models/ru/vits"
    
    try:
        # Инициализируем модель
        tts = TTS(model_name=model_name, progress_bar=False, gpu=torch.cuda.is_available())
        print(f"Модель {model_name} успешно загружена")
        
        # Доступные спикеры
        speakers = ["aidar", "baya", "kseniya", "xenia", "eugene"]
        
        while True:
            print("\nДоступные голоса:")
            for i, speaker in enumerate(speakers):
                print(f"{i+1}. {speaker}")
            print("0. Выход")
            
            try:
                choice = input("\nВыберите голос (или 0 для выхода): ").strip()
                if choice == "0":
                    break
                    
                speaker_idx = int(choice) - 1
                if 0 <= speaker_idx < len(speakers):
                    speaker = speakers[speaker_idx]
                    text = input("Введите текст для озвучивания: ").strip()
                    
                    if not text:
                        text = "Привет! Это тестовое сообщение для проверки голоса."
                    
                    print(f"\nГенерация речи с голосом {speaker}...")
                    
                    # Создаем временный файл для аудио
                    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
                        temp_file = f.name
                    
                    try:
                        # Генерируем речь
                        tts.tts_to_file(
                            text=text,
                            file_path=temp_file,
                            speaker=speaker
                        )
                        
                        # Загружаем и воспроизводим аудио
                        data, samplerate = sf.read(temp_file)
                        
                        # Нормализуем громкость
                        max_volume = np.max(np.abs(data))
                        if max_volume > 0:
                            data = data * (0.9 / max_volume)
                        
                        print("Воспроизведение... (нажмите Ctrl+C для остановки)")
                        sd.play(data, samplerate)
                        sd.wait()
                        
                    finally:
                        # Удаляем временный файл
                        try:
                            os.unlink(temp_file)
                        except:
                            pass
                else:
                    print("Неверный выбор голоса")
                    
            except (ValueError, KeyboardInterrupt):
                print("\nВозврат в меню...")
                continue
                
    except Exception as e:
        print(f"Ошибка при инициализации Coqui TTS: {str(e)}")
        print("Убедитесь, что модель загружена и доступна.")
        print("Попробуйте выполнить: tts --model_name tts_models/ru/vits --list_speaker_idxs")

if __name__ == "__main__":
    print("=== Тест Coqui TTS ===\n")
    print("Проверка доступности CUDA:", "Доступно" if torch.cuda.is_available() else "Не доступно")
    test_coqui_tts()
