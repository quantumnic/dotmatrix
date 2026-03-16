"""Send 'Hello World!' to an iDotMatrix display."""

import asyncio
from dotmatrix import DotMatrixClient


async def main():
    async with DotMatrixClient(device_name="IDM 6CDEE8") as client:
        await client.send_text("Hello World!", color="cyan", speed=60)
        print("✓ Text sent!")


if __name__ == "__main__":
    asyncio.run(main())
