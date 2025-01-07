from asr.base_asr_client import BaseASRClient
import fal_client


class FalAiASRClient(BaseASRClient):

    def transcribe(self, audio_data_uri: str) -> str:
        response: dict[str, str | list] = fal_client.subscribe(
            "fal-ai/wizper",
            arguments={
                "audio_url": audio_data_uri,
                "task": "transcribe",
                "language": "en"
            },
            with_logs=True
        )
        return response["text"] or ""
