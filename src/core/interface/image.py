from core.interface.base import AIServiceBase


class ImageServiceBase(AIServiceBase):
    """
    Base class for image-based AI services.
    """

    def process_request(self, image_data, **kwargs):
        """
        Process an image-based request using OpenAI API.
        """
        pass
