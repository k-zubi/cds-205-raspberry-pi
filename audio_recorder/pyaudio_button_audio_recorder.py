from audio_recorder.base_audio_recorder import BaseAudioRecorder
import pyaudio
import wave
import base64
import io
from gpiozero import Button
import time


class PyAudioButtonAudioRecorder(BaseAudioRecorder):

    def __init__(self,
                 chunk: int = 8192,
                 pyaudio_format=pyaudio.paInt16,
                 channels: int = 1,
                 rate: int = 44100,
                 button_pin: int = 17):
        super().__init__()
        self.CHUNK = chunk
        self.FORMAT = pyaudio_format
        self.CHANNELS = channels
        self.RATE = rate
        self.button = Button(button_pin, pull_up=True)

    def record(self) -> str:
        p = pyaudio.PyAudio()
        frames = []
        recording = False
        started = False

        stream = p.open(format=self.FORMAT,
                       channels=self.CHANNELS,
                       rate=self.RATE,
                       input=True,
                       frames_per_buffer=self.CHUNK)

        print("Press the HAT button to start recording...")

        while not started:
            if self.button.is_pressed:
                recording = True
                started = True
                print("Recording started... Press button again to stop")
                time.sleep(0.2)  # Debounce delay

        def stop_recording():
            nonlocal recording
            recording = False

        self.button.when_pressed = stop_recording

        while recording:
            try:
                data = stream.read(self.CHUNK)
                frames.append(data)
            except IOError as e:
                print(repr(e))
                continue

        print("Recording stopped")

        stream.stop_stream()
        stream.close()
        p.terminate()

        buffer = io.BytesIO()
        with wave.open(buffer, 'wb') as wf:
            wf.setnchannels(self.CHANNELS)
            wf.setsampwidth(p.get_sample_size(self.FORMAT))
            wf.setframerate(self.RATE)
            wf.writeframes(b''.join(frames))
        buffer.flush()
        buffer.seek(0)

        wav_bytes = buffer.getvalue()
        audio_base64 = base64.b64encode(wav_bytes).decode('utf-8')

        return f"data:audio/x-wav;base64,{audio_base64}"
