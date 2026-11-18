"""Data resource — use this file to define static or semi-static data resources.

Resource URI conventions:
  - Use a consistent scheme per service, e.g. "census://", "example://".
  - Static resources (no parameters):  @mcp.resource("scheme://path")
  - Parameterized resources:           @mcp.resource("scheme://path/{param}")
"""

from __future__ import annotations

import json
from urllib.request import urlopen

from fastmcp import FastMCP


def register(mcp: FastMCP) -> None:
    """Register the data resource(s) with the MCP server."""

    @mcp.resource("data://top_downloads")
    def top_downloads() -> str:
        """Return the latest seven-day top downloads from analytics.usa.gov.
        
        I'm fetching the latest seven-day top downloads from analytics.usa.gov.
        It might more efficient to cache this data locally instead of fetching it on every 
        request. This would reduce latency and the load on the external service. 

        """
        url = "https://analytics.usa.gov/data/live/top-downloads-7-days.json"
        with urlopen(url, timeout=10) as response:
            data = json.load(response)
        return json.dumps(data, indent=2)
