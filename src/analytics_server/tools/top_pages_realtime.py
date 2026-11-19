"""Example tool — replace this with a real tool for your service.

This is the canonical one-tool-per-file pattern:
  - the module exposes a single `register(mcp)` function,
  - inside it, one `@mcp.tool`-decorated function is defined,
  - the decorated function is async (so I/O doesn't block the server),
  - annotations describe the tool's behavior to the client.

Tool design tips for federal datasets:
  - Return dicts/lists with consistent keys; let the LLM narrate the data.
  - State the data's update frequency and "as-of" date in the docstring.
  - Expose pagination (see `PaginationParams` / `paginate`) for list results.
  - Give errors an *actionable* message ("try filter=X"), not a raw stack trace.
"""

from __future__ import annotations

from typing import Any

import httpx
from fastmcp import FastMCP
from fastmcp.exceptions import ToolError

from analytics_server.resources import parameters_values


def register(mcp: FastMCP) -> None:
    """Register the example tool with the MCP server."""

    @mcp.tool("get_top_pages_realtime",
        annotations={
            "title": "Search Datasets (example)",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": True,
        },
    )
    async def get_top_pages_realtime(agency: str) -> list[dict[str, Any]]:
        """Fetch the last 30 minutes of top pages for the specified agency.

        Args:
            agency: Agency name in lower case with hyphens, or its acronym.
        """
        original_agency = agency
        agency = parameters_values.validate_agency(agency)
        if not agency:
            raise ToolError(
                f"Invalid agency '{original_agency}'. "
                "Please provide a valid agency name or acronym."
            )

        # Not needed for fetching the CSV directly from the public URL.
        # headers = {"x-api-key": API_KEY}
        # params = {}  # Add any query parameters if needed

        csv_url = f"https://analytics.usa.gov/data/{agency}/top-pages-realtime.csv"
        # example https://analytics.usa.gov/data/national-library-medicine/top-pages-realtime.csv
    
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(csv_url)
                if response.status_code != 200:
                    raise ToolError(
                        f"Analytics API returned HTTP {response.status_code}."
                    )

                text_data = response.text
                if not text_data.strip():
                    return []

                import csv
                from io import StringIO

                csv_reader = csv.DictReader(StringIO(text_data))
                data = list(csv_reader)

                return data

        except httpx.HTTPError as exc:
            raise ToolError(
                "Could not retrieve real-time analytics data."
            ) from exc
