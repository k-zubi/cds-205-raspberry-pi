from abc import ABC, abstractmethod


class BaseASRClient(ABC):

    @abstractmethod
    def transcribe(self, audio_data_uri: str) -> str:
        pass