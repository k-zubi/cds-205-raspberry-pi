from abc import ABC, abstractmethod
from typing import Iterator


class BaseTTSClient(ABC):

    @abstractmethod
    def read_text(self,
                  text: str,
                  model: str = None,
                  voice: str = None,
                  stream_read: bool = True) -> Iterator[bytes]:
        pass

    @abstractmethod
    def read_text_from_iterator(self,
                                text_iterator: Iterator[str],
                                model: str = None,
                                voice: str = None,
                                stream_read: bool = True) -> Iterator[bytes]:
        pass
