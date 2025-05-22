import nemo.collections.tts as nemo_tts

# Загружаем предобученную модель Tacotron2
model = nemo_tts.models.Tacotron2Model.from_pretrained("tts_en_tacotron2")

# Текст для озвучки
text = "Hello, this is a test of NVIDIA NeMo TTS."

# Генерируем мел-спектрограмму
spectrogram = model.parse(text)

# Для преобразования в аудио нужна WaveGlow
waveglow = nemo_tts.models.WaveGlowModel.from_pretrained("tts_waveglow_88m")

audio = waveglow.convert_spectrogram_to_audio(spec=spectrogram)

# Сохраняем в файл
import soundfile as sf
sf.write("output.wav", audio.cpu().numpy(), samplerate=22050)
