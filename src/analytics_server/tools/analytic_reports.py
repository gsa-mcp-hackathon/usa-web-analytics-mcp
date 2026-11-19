"""Expose the first two Analytics API endpoints as FastMCP tools."""

from __future__ import annotations

from typing import Annotated, Any

from fastmcp import FastMCP
# import requests
from datetime import date
from typing import Any
from urllib.parse import quote

from fastmcp.exceptions import ToolError

from analytics_server.models import PaginationParams, ResponseFormat
from analytics_server.utils import API_BASE_URL, API_KEY, UpstreamServiceError, fetch_json, paginate


# Helper function to validate and encode path segments for API requests.
def _path_segment(value: str, name: str) -> str:
    if not value.strip() or value in {".", ".."}:
        raise ToolError(f"{name} must be a non-empty name, not '.' or '..'.")
    return quote(value, safe="")

# Helper function to validate and construct query parameters for API requests.
def _query_params(
    limit: int, 
    page: int, 
    after: str | None, 
    before: str | None
) -> dict[str, int | str]:
    if not 1 <= limit <= 10_000:
        raise ToolError("limit must be between 1 and 10000.")
    if page < 1:
        raise ToolError("page must be at least 1.")
    params: dict[str, int | str] = {"limit": limit, "page": page}
    for name, value in (("after", after), ("before", before)):
        if value is None:
            continue
        try:
            parsed = date.fromisoformat(value)
        except ValueError as exc:
            raise ToolError(f"{name} must be a valid date in YYYY-MM-DD format.") from exc
        if parsed.isoformat() != value:
            raise ToolError(f"{name} must be a valid date in YYYY-MM-DD format.")
        params[name] = value
    if after is not None and before is not None and after > before:
        raise ToolError("after must be on or before before.")
    return params


def register(mcp: FastMCP) -> None:
    """Register the example tool with the MCP server."""
    @mcp.tool(
            name = "get_analytic_reports",
        annotations={
                "title": "Search Datasets (example)",
                "readOnlyHint": True,
                "destructiveHint": False,
                "idempotentHint": True,
                "openWorldHint": True,
            },
    )
    async def get_analytic_reports(
        report_name: str,
        limit: int = 1000,
        page: int = 1,
        after: str | None = None,
        before: str | None = None,
    ) -> list[dict[str, Any]]:
        """Get analytic reports across all government agencies.

        Args:
            report_name: Name of the report to retrieve.
            limit: Number of data points per page, from 1 to 10000. Defaults to 1000.
            page: Result page, starting at 1.
            after: Include dates on or after this YYYY-MM-DD date.
            before: Include dates on or before this YYYY-MM-DD date.
        """
        report = _path_segment(report_name, "report_name")
        params = _query_params(limit, page, after, before)
        try:
            payload = await fetch_json(
                f"reports/{report}/data",
                params=params,
                headers={"x-api-key": API_KEY},
            )
        # except httpx.HTTPStatusError as exc:
        except UpstreamServiceError as exc:
            raise ToolError(str(exc)) from exc
        
        # API returns either a list directly or a dict with "results" key
        if isinstance(payload, list):
            return payload
        return payload.get("results", [])


        # page = paginate(results, pagination.limit, pagination.offset)

        # if response_format is ResponseFormat.MARKDOWN:
        #     lines = [f"# Datasets matching '{query}'", ""]
        #     lines += [f"- **{r['title']}** (`{r['id']}`)" for r in page["items"]]
        #     lines.append("")
        #     lines.append(
        #         f"_Showing {page['count']} of {page['total']}._"
        #         + (f" Next offset: {page['next_offset']}." if page["has_more"] else "")
        #     )
        #     return "\n".join(lines)


