"""Click CLI for dotmatrix."""

from __future__ import annotations

import asyncio

import click
from rich.console import Console
from rich.table import Table

from dotmatrix.client import DotMatrixClient
from dotmatrix.animations import ANIMATIONS

console = Console()


def run_async(coro):
    """Run an async coroutine from sync CLI."""
    return asyncio.run(coro)


@click.group()
@click.version_option(package_name="dotmatrix")
def cli():
    """🎨 dotmatrix — Control iDotMatrix LED displays via Bluetooth."""
    pass


@cli.command()
@click.option("--timeout", default=5, help="Scan timeout in seconds.")
def scan(timeout: int):
    """Scan for iDotMatrix devices."""

    async def _scan():
        client = DotMatrixClient()
        devices = await client.scan(timeout=timeout)
        if not devices:
            console.print("[yellow]No iDotMatrix devices found.[/yellow]")
            return

        table = Table(title="🔍 iDotMatrix Devices")
        table.add_column("Name", style="cyan")
        table.add_column("Address", style="green")
        table.add_column("RSSI", style="yellow")
        for d in devices:
            table.add_row(d["name"], d["address"], d["rssi"])
        console.print(table)

    run_async(_scan())


@cli.command()
@click.argument("message")
@click.option("--device", "-d", required=True, help="Device name (e.g. 'IDM 6CDEE8').")
@click.option("--color", "-c", default="white", help="Text color (name or #hex).")
@click.option("--speed", "-s", default=50, type=int, help="Scroll speed 0-100.")
@click.option("--mode", "-m", default="scroll", type=click.Choice(["scroll", "static"]))
def text(message: str, device: str, color: str, speed: int, mode: str):
    """Show text on the display."""

    async def _text():
        async with DotMatrixClient(device_name=device) as client:
            await client.send_text(message, color=color, speed=speed, mode=mode)
            console.print(f"[green]✓[/green] Sent text: {message!r}")

    run_async(_text())


@cli.command()
@click.option("--device", "-d", required=True, help="Device name.")
@click.option("--format", "fmt", default="24h", type=click.Choice(["24h", "12h"]))
def clock(device: str, fmt: str):
    """Show the built-in clock."""

    async def _clock():
        async with DotMatrixClient(device_name=device) as client:
            await client.show_clock(fmt=fmt)
            console.print(f"[green]✓[/green] Clock set to {fmt}")

    run_async(_clock())


@cli.command()
@click.argument("path", type=click.Path(exists=True))
@click.option("--device", "-d", required=True, help="Device name.")
def image(path: str, device: str):
    """Show a static image on the display."""

    async def _image():
        async with DotMatrixClient(device_name=device) as client:
            await client.send_image(path)
            console.print(f"[green]✓[/green] Image sent: {path}")

    run_async(_image())


@cli.command()
@click.argument("path", type=click.Path(exists=True))
@click.option("--device", "-d", required=True, help="Device name.")
@click.option("--speed", "-s", default=50, type=int, help="Playback speed 0-100.")
def gif(path: str, device: str, speed: int):
    """Show a GIF animation on the display."""

    async def _gif():
        async with DotMatrixClient(device_name=device) as client:
            await client.send_gif(path, speed=speed)
            console.print(f"[green]✓[/green] GIF sent: {path}")

    run_async(_gif())


@cli.command()
@click.argument("name", type=click.Choice(list(ANIMATIONS.keys())))
@click.option("--device", "-d", required=True, help="Device name.")
@click.option("--size", default=32, type=int, help="Display size (16, 32, 64).")
@click.option("--frames", default=60, type=int, help="Number of frames.")
def animate(name: str, device: str, size: int, frames: int):
    """Play a built-in animation."""

    async def _animate():
        async with DotMatrixClient(device_name=device, size=size) as client:
            anim_func = ANIMATIONS[name]
            frame_list = list(anim_func(size=size, frames=frames))
            await client._client.set_gif(frame_list, size)
            console.print(f"[green]✓[/green] Animation '{name}' playing ({len(frame_list)} frames)")

    run_async(_animate())


@cli.command()
@click.argument("value", type=click.IntRange(0, 100))
@click.option("--device", "-d", required=True, help="Device name.")
def brightness(value: int, device: str):
    """Set display brightness (0-100)."""

    async def _brightness():
        async with DotMatrixClient(device_name=device) as client:
            await client.set_brightness(value)
            console.print(f"[green]✓[/green] Brightness set to {value}%")

    run_async(_brightness())


@cli.command()
@click.option("--device", "-d", required=True, help="Device name.")
def off(device: str):
    """Turn off the display."""

    async def _off():
        async with DotMatrixClient(device_name=device) as client:
            await client.off()
            console.print("[green]✓[/green] Display off")

    run_async(_off())


@cli.command()
@click.argument("name", type=click.Choice(["clock", "text", "image", "gif"]))
@click.option("--device", "-d", required=True, help="Device name.")
def mode(name: str, device: str):
    """Set the display mode."""

    async def _mode():
        async with DotMatrixClient(device_name=device) as client:
            await client.set_mode(name)
            console.print(f"[green]✓[/green] Mode set to {name}")

    run_async(_mode())


@cli.command()
@click.argument("left", type=int)
@click.argument("right", type=int)
@click.option("--device", "-d", required=True, help="Device name.")
def score(left: int, right: int, device: str):
    """Show a scoreboard."""

    async def _score():
        async with DotMatrixClient(device_name=device) as client:
            await client.set_score(left, right)
            console.print(f"[green]✓[/green] Score: {left} — {right}")

    run_async(_score())


if __name__ == "__main__":
    cli()
