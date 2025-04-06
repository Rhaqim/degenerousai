from abc import ABC, abstractmethod


class AIServiceBase(ABC):
    """
    Base class for all AI services.
    """

    def __init__(self, api_key: str):
        self.api_key = api_key

    @abstractmethod
    def process_request(self, *args, **kwargs):
        """
        Abstract method to process a request.
        Must be implemented by subclasses.
        """
        pass
