from abc import abstractmethod
from core.interface.base import AIServiceBase


class VideoServiceBase(AIServiceBase):
    """
    Base class for video-based AI services.
    """

    @abstractmethod
    def process_request(self, video_data, **kwargs):
        """
        Abstract method to process video data.
        Must be implemented by subclasses.
        """
        pass
