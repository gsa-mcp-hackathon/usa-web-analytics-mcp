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

from typing import Annotated, Any

import httpx
from fastmcp import FastMCP

from analytics_server.models import PaginationParams, ResponseFormat
from analytics_server.utils import API_BASE_URL, API_KEY, fetch_json, paginate


def register(mcp: FastMCP) -> None:
    """Register the example tool with the MCP server."""

    @mcp.tool(
        name="example_search_datasets",
        annotations={
            "title": "Search Datasets (example)",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": True,
        },
    )
    async def get_dap_analytics(
        report: Annotated[str, "Report name (e.g., 'domain', 'download', 'second-level-domain', 'top-pages-realtime')"], 
        agency: Annotated[str | None, "Optional uppercase acronym (e.g. 'HHS', 'USDA', 'GSA')"], 
        domain: Annotated[str | None, "Optional specific subdomain or domain to filter by (e.g., 'nlm.nih.gov')"]
        ) -> str:
        """Fetches historical or real-time analytics data from the GSA Digital Analytics Program (DAP) API v2.
        
        Parameters:
        - report: One of 'domain', 'download', 'second-level-domain', or 'top-pages-realtime'
        - agency: Optional uppercase acronym (e.g. 'HHS', 'USDA', 'GSA')
        - domain: Optional specific subdomain or domain to filter by (e.g., 'nlm.nih.gov')
        
        Returns:
        - A string representation of the fetched analytics data (up to 15 records)
        - An error message if the API call fails or no data is found
        """

        clean_domain = domain.strip().lower() if domain else ""

        if clean_domain and report != 'top-pages-realtime':
            endpoint = f"{API_BASE_URL}/domain/{clean_domain}/reports/{report}/data"
        else:
            endpoint = f"{API_BASE_URL}/reports/{report}/data"

        params = {}
        if agency and agency.lower() != 'all' and not clean_domain:
            if report not in ['top-pages-realtime', 'second-level-domain']:
                params['agency'] = agency

        headers = {"X-API-KEY": API_KEY}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(endpoint, headers=headers, params=params)
            if response.status_code != 200:
                return f"API Error {response.status_code}: {response.text}"

            data = response.json()
            if not data:
                return "No records found for the given criteria."

            if clean_domain and report == 'top-pages-realtime':
                filtered_data = []
                for row in data:
                    domain_val = str(row.get('domain', '')).lower()
                    page_val = str(row.get('page', '')).lower()
                    if clean_domain in domain_val or clean_domain in page_val:
                        filtered_data.append(row)
                data = filtered_data

            if not data:
                return f"No matching records found for domain '{clean_domain}' in the realtime dataset."

            return str(data[:15])

        except Exception as e:
            return f"An unexpected exception occurred: {str(e)}"

    # Keep httpx + fetch_json imported so the commented example above is
    # copy-paste ready (remove these once you wire in the real API call).
    _ = (httpx, fetch_json)
