"""图床提供者模块"""

from .stardots_provider import StarDotsProvider
from .cloudflare_r2_provider import CloudflareR2Provider
from .provider_template import ImageHostProvider

__all__ = [
    "StarDotsProvider",
    "CloudflareR2Provider", 
    "ImageHostProvider"
]