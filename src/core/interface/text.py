from abc import abstractmethod
from core.interface.base import AIServiceBase


class TextServiceBase(AIServiceBase):
    """
    Base class for text-based AI services.
    """

    def process_request(self, prompt: str, **kwargs):
        """
        Process a text-based request using OpenAI API.
        """
        pass

    @abstractmethod
    def create_chat_completion(self, messages: list, **kwargs):
        """
        Abstract method to create chat completion.
        Must be implemented by subclasses.
        """
        pass