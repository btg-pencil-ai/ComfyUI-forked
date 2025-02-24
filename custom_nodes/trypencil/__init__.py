from .color_correction import NODE_CLASS_MAPPINGS as CC_NCM
from .color_correction import NODE_DISPLAY_NAME_MAPPINGS as CC_NDNM
from .detail_restoration import NODE_CLASS_MAPPINGS as DR_NCM
from .detail_restoration import NODE_DISPLAY_NAME_MAPPINGS as DR_NDNM
from .hdr import NODE_CLASS_MAPPINGS as HDR_NCM
from .hdr import NODE_DISPLAY_NAME_MAPPINGS as HDR_NDNM
from .to_base64 import NODE_CLASS_MAPPINGS as B64_NCM
from .to_base64 import NODE_DISPLAY_NAME_MAPPINGS as B64_NDNM

NODE_CLASS_MAPPINGS = {**CC_NCM, **DR_NCM, **HDR_NCM, **B64_NCM}
NODE_DISPLAY_NAME_MAPPINGS = {**CC_NDNM, **DR_NDNM, **HDR_NDNM, **B64_NDNM}
__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
