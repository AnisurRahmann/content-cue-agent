"""
Ideogram API Tool for AI Image Generation

Generates marketing images using Ideogram API with placeholder fallback.
"""

import os
from typing import Optional
from dotenv import load_dotenv
import httpx

load_dotenv()


# =============================================================================
# CONFIGURATION
# =============================================================================

IDEOGRAM_API_KEY = os.getenv("IDEOGRAM_API_KEY")
IDEOGRAM_API_URL = "https://api.ideogram.ai/v1/images/generation"


def is_ideogram_available() -> bool:
    """Check if Ideogram API key is configured."""
    return bool(IDEOGRAM_API_KEY)


# =============================================================================
# IMAGE GENERATION
# =============================================================================

async def generate_image_ideogram(
    prompt: str,
    aspect_ratio: str = "1:1",
    model: str = "V_2_TURBO",
    prompt_weight: Optional[float] = None,
) -> Optional[dict]:
    """
    Generate an image using Ideogram API.

    Args:
        prompt: Detailed text prompt for image generation
        aspect_ratio: Image aspect ratio (e.g., "1:1", "16:9", "9:16")
        model: Ideogram model to use (V_2_TURBO is fastest)
        prompt_weight: Optional prompt strength (0-1, higher = more literal)

    Returns:
        Dict with image_url or None if generation failed
        {
            "image_url": "https://...",
            "image_seed": 12345,
            "is_safe": true
        }
    """
    if not is_ideogram_available():
        return None

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                IDEOGRAM_API_URL,
                headers={
                    "Authorization": f"Bearer {IDEOGRAM_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "image_request": {
                        "prompt": prompt,
                        "aspect_ratio": aspect_ratio,
                        "model": model,
                        "magic_prompt_option": "AUTO" if not prompt_weight else "OFF",
                    }
                },
            )

            if response.status_code == 200:
                data = response.json()
                if data.get("data") and len(data["data"]) > 0:
                    return data["data"][0]

            return None

    except Exception as e:
        print(f"⚠️ Ideogram API error: {e}")
        return None


def generate_image_placeholder(
    prompt: str,
    output_path: str,
    aspect_ratio: str = "1:1",
) -> str:
    """
    Generate a placeholder text description instead of a real image.
    Used when IDEOGRAM_API_KEY is not configured.

    Args:
        prompt: The image prompt that was intended
        output_path: Where to save the placeholder text file
        aspect_ratio: Requested aspect ratio

    Returns:
        Path to the placeholder file
    """
    from pathlib import Path

    # Create output directory if needed
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    # Write placeholder description
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"# IMAGE PLACEHOLDER\n\n")
        f.write(f"This is a placeholder for an AI-generated image.\n\n")
        f.write(f"## Prompt:\n{prompt}\n\n")
        f.write(f"## Aspect Ratio:\n{aspect_ratio}\n\n")
        f.write(f"## Note:\n")
        f.write(f"To generate real images, set IDEOGRAM_API_KEY in .env\n")

    return output_path


# =============================================================================
# DOWNLOAD IMAGE FROM URL
# =============================================================================

async def download_image(url: str, output_path: str) -> str:
    """
    Download an image from URL to local file.

    Args:
        url: Image URL
        output_path: Local file path to save image

    Returns:
        Local file path
    """
    from pathlib import Path

    # Create output directory if needed
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(url)
        response.raise_for_status()

        with open(output_path, "wb") as f:
            f.write(response.content)

    return output_path


# =============================================================================
# MAIN GENERATION FUNCTION (WITH FALLBACK)
# =============================================================================

async def generate_image(
    prompt: str,
    output_path: str,
    aspect_ratio: str = "1:1",
) -> tuple[str, bool]:
    """
    Generate an image with automatic fallback to placeholder.

    Args:
        prompt: Image generation prompt
        output_path: Where to save the image
        aspect_ratio: Image aspect ratio

    Returns:
        Tuple of (file_path, is_real_image)
        - file_path: Path to generated file (image or placeholder)
        - is_real_image: True if real image, False if placeholder
    """
    if is_ideogram_available():
        # Try real image generation
        result = await generate_image_ideogram(prompt, aspect_ratio=aspect_ratio)

        if result and "image_url" in result:
            # Download image to local file
            image_path = await download_image(result["image_url"], output_path)
            return image_path, True

    # Fallback to placeholder
    placeholder_path = output_path.replace(".png", "_placeholder.txt")
    return generate_image_placeholder(prompt, placeholder_path, aspect_ratio), False


if __name__ == "__main__":
    import asyncio

    async def test():
        print("Testing Ideogram Tool...\n")

        # Test availability
        print(f"1. Ideogram Available: {is_ideogram_available()}")

        # Test generation (will use placeholder if no API key)
        prompt = "Modern tech product showcase with blue gradient background, ChatGPT Plus logo, price ৳2,500/month"
        output_path = "test_output.png"

        print(f"\n2. Generating image...")
        print(f"   Prompt: {prompt[:100]}...")

        path, is_real = await generate_image(prompt, output_path)

        print(f"\n   Result:")
        print(f"   - Path: {path}")
        print(f"   - Real Image: {is_real}")

    asyncio.run(test())
