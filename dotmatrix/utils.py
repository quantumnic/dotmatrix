"""Image and pixel helpers for dotmatrix."""

from __future__ import annotations


from PIL import Image


def resize_image(img: Image.Image, size: int) -> Image.Image:
    """Resize an image to fit the display, maintaining aspect ratio with padding.

    The image is resized to fit within size×size and centered on a black background.
    """
    img = img.convert("RGB")
    # Calculate resize keeping aspect ratio
    ratio = min(size / img.width, size / img.height)
    new_w = max(1, int(img.width * ratio))
    new_h = max(1, int(img.height * ratio))
    img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)

    # Center on black background
    canvas = Image.new("RGB", (size, size), (0, 0, 0))
    offset_x = (size - new_w) // 2
    offset_y = (size - new_h) // 2
    canvas.paste(img, (offset_x, offset_y))
    return canvas


def image_to_pixel_data(img: Image.Image) -> bytes:
    """Convert a PIL Image to raw RGB pixel bytes (row-major).

    Returns bytes of length width * height * 3.
    """
    img = img.convert("RGB")
    return img.tobytes()


def pixel_data_to_image(data: bytes, size: int) -> Image.Image:
    """Convert raw RGB pixel bytes back to a PIL Image."""
    return Image.frombytes("RGB", (size, size), data)


def gif_to_frames(gif_path: str, size: int) -> list[bytes]:
    """Extract frames from a GIF and resize each to the display size.

    Returns a list of raw RGB pixel byte arrays, one per frame.
    """
    img = Image.open(gif_path)
    frames: list[bytes] = []
    try:
        while True:
            frame = img.copy().convert("RGB")
            frame = resize_image(frame, size)
            frames.append(image_to_pixel_data(frame))
            img.seek(img.tell() + 1)
    except EOFError:
        pass
    return frames


def create_solid_frame(size: int, r: int, g: int, b: int) -> bytes:
    """Create a solid color frame as raw RGB bytes."""
    return bytes([r, g, b] * (size * size))


def blend_frames(frame_a: bytes, frame_b: bytes, alpha: float) -> bytes:
    """Blend two frames together. alpha=0 → frame_a, alpha=1 → frame_b."""
    alpha = max(0.0, min(1.0, alpha))
    result = bytearray(len(frame_a))
    for i in range(len(frame_a)):
        result[i] = int(frame_a[i] * (1 - alpha) + frame_b[i] * alpha)
    return bytes(result)
