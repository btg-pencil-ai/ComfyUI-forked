import math

import cv2
import numpy as np
from PIL import Image

from .utils import apply_to_batch, pil2tensor, tensor2pil


def apply_mask(matrix, mask, fill_value):
    masked = np.ma.array(matrix, mask=mask, fill_value=fill_value)
    return masked.filled()


def apply_threshold(matrix, low_value, high_value):
    low_mask = matrix < low_value
    matrix = apply_mask(matrix, low_mask, low_value)
    high_mask = matrix > high_value
    matrix = apply_mask(matrix, high_mask, high_value)
    return matrix


class ColorCorrection:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE", {"default": None}),
                "intensity": ("FLOAT", {"default": 0.05, "min": 0.0, "max": 1.0, "step": 0.01}),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "color_correction"
    CATEGORY = "trypencil"

    @apply_to_batch
    def color_correction(self, image, intensity=0.05):
        image = tensor2pil(image)
        image_array = np.array(image)
        half_percent = intensity / 2.0
        channels = cv2.split(image_array)
        out_channels = []

        for channel in channels:
            # find the low and high percentile values (based on the input percentile)
            height, width = channel.shape
            vector_size = width * height

            flat_channel = channel.reshape(vector_size)
            flat_channel = np.sort(flat_channel)

            columns_number = flat_channel.shape[0]
            low_values = flat_channel[math.floor(columns_number * half_percent)]
            high_values = flat_channel[math.ceil(columns_number * (1.0 - half_percent))]

            # saturate below the low percentile and above the high percentile
            threshold_channel = apply_threshold(channel, low_values, high_values)

            # scale the channel
            normalized_channel = cv2.normalize(threshold_channel, threshold_channel.copy(), 0, 255, cv2.NORM_MINMAX)
            out_channels.append(normalized_channel)

        corrected_image = Image.fromarray(cv2.merge(out_channels))

        return pil2tensor(corrected_image)


NODE_CLASS_MAPPINGS = {"ColorCorrection": ColorCorrection}
NODE_DISPLAY_NAME_MAPPINGS = {"ColorCorrection": "Automatic color correction"}
