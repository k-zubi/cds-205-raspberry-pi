from audio_recorder.base_audio_recorder import BaseAudioRecorder
import pyaudio
import wave
from pynput import keyboard
import base64
import io


class PyAudioKeyboardAudioRecorder(BaseAudioRecorder):

    def __init__(self,
                 chunk: int = 8192,
                 pyaudio_format = pyaudio.paInt16,
                 channels: int = 1,
                 rate: int = 44100):
        super().__init__()
        self.CHUNK = chunk
        self.FORMAT = pyaudio_format
        self.CHANNELS = channels
        self.RATE = rate

    def record(self) -> str:
        p = pyaudio.PyAudio()
        frames = []
        recording = True

        def on_press(key):
            nonlocal recording
            if key == keyboard.Key.space:
                recording = False
                return False

        stream = p.open(format=self.FORMAT,
                        channels=self.CHANNELS,
                        rate=self.RATE,
                        input=True,
                        frames_per_buffer=self.CHUNK)

        listener = keyboard.Listener(on_press=on_press)
        listener.start()

        print("Recording... Press SPACE to stop")

        while recording:
            try:
                data = stream.read(self.CHUNK)
                frames.append(data)
            except IOError as e:
                print(repr(e))
                continue

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

        # For Debugging:
        # with wave.open("last_recording.wav", 'wb') as wf:
        #     wf.setnchannels(self.CHANNELS)
        #     wf.setsampwidth(p.get_sample_size(self.FORMAT))
        #     wf.setframerate(self.RATE)
        #     wf.writeframes(b''.join(frames))

        return f"data:audio/x-wav;base64,{audio_base64}"
