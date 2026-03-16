"""Tests for DotMatrixClient — all Bluetooth calls are mocked."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from dotmatrix.client import DotMatrixClient, parse_color, COLOR_MAP


# ---------------------------------------------------------------------------
# parse_color
# ---------------------------------------------------------------------------

class TestParseColor:
    def test_tuple_passthrough(self):
        assert parse_color((10, 20, 30)) == (10, 20, 30)

    def test_named_colors(self):
        for name, rgb in COLOR_MAP.items():
            assert parse_color(name) == rgb

    def test_named_color_case_insensitive(self):
        assert parse_color("RED") == (255, 0, 0)
        assert parse_color("  Green  ") == (0, 255, 0)

    def test_hex_color(self):
        assert parse_color("#ff8800") == (255, 136, 0)

    def test_unknown_raises(self):
        with pytest.raises(ValueError, match="Unknown color"):
            parse_color("fuchsia-sparkle")


# ---------------------------------------------------------------------------
# DotMatrixClient — unit tests with mocked BLE
# ---------------------------------------------------------------------------

def _make_client(**kwargs) -> DotMatrixClient:
    """Create a DotMatrixClient pre-wired with a mock _client."""
    c = DotMatrixClient(**kwargs)
    c._client = AsyncMock()
    c._connected = True
    return c


class TestClientProperties:
    def test_defaults(self):
        c = DotMatrixClient()
        assert c.size == 32
        assert c.device_name is None
        assert c.address is None
        assert not c.is_connected

    def test_custom_init(self):
        c = DotMatrixClient(device_name="IDM TEST", address="AA:BB:CC", size=64)
        assert c.device_name == "IDM TEST"
        assert c.address == "AA:BB:CC"
        assert c.size == 64


class TestClientCommands:
    @pytest.fixture()
    def client(self):
        return _make_client(device_name="IDM MOCK")

    @pytest.mark.asyncio
    async def test_send_text_default(self, client):
        await client.send_text("hi")
        client._client.set_text.assert_awaited_once()
        kw = client._client.set_text.call_args
        assert kw.kwargs["text"] == "hi"
        assert kw.kwargs["color_r"] == 255  # white

    @pytest.mark.asyncio
    async def test_send_text_named_color(self, client):
        await client.send_text("yo", color="red")
        kw = client._client.set_text.call_args
        assert kw.kwargs["color_r"] == 255
        assert kw.kwargs["color_g"] == 0

    @pytest.mark.asyncio
    async def test_set_brightness_clamps(self, client):
        await client.set_brightness(150)  # clamped to 100
        client._client.set_brightness.assert_awaited_once_with(100)

    @pytest.mark.asyncio
    async def test_set_brightness_zero(self, client):
        await client.set_brightness(0)
        client._client.set_brightness.assert_awaited_once_with(0)

    @pytest.mark.asyncio
    async def test_show_clock_24h(self, client):
        await client.show_clock("24h")
        client._client.set_clock.assert_awaited_once_with(style=0, visible=True, hour24=True)

    @pytest.mark.asyncio
    async def test_show_clock_12h(self, client):
        await client.show_clock("12h")
        client._client.set_clock.assert_awaited_once_with(style=0, visible=True, hour24=False)

    @pytest.mark.asyncio
    async def test_set_color(self, client):
        await client.set_color(128, 64, 32)
        client._client.set_color.assert_awaited_once_with(128, 64, 32)

    @pytest.mark.asyncio
    async def test_off(self, client):
        await client.off()
        client._client.set_brightness.assert_awaited_once_with(0)

    @pytest.mark.asyncio
    async def test_set_mode_valid(self, client):
        await client.set_mode("clock")
        client._client.set_screen_mode.assert_awaited_once_with(0)

    @pytest.mark.asyncio
    async def test_set_mode_invalid(self, client):
        with pytest.raises(ValueError, match="Unknown mode"):
            await client.set_mode("disco")

    @pytest.mark.asyncio
    async def test_set_score(self, client):
        await client.set_score(3, 2)
        client._client.set_scoreboard.assert_awaited_once_with(3, 2)

    @pytest.mark.asyncio
    async def test_not_connected_raises(self):
        c = DotMatrixClient()
        with pytest.raises(ConnectionError, match="Not connected"):
            await c.send_text("oops")


class TestClientScan:
    @pytest.mark.asyncio
    async def test_scan_filters_idm(self):
        mock_dev_1 = MagicMock()
        mock_dev_1.name = "IDM ABC123"
        mock_dev_1.address = "AA:BB:CC:DD:EE:FF"
        mock_dev_1.rssi = -50

        mock_dev_2 = MagicMock()
        mock_dev_2.name = "SomeOther"
        mock_dev_2.address = "11:22:33:44:55:66"
        mock_dev_2.rssi = -70

        with patch("dotmatrix.client.BleakScanner.discover", new_callable=AsyncMock) as mock_disc:
            mock_disc.return_value = [mock_dev_1, mock_dev_2]
            c = DotMatrixClient()
            found = await c.scan()

        assert len(found) == 1
        assert found[0]["name"] == "IDM ABC123"
