"""Play a rainbow animation on an iDotMatrix display."""

import asyncio
from dotmatrix import DotMatrixClient
from dotmatrix.animations import rainbow


async def main():
    async with DotMatrixClient(device_name="IDM 6CDEE8") as client:
        frames = list(rainbow(size=client.size, frames=60))
        await client._client.set_gif(frames, client.size)
        print("✓ Rainbow animation playing!")


if __name__ == "__main__":
    asyncio.run(main())
