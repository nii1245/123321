import torch
import os
import threading
import sounddevice as sd
import numpy as np

class VoiceManager:
    def __init__(self):
        self.enabled = False
        self.current_voice = "мужской"
        self.model = None
        self.sample_rate = 48000
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.voices = {
            "мужской": "aidar",
            "женский": "baya"
        }
        self._initialize()
    
    def _initialize(self):
        """Инициализирует голосовой движок"""
        try:
            print("Инициализация Silero TTS...")
            self.model, _ = torch.hub.load(
                repo_or_dir='snakers4/silero-models',
                model='silero_tts',
                language='ru',
                speaker='v3_1_ru'
            )
            self.model.to(self.device)
            self.enabled = True
            print(f"Голосовой движок инициализирован (устройство: {self.device})")
            return True
        except Exception as e:
            print(f"Ошибка инициализации голосового движка: {str(e)}")
            self.enabled = False
            return False

    def speak(self, text):
        """Озвучивает текст"""
        if not self.enabled or not text.strip():
            return
            
        def _speak():
            try:
                # Генерируем аудио
                speaker = self.voices.get(self.current_voice, "aidar")
                audio = self.model.apply_tts(
                    text=text,
                    speaker=speaker,
                    sample_rate=self.sample_rate
                )
                
                # Воспроизводим аудио
                if isinstance(audio, torch.Tensor):
                    audio = audio.cpu().numpy()
                
                sd.play(audio, self.sample_rate)
                sd.wait()
                
            except Exception as e:
                print(f"Ошибка при воспроизведении речи: {str(e)}")
        
        # Запускаем в отдельном потоке, чтобы не блокировать основной
        threading.Thread(target=_speak, daemon=True).start()

    def change_voice(self, voice_name):
        """Меняет голос"""
        if voice_name not in self.voices:
            return f"Такого голоса нет в списке. Доступные голоса: {', '.join(self.voices.keys())}"
            
        if voice_name == self.current_voice:
            return f"Уже выбран голос: {voice_name}"
            
        self.current_voice = voice_name
        return f"Голос изменён на {voice_name}"

    def toggle(self, state=None):
        """Включает/выключает голос"""
        if state is not None:
            self.enabled = bool(state)
        else:
            self.enabled = not self.enabled
        status = "включен" if self.enabled else "выключен"
        return f"Голос {status}"

    def stop(self):
        """Останавливает текущее воспроизведение"""
        try:
            sd.stop()
            return "Воспроизведение остановлено"
        except Exception as e:
            print(f"Ошибка при остановке воспроизведения: {str(e)}")
            return "Не удалось остановить воспроизведение"

# Пример использования
if __name__ == "__main__":
    import time
    
    voice = VoiceManager()
    
    if voice.enabled:
        print("Тестируем голос...")
        voice.speak("Привет! Это тестовое сообщение для проверки голоса.")
        
        print("Меняем на женский голос...")
        print(voice.change_voice("женский"))
        time.sleep(1)
        
        voice.speak("Теперь у меня женский голос. Как вам?")
        
        print("Отключаем голос...")
        print(voice.toggle(False))
    else:
        print("Не удалось инициализировать голосовой движок")
