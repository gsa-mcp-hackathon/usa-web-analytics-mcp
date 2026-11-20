"""Example resource — replace or supplement with your own.

Resource URI conventions:
  - Use a consistent scheme per service, e.g. "census://", "example://".
  - Static resources (no parameters):  @mcp.resource("scheme://path")
  - Parameterized resources:           @mcp.resource("scheme://path/{param}")
"""

from __future__ import annotations

from fastmcp import FastMCP


def register(mcp: FastMCP) -> None:
    """Register the US website analytics resource(s) with the MCP server."""

    @mcp.resource("about://info/server")
    def server_info() -> str:
        """This is a United States government web analytics MCP server.

        It provides access to web analytics data for government websites.
        It was developed as part of the GSA MCP hackathon.
        """
        return (
            "NLMs GSA Hackathon MCP Server\n\n"
            "This is a the National Library of Medicine's entry for the GSA 2026 MCP server hackathon.\n"
        )

    @mcp.resource("about://docs/{topic}")
    def docs(topic: str) -> str:
        """Todo: replace this with actual documentation lookup. Parameterized resource."""
        pages = {
            "getting-started": "Clone, `uv sync`, then `uv run python main.py`.",
            "deploy": "See deploy/ for IBM and Databricks deployment kits.",
        }
        return pages.get(topic, f"No documentation found for topic '{topic}'.")

    @mcp.resource("analytics://about")
    def about() -> str:
        """Explain the Analytics API tools and their data source."""
        return (
            "Analytics Server retrieves US government web analytics reports across allagencies "
            "or filtered by agency and or web domain. Data comes from the GSA Digital Analytics Program. "
            "The program does not track individuals and anonymizes visitor IP addresses. "
            "Tools return JSON arrays and support pagination and inclusive YYYY-MM-DD "
            "date filters. Set ANALYTICS_API_KEY for x-api-key authentication"
            "and optionally set ANALYTICS_API_BASE_URL to override the GSA API URL."
        )
