from abc import abstractmethod
from core.interface.base import AIServiceBase


class TextToSpeechServiceBase(AIServiceBase):
    """
    Base class for text-to-speech AI services.
    """

    @abstractmethod
    def process_request(
        self, text: str, lang_code: str, voice: str, speed: float = 1.0, **kwargs
    ):
        """
        Abstract method to process text-to-speech requests.
        Must be implemented by subclasses.
        """
        pass
