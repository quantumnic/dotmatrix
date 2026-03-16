"""Show the built-in clock on an iDotMatrix display."""

import asyncio
from dotmatrix import DotMatrixClient


async def main():
    async with DotMatrixClient(device_name="IDM 6CDEE8") as client:
        await client.show_clock(fmt="24h")
        print("✓ Clock displayed!")


if __name__ == "__main__":
    asyncio.run(main())
