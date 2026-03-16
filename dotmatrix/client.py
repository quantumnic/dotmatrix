"""High-level client wrapping the idotmatrix library."""

from __future__ import annotations

from typing import Any

from bleak import BleakScanner
from PIL import Image

from dotmatrix.utils import resize_image, image_to_pixel_data, gif_to_frames

# Screen size constants
SCREEN_SIZES = {16: "16x16", 32: "32x32", 64: "64x64"}

# Color name → RGB mapping
COLOR_MAP = {
    "red": (255, 0, 0),
    "green": (0, 255, 0),
    "blue": (0, 0, 255),
    "white": (255, 255, 255),
    "yellow": (255, 255, 0),
    "cyan": (0, 255, 255),
    "magenta": (255, 0, 255),
    "orange": (255, 165, 0),
    "purple": (128, 0, 128),
}


def parse_color(color: str | tuple[int, int, int]) -> tuple[int, int, int]:
    """Parse a color name or RGB tuple."""
    if isinstance(color, tuple):
        return color
    if isinstance(color, str):
        lower = color.lower().strip()
        if lower in COLOR_MAP:
            return COLOR_MAP[lower]
        # Try hex
        if lower.startswith("#") and len(lower) == 7:
            return (int(lower[1:3], 16), int(lower[3:5], 16), int(lower[5:7], 16))
    raise ValueError(f"Unknown color: {color}")


class DotMatrixClient:
    """High-level client for iDotMatrix LED displays.

    Args:
        device_name: Bluetooth device name (e.g. "IDM 6CDEE8").
        address: Bluetooth MAC address. If given, takes priority over device_name.
        size: Pixel size of the display (16, 32, or 64).
    """

    def __init__(
        self,
        device_name: str | None = None,
        address: str | None = None,
        size: int = 32,
    ):
        self.device_name = device_name
        self.address = address
        self.size = size
        self._client: Any = None
        self._connected = False

    @property
    def is_connected(self) -> bool:
        return self._connected

    # ------------------------------------------------------------------
    # Scanning
    # ------------------------------------------------------------------

    async def scan(self, timeout: float = 5.0) -> list[dict[str, str]]:
        """Scan for iDotMatrix devices.

        Returns a list of dicts with keys: name, address, rssi.
        """
        devices: list[dict[str, str]] = []
        discovered = await BleakScanner.discover(timeout=timeout)
        for d in discovered:
            name = d.name or ""
            if name.upper().startswith("IDM"):
                devices.append(
                    {"name": name, "address": d.address, "rssi": str(d.rssi)}
                )
        return devices

    # ------------------------------------------------------------------
    # Connection
    # ------------------------------------------------------------------

    async def connect(self) -> None:
        """Connect to the iDotMatrix device."""
        from idotmatrix import ConnectionManager

        address = self.address
        if not address and self.device_name:
            # Scan to resolve name → address
            found = await self.scan()
            for d in found:
                if d["name"] == self.device_name:
                    address = d["address"]
                    break
            if not address:
                raise ConnectionError(
                    f"Device '{self.device_name}' not found. Run `dotmatrix scan` first."
                )

        self._client = ConnectionManager(address)
        await self._client.connect()
        self._connected = True

    async def disconnect(self) -> None:
        """Disconnect from the device."""
        if self._client:
            await self._client.disconnect()
        self._connected = False

    # ------------------------------------------------------------------
    # Commands
    # ------------------------------------------------------------------

    async def send_text(
        self,
        text: str,
        color: str | tuple[int, int, int] = (255, 255, 255),
        speed: int = 50,
        mode: str = "scroll",
    ) -> None:
        """Send scrolling or static text to the display.

        Args:
            text: The string to display.
            color: Color name or (R, G, B) tuple.
            speed: Scroll speed 0-100.
            mode: 'scroll' or 'static'.
        """
        self._ensure_connected()
        rgb = parse_color(color)
        await self._client.set_text(
            text=text,
            color_r=rgb[0],
            color_g=rgb[1],
            color_b=rgb[2],
            speed=speed,
            mode=0 if mode == "scroll" else 1,
        )

    async def send_image(self, image_path: str) -> None:
        """Send a static image to the display.

        The image is resized to fit the display.
        """
        self._ensure_connected()
        img = Image.open(image_path)
        img = resize_image(img, self.size)
        pixel_data = image_to_pixel_data(img)
        await self._client.set_image(pixel_data, self.size)

    async def send_gif(self, gif_path: str, speed: int = 50) -> None:
        """Send a GIF animation to the display.

        Args:
            gif_path: Path to GIF file.
            speed: Playback speed 0-100.
        """
        self._ensure_connected()
        frames = gif_to_frames(gif_path, self.size)
        await self._client.set_gif(frames, self.size, speed=speed)

    async def set_brightness(self, value: int) -> None:
        """Set display brightness (0-100)."""
        self._ensure_connected()
        value = max(0, min(100, value))
        await self._client.set_brightness(value)

    async def show_clock(self, fmt: str = "24h") -> None:
        """Show the built-in clock.

        Args:
            fmt: '24h' or '12h'.
        """
        self._ensure_connected()
        use_24h = fmt.lower() in ("24h", "24")
        await self._client.set_clock(style=0, visible=True, hour24=use_24h)

    async def set_color(self, r: int, g: int, b: int) -> None:
        """Fill the entire display with a solid color."""
        self._ensure_connected()
        await self._client.set_color(r, g, b)

    async def set_mode(self, mode: str) -> None:
        """Set display mode: clock, text, image, gif."""
        self._ensure_connected()
        mode_map = {"clock": 0, "text": 1, "image": 2, "gif": 3}
        mode_id = mode_map.get(mode.lower())
        if mode_id is None:
            raise ValueError(f"Unknown mode: {mode}. Choose from: {list(mode_map.keys())}")
        await self._client.set_screen_mode(mode_id)

    async def set_score(self, left: int, right: int) -> None:
        """Show a scoreboard with left/right values."""
        self._ensure_connected()
        await self._client.set_scoreboard(left, right)

    async def off(self) -> None:
        """Turn off the display (set brightness to 0 and clear)."""
        self._ensure_connected()
        await self._client.set_brightness(0)

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _ensure_connected(self) -> None:
        if not self._connected:
            raise ConnectionError("Not connected. Call connect() first.")

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, *exc):
        await self.disconnect()
