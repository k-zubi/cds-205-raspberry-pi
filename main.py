from asr.base_asr_client import BaseASRClient
from asr.fal_ai_asr_client import FalAiASRClient
from audio_recorder.base_audio_recorder import BaseAudioRecorder
from audio_recorder.pyaudio_keyboard_audio_recorder import PyAudioKeyboardAudioRecorder
from core.chat import Chat
from tts.elevenlabs_tts_client import ElevenLabsTTSClient


if __name__ == "__main__":
    asr: BaseASRClient = FalAiASRClient()
    audio_recorder: BaseAudioRecorder = PyAudioKeyboardAudioRecorder()
    tts: ElevenLabsTTSClient = ElevenLabsTTSClient()

    chat: Chat = Chat()
    running: bool = True
    while running:
        recorded_audio_as_uri: str = audio_recorder.record()
        transcription: str = asr.transcribe(audio_data_uri=recorded_audio_as_uri)
        print(f"User:\n{transcription}\n\n", end="")
        print("Assistant:")

        assistant_response: str = ""
        for chunk in chat.send_user_message(user_message=transcription, stream=True):
            print(chunk, end="")
            assistant_response += chunk
        print("\n\n", end="")
        tts.read_text(text=assistant_response)
