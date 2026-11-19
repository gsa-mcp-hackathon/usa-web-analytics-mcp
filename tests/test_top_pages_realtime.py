from __future__ import annotations

import pytest
from fastmcp import FastMCP
from fastmcp.exceptions import ToolError

from analytics_server.tools import top_pages_realtime


class FakeResponse:
    def __init__(self, status_code: int, text: str):
        self.status_code = status_code
        self.text = text


class FakeAsyncClient:
    def __init__(self, response: FakeResponse):
        self.response = response

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return None

    async def get(self, url: str) -> FakeResponse:
        return self.response


def create_server() -> FastMCP:
    server = FastMCP("test")
    top_pages_realtime.register(server)
    return server


@pytest.mark.asyncio
async def test_top_pages_tool_returns_structured_list(monkeypatch):
    monkeypatch.setattr(
        top_pages_realtime.parameters_values,
        "validate_agency",
        lambda agency: agency,
    )
    monkeypatch.setattr(
        top_pages_realtime.httpx,
        "AsyncClient",
        lambda: FakeAsyncClient(
            FakeResponse(200, "Active Users,page_title\n12,Example Page\n")
        ),
    )
    server = create_server()

    tool = await server.get_tool("get_top_pages_realtime")
    assert tool is not None
    result_schema = tool.output_schema["properties"]["result"]
    assert result_schema["type"] == "array"
    assert result_schema["items"]["type"] == "object"

    result = await server.call_tool(
        "get_top_pages_realtime",
        {"agency": "commerce"},
    )
    assert result.structured_content == {
        "result": [{"Active Users": "12", "page_title": "Example Page"}]
    }


@pytest.mark.asyncio
async def test_top_pages_tool_returns_empty_list_for_no_records(monkeypatch):
    monkeypatch.setattr(
        top_pages_realtime.parameters_values,
        "validate_agency",
        lambda agency: agency,
    )
    monkeypatch.setattr(
        top_pages_realtime.httpx,
        "AsyncClient",
        lambda: FakeAsyncClient(FakeResponse(200, "")),
    )
    server = create_server()

    result = await server.call_tool(
        "get_top_pages_realtime",
        {"agency": "commerce"},
    )
    assert result.structured_content == {"result": []}
    assert not result.is_error


@pytest.mark.asyncio
async def test_top_pages_tool_reports_failures_as_tool_errors(monkeypatch):
    monkeypatch.setattr(
        top_pages_realtime.parameters_values,
        "validate_agency",
        lambda agency: "" if agency == "invalid" else agency,
    )
    monkeypatch.setattr(
        top_pages_realtime.httpx,
        "AsyncClient",
        lambda: FakeAsyncClient(FakeResponse(503, "")),
    )
    server = create_server()

    with pytest.raises(ToolError, match="Invalid agency"):
        await server.call_tool(
            "get_top_pages_realtime",
            {"agency": "invalid"},
        )

    with pytest.raises(ToolError, match="HTTP 503"):
        await server.call_tool(
            "get_top_pages_realtime",
            {"agency": "commerce"},
        )
