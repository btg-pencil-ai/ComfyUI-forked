import math

import numpy as np
import pilgram
from PIL import Image, ImageOps, ImageFilter

from .utils import apply_to_batch, pil2tensor, tensor2pil


def image_to_rgb(image):
    return pil2tensor(tensor2pil(image).convert('RGB'))


def invert_image(image):
    s = 1.0 - image
    return s


def mask_to_image(mask):
    return mask.reshape((-1, 1, mask.shape[-2], mask.shape[-1])).movedim(1, -1).expand(-1, -1, -1, 3)


def image_gaussian_blur(image, radius=5):
    img = tensor2pil(image)
    img = img.filter(ImageFilter.GaussianBlur(radius=radius))
    return pil2tensor(img)


def image_add_blending(image_a, image_b, blend_percentage=1.0):
    img_a = tensor2pil(image_a)
    img_b = tensor2pil(image_b)

    # Apply "add" blending
    out_image = pilgram.css.blending.normal(img_a, img_b)
    out_image = out_image.convert("RGB")

    # Blend image
    blend_mask = Image.new(mode="L", size=img_a.size, color=round(blend_percentage * 255))
    blend_mask = ImageOps.invert(blend_mask)
    out_image = Image.composite(img_a, out_image, blend_mask)

    return pil2tensor(out_image)


def image_blend_by_mask(image_a, image_b, mask, blend_percentage=1.0):
    img_a = tensor2pil(image_a)
    img_b = tensor2pil(image_b)
    mask = ImageOps.invert(tensor2pil(mask).convert('L'))
    masked_img = Image.composite(img_a, img_b, mask.resize(img_a.size))

    # Blend image
    blend_mask = Image.new(mode="L", size=img_a.size, color=round(blend_percentage * 255))
    blend_mask = ImageOps.invert(blend_mask)
    img_result = Image.composite(img_a, masked_img, blend_mask)

    del img_a, img_b, blend_mask, mask

    return pil2tensor(img_result)


def adjust_image_levels(image, black_level, mid_level, white_level):
    image = tensor2pil(image)

    im_arr = np.array(image).astype(np.float32)
    im_arr[im_arr < black_level] = black_level
    im_arr = (im_arr - black_level) * \
        (255 / (white_level - black_level))
    im_arr = np.clip(im_arr, 0, 255)

    # Mid-level adjustment
    gamma = math.log(0.5) / math.log((mid_level - black_level) / (white_level - black_level))
    im_arr = np.power(im_arr / 255, gamma) * 255

    im_arr = im_arr.astype(np.uint8)

    return pil2tensor(Image.fromarray(im_arr))


class DetailRestoration:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "destination": ("IMAGE",),
                "source": ("IMAGE",),
                "mask": ("MASK",),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "detail_restoration"
    CATEGORY = "trypencil"

    @apply_to_batch
    def detail_restoration(
        self,
        destination,
        source,
        mask,
        # expose more parameters if needed
    ):
        def extract_details(image, blur_radius=5, blend_percentage=0.5):
            image = image_to_rgb(image)
            inverted_image = invert_image(image)
            blurred_image = image_gaussian_blur(image, blur_radius)
            inverted_details = image_add_blending(inverted_image, blurred_image, blend_percentage)
            return invert_image(inverted_details)

        blurred_destination = image_gaussian_blur(destination)

        source_details = extract_details(source)
        destination_details = extract_details(destination)
        combined_details = image_blend_by_mask(destination_details, source_details, mask_to_image(mask))

        blended_image = image_add_blending(blurred_destination, combined_details, blend_percentage=0.65)

        return adjust_image_levels(
            blended_image,
            black_level=80,
            mid_level=130,
            white_level=180
        )


NODE_CLASS_MAPPINGS = {"DetailRestoration": DetailRestoration}
NODE_DISPLAY_NAME_MAPPINGS = {"DetailRestoration": "Detail Restoration"}
