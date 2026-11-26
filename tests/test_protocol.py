import asyncio
import base64
import io
import socket
import subprocess
import sys
import time

from fastmcp import Client
from fastmcp.client.transports import StdioTransport
from mcp.types import ImageContent
from PIL import Image

from forge_mcp.server import mcp


async def check(client):
    async with client:
        tools = await client.list_tools()
        assert {"environment", "diagnostic_image"} <= {tool.name for tool in tools}
        result = await client.call_tool("environment", {})
        assert not result.is_error
        assert result.data["cad_ready"] is False
        image = await client.call_tool("diagnostic_image", {})
        assert not image.is_error
        block = next(item for item in image.content if isinstance(item, ImageContent))
        assert block.mimeType == "image/png"
        with Image.open(io.BytesIO(base64.b64decode(block.data))) as png:
            assert png.format == "PNG"
            assert png.size == (16, 16)
            png.verify()


def test_in_process():
    asyncio.run(check(Client(mcp)))


def test_stdio_subprocess():
    transport = StdioTransport(command=sys.executable, args=["-m", "forge_mcp.server"])
    asyncio.run(check(Client(transport)))


def test_streamable_http_two_clients():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    process = subprocess.Popen(
        [sys.executable, "-m", "forge_mcp.server", "--transport", "http", "--port", str(port)],
    )
    try:
        deadline = time.monotonic() + 30
        while True:
            if process.poll() is not None:
                raise RuntimeError("HTTP MCP server exited early")
            try:
                with socket.create_connection(("127.0.0.1", port), timeout=0.5):
                    break
            except OSError:
                if time.monotonic() >= deadline:
                    raise RuntimeError("HTTP MCP server did not start")
                time.sleep(0.1)
        async def run():
            url = f"http://127.0.0.1:{port}/mcp"
            await asyncio.wait_for(
                asyncio.gather(check(Client(url)), check(Client(url))), timeout=30
            )
        asyncio.run(run())
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)
