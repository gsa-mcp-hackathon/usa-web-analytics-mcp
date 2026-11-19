"""Example prompt — replace or supplement with your own.

A prompt function returns a string (rendered as a user message) or a list of
messages for a multi-turn starter. Its parameters become input fields in the
client UI. Keep prompts dataset-agnostic where possible so they compose well.
"""

from __future__ import annotations

from fastmcp import FastMCP


def register(mcp: FastMCP) -> None:
    @mcp.prompt
    def analyze_report(
        report_name: str, after: str, before: str, agency_name: str | None = None
    ) -> str:
        """Ask the assistant to retrieve and summarize an analytics report."""
        scope = f"agency {agency_name}" if agency_name else "all agencies"
        return (
            f"Retrieve the {report_name} analytics report for {scope}, from {after} "
            f"through {before}, using the matching analytics tool. Follow pagination "
            "until an empty page is returned, or clearly state any retrieval limit. "
            "Summarize the available metrics and trends without inventing missing data."
        )
