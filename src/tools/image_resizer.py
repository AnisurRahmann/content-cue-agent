"""
Image Resizer Tool - Resize images to platform specifications using Pillow.

Platform specifications from brand guidelines:
- Facebook post: 1200x630
- Instagram square: 1080x1080
- Instagram carousel: 1080x1350
- LinkedIn: 1200x627
- Ad creative: 1080x1080
- WhatsApp status: 1080x1920
"""

from pathlib import Path
from typing import Literal
from PIL import Image


# =============================================================================
# PLATFORM SPECIFICATIONS
# =============================================================================

PlatformSpec = Literal[
    "facebook_post",
    "instagram_square",
    "instagram_carousel",
    "linkedin_post",
    "ad_creative",
    "whatsapp_status",
]

PLATFORM_SIZES = {
    "facebook_post": (1200, 630),
    "instagram_square": (1080, 1080),
    "instagram_carousel": (1080, 1350),
    "linkedin_post": (1200, 627),
    "ad_creative": (1080, 1080),
    "whatsapp_status": (1080, 1920),
}


# =============================================================================
# RESIZE FUNCTION
# =============================================================================

def resize_image(
    input_path: str,
    output_path: str,
    platform: PlatformSpec,
    quality: int = 95,
) -> str:
    """
    Resize an image to platform specifications.

    Args:
        input_path: Path to input image
        output_path: Path to save resized image
        platform: Platform specification key
        quality: JPEG quality (1-100, default: 95)

    Returns:
        Path to resized image

    Raises:
        FileNotFoundError: If input image doesn't exist
        ValueError: If platform spec is unknown
    """
    if platform not in PLATFORM_SIZES:
        raise ValueError(f"Unknown platform spec: {platform}")

    target_width, target_height = PLATFORM_SIZES[platform]

    # Open image
    img = Image.open(input_path)

    # Convert RGBA to RGB if necessary (for JPEG output)
    if img.mode == "RGBA":
        # Create white background
        background = Image.new("RGB", img.size, (255, 255, 255))
        background.paste(img, mask=img.split()[3])  # Use alpha channel as mask
        img = background
    elif img.mode not in ("RGB", "L"):
        img = img.convert("RGB")

    # Resize using high-quality resampling
    img_resized = img.resize((target_width, target_height), Image.Resampling.LANCZOS)

    # Create output directory if needed
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    # Save based on file extension
    output_format = "JPEG" if output_path.lower().endswith((".jpg", ".jpeg")) else "PNG"

    if output_format == "JPEG":
        img_resized.save(output_path, format="JPEG", quality=quality, optimize=True)
    else:
        img_resized.save(output_path, format="PNG", optimize=True)

    return output_path


def resize_image_to_size(
    input_path: str,
    output_path: str,
    width: int,
    height: int,
    quality: int = 95,
) -> str:
    """
    Resize an image to custom dimensions.

    Args:
        input_path: Path to input image
        output_path: Path to save resized image
        width: Target width in pixels
        height: Target height in pixels
        quality: JPEG quality (1-100, default: 95)

    Returns:
        Path to resized image
    """
    # Open image
    img = Image.open(input_path)

    # Convert RGBA to RGB if necessary
    if img.mode == "RGBA":
        background = Image.new("RGB", img.size, (255, 255, 255))
        background.paste(img, mask=img.split()[3])
        img = background
    elif img.mode not in ("RGB", "L"):
        img = img.convert("RGB")

    # Resize
    img_resized = img.resize((width, height), Image.Resampling.LANCZOS)

    # Create output directory if needed
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    # Save
    img_resized.save(output_path, format="JPEG", quality=quality, optimize=True)

    return output_path


# =============================================================================
# BATCH RESIZE
# =============================================================================

def resize_for_platforms(
    input_path: str,
    output_dir: str,
    platforms: list[PlatformSpec],
) -> dict[str, str]:
    """
    Resize an image for multiple platforms.

    Args:
        input_path: Path to input image
        output_dir: Directory to save resized images
        platforms: List of platform specs to generate

    Returns:
        Dict mapping platform names to output paths
    """
    results = {}

    input_filename = Path(input_path).stem
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    for platform in platforms:
        output_filename = f"{input_filename}_{platform}.jpg"
        output_path = str(Path(output_dir) / output_filename)

        try:
            resized_path = resize_image(input_path, output_path, platform)
            results[platform] = resized_path
        except Exception as e:
            print(f"⚠️ Failed to resize for {platform}: {e}")
            results[platform] = None

    return results


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def get_image_dimensions(image_path: str) -> tuple[int, int]:
    """Get image dimensions (width, height)."""
    with Image.open(image_path) as img:
        return img.size


def get_aspect_ratio(width: int, height: int) -> str:
    """Calculate aspect ratio as string (e.g., '1:1', '16:9')."""
    from math import gcd

    divisor = gcd(width, height)
    return f"{width // divisor}:{height // divisor}"


if __name__ == "__main__":
    # Test resizing
    print("Image Resizer Tool\n")

    # Example usage (would need actual image)
    print("Platform Sizes:")
    for platform, (w, h) in PLATFORM_SIZES.items():
        print(f"  {platform}: {w}x{h}")

    print("\nTo resize an image:")
    print("  resize_image('input.jpg', 'output.jpg', 'facebook_post')")
