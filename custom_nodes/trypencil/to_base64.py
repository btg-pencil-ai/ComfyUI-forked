import base64
from io import BytesIO

from .utils import tensor2pil

class ImageBatchToBase64:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE",),
            },
        }

    RETURN_TYPES = ()
    FUNCTION = "to_base64_batch"
    CATEGORY = "trypencil"
    OUTPUT_NODE = True

    def to_base64_batch(self, images):
        outputs = []
        for image in images:  # Iter through batch of images
            pil_image = tensor2pil(image)

            buffered = BytesIO()
            pil_image.save(buffered, format="JPEG")
            image_bytes = buffered.getvalue()

            base64_str = base64.b64encode(image_bytes).decode("utf-8")
            outputs.append(base64_str)

        return {"ui": {"images": outputs}}


NODE_CLASS_MAPPINGS = {"ImageBatchToBase64": ImageBatchToBase64}
NODE_DISPLAY_NAME_MAPPINGS = {"ImageBatchToBase64": "Images batch to base64"}
