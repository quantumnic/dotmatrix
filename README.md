# 🎨 dotmatrix

Control your iDotMatrix LED display via Bluetooth from Python or CLI.

Supports 16×16, 32×32, and 64×64 pixel displays with the "IDM XXXXXX" Bluetooth name.

## Install

```bash
pip install git+https://github.com/quantumnic/dotmatrix
```

## Quick Start

```bash
# Scan for your display
dotmatrix scan

# Show scrolling text
dotmatrix text "Hello World!" --device "IDM 6CDEE8"

# Show clock
dotmatrix clock --device "IDM 6CDEE8"

# Rainbow animation
dotmatrix animate rainbow --device "IDM 6CDEE8"
```

## CLI Commands

```bash
# Scan for devices
dotmatrix scan

# Show text (scrolling or static)
dotmatrix text "Hello!" -d "IDM 6CDEE8" --color red --speed 50

# Show the built-in clock
dotmatrix clock -d "IDM 6CDEE8" --format 24h

# Display a static image
dotmatrix image photo.png -d "IDM 6CDEE8"

# Play a GIF animation
dotmatrix gif animation.gif -d "IDM 6CDEE8"

# Built-in animations
dotmatrix animate rainbow -d "IDM 6CDEE8"
dotmatrix animate fire -d "IDM 6CDEE8"
dotmatrix animate matrix -d "IDM 6CDEE8"
dotmatrix animate pulse -d "IDM 6CDEE8"

# Set brightness (0-100)
dotmatrix brightness 80 -d "IDM 6CDEE8"

# Show scoreboard
dotmatrix score 3 2 -d "IDM 6CDEE8"

# Set display mode
dotmatrix mode clock -d "IDM 6CDEE8"

# Turn off
dotmatrix off -d "IDM 6CDEE8"
```

## Python API

```python
import asyncio
from dotmatrix import DotMatrixClient

async def main():
    async with DotMatrixClient(device_name="IDM 6CDEE8") as client:
        await client.send_text("Hello!", color="cyan")
        await client.set_brightness(80)
        await client.show_clock()

asyncio.run(main())
```

## Built-in Animations

| Name | Description |
|------|-------------|
| `rainbow` | Cycling diagonal rainbow |
| `fire` | Heat propagation fire effect |
| `matrix` | Green falling characters |
| `pulse` | Pulsing single color |
| `checkerboard` | Alternating colored squares |

## License

MIT
