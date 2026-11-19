"""Example resource — replace or supplement with your own.

Resource URI conventions:
  - Use a consistent scheme per service, e.g. "census://", "example://".
  - Static resources (no parameters):  @mcp.resource("scheme://path")
  - Parameterized resources:           @mcp.resource("scheme://path/{param}")
"""

from __future__ import annotations

from fastmcp import FastMCP


def register(mcp: FastMCP) -> None:
    """Register the example resource(s) with the MCP server."""

    @mcp.resource("about://info/server")
    def server_info() -> str:
        """Basic information about this MCP server.

        Replace with a better description of our project.
        """
        return (
            "NLMs GSA Hackathon MCP Server\n\n"
            "This is a the National Library of Medicine's server for the GSA MCP hackathon.\n"
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
            "Analytics Server retrieves government web analytics reports across agencies "
            "or filtered by agency. Data comes from the GSA Digital Analytics Program. "
            "The program does not track individuals and anonymizes visitor IP addresses. "
            "Tools return JSON arrays and support pagination and inclusive YYYY-MM-DD "
            "date filters. Set ANALYTICS_API_KEY for X-API-KEY authentication and optionally "
            "ANALYTICS_API_BASE_URL to override the GSA API URL."
        )
