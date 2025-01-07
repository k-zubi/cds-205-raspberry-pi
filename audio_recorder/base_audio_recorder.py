from abc import ABC, abstractmethod


class BaseAudioRecorder(ABC):

    @abstractmethod
    def record(self) -> str:
        pass
