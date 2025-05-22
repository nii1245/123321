import torch

# Загрузка модели
language = 'ru'
model_id = 'v3_1_ru'  # Модель для русского языка
device = torch.device('cpu')  # или 'cuda' если есть GPU

model, example_text = torch.hub.load(
    repo_or_dir='snakers4/silero-models',
    model='silero_tts',
    language=language,
    speaker=model_id
)
model.to(device)

# Синтез речи
text = "Привет! Это тест голоса от Silero TTS."
sample_rate = 48000  # Частота дискретизации
speaker = 'aidar'    # Варианты: 'aidar', 'baya', 'kseniya', 'xenia', 'random'

# Сохранение в файл
audio_path = 'output.wav'
model.save_wav(
    text=text,
    speaker=speaker,
    sample_rate=sample_rate,
    audio_path=audio_path
)

print(f"Аудио сохранено в {audio_path}")