from typing import Iterator

from elevenlabs.client import ElevenLabs
from elevenlabs import stream

from tts.base_tts_client import BaseTTSClient


class ElevenLabsTTSClient(BaseTTSClient):

    def __init__(self):
        super().__init__()
        self.client: ElevenLabs = ElevenLabs()

    def read_text(self,
                  text: str,
                  model: str = "eleven_turbo_v2_5",
                  voice: str = "aEO01A4wXwd1O8GPgGlF",
                  stream_read: bool = True,
                  play: bool = True) -> Iterator[bytes] | None:
        audio_stream: Iterator[bytes] = self.client.generate(
            text=text,
            voice=voice,
            model=model,
            stream=stream_read
        )
        if play:
            self.stream_play(audio_stream=audio_stream)
        else:
            return audio_stream

    def read_text_from_iterator(self,
                                text_iterator: Iterator[str],
                                model: str = "eleven_turbo_v2_5",
                                voice: str = "aEO01A4wXwd1O8GPgGlF",
                                stream_read: bool = True,
                                play: bool = True) -> Iterator[bytes] | None:
        audio_stream: Iterator[bytes] = self.client.generate(
            text=text_iterator,
            voice=voice,
            model=model,
            stream=stream_read
        )
        if play:
            self.stream_play(audio_stream=audio_stream)
        else:
            return audio_stream


    @staticmethod
    def stream_play(audio_stream: Iterator[bytes]):
        """Plays the sound from a stream on the default output device using MPV."""
        stream(audio_stream=audio_stream)
