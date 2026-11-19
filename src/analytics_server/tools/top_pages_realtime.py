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

from collections.abc import Mapping
from importlib import import_module
from typing import Annotated, Any

import httpx
from fastmcp import FastMCP

from analytics_server.models import PaginationParams, ResponseFormat
from analytics_server.utils import API_BASE_URL, API_KEY, fetch_json, paginate
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
    async def get_top_pages_realtime(agency: str) -> str:
        """Fetches the last 30 minutes of top pages for the specified agency from the real-time analytics data.
        
        Parameters:
        - agency: The name of the agency in lower case with hyphens (e.g. 'national-library-medicine') 
        or its uppercase acronym (e.g. 'NLM','HHS', 'USDA', 'GSA')
        """
        try:
            # Validate the agency by calling the validate_agency function from parameters_values
            parameters = import_module("analytics_server.resources.parameters_values")
            agency = parameters.validate_agency(agency)
            if not agency:
                return f"Invalid agency '{agency}'. Please provide a valid agency name or acronym."
        except ImportError:
            return "Agency options could not be loaded from analytics_server.resources.parameters_values."

        # Not needed for fetching the CSV directly from the public URL.
        # headers = {"X-API-KEY": API_KEY}
        # params = {}  # Add any query parameters if needed

        csv_url = f"https://analytics.usa.gov/data/{agency}/top-pages-realtime.csv"
        # example https://analytics.usa.gov/data/national-library-medicine/top-pages-realtime.csv
    
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(csv_url)
                if response.status_code != 200:
                    return f"API Error {response.status_code}: {response.text}"
                # The response is expected to be CSV, so we need to parse it accordingly
                # For now, let's just read it as text and split by lines
                text_data = response.text
                lines = text_data.splitlines()
                if not lines:
                    return "No records found in the CSV response."

                # Convert the CSV lines into a list of dictionaries
                import csv
                from io import StringIO

                csv_reader = csv.DictReader(StringIO(text_data))
                data = list(csv_reader)

                if not data:
                    return "No records found for the given criteria."

                return data

        except Exception as e:
            return f"An unexpected exception occurred: {str(e)}"

    # Keep httpx + fetch_json imported so the commented example above is
    # copy-paste ready (remove these once you wire in the real API call).
    _ = (httpx, fetch_json)
