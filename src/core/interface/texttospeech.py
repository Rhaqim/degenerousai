from abc import abstractmethod
from core.interface.base import AIServiceBase


class TextToSpeechServiceBase(AIServiceBase):
    """
    Base class for text-to-speech AI services.
    """

    @abstractmethod
    def process_request(self, text: str, **kwargs):
        """
        Abstract method to process text-to-speech requests.
        Must be implemented by subclasses.
        """
        pass
