import functools

import numpy as np
from PIL import Image
import torch


def pil2tensor(image: Image) -> torch.Tensor:
    return torch.from_numpy(np.array(image).astype(np.float32) / 255.0).unsqueeze(0)


def tensor2pil(t_image: torch.Tensor) -> Image:
    return Image.fromarray(np.clip(255.0 * t_image.cpu().numpy().squeeze(), 0, 255).astype(np.uint8))


# Create a wrapper function that can apply a function to multiple images in a batch
# while passing all other arguments to the function
def apply_to_batch(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        batch = None
        batch_arg_index = None
        batch_kwarg_key = None

        for i, arg in enumerate(args):
            if isinstance(arg, (list, torch.Tensor)):
                batch = arg
                batch_arg_index = i
                args = args[:i] + args[i+1:]
                break
        else:
            for key, value in kwargs.items():
                if isinstance(value, (list, torch.Tensor)):
                    batch = value
                    batch_kwarg_key = key
                    kwargs.pop(key)
                    break

        if batch is not None:
            results = []
            for item in batch:
                if batch_arg_index is not None:
                    mod_args = args[:batch_arg_index] + (item,) + args[batch_arg_index:]
                    results.append(func(*mod_args, **kwargs))
                else:
                    mod_kwargs = kwargs.copy()
                    mod_kwargs[batch_kwarg_key] = item
                    results.append(func(*args, **mod_kwargs))

            batch_tensor = torch.cat(results, dim=0)

        else:
            batch_tensor =  func(*args, **kwargs)

        return (batch_tensor,)

    return wrapper
