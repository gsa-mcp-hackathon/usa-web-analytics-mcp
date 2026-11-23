"""Expose the first two Analytics API endpoints as FastMCP tools."""

from __future__ import annotations

from typing import Annotated, Any

from fastmcp import FastMCP
# import requests
from datetime import date
from typing import Any
import re
from urllib.parse import quote

from fastmcp.exceptions import ToolError

from analytics_server.models import PaginationParams, ResponseFormat
from analytics_server.resources import parameters_values
from analytics_server.utils import API_BASE_URL, API_KEY, UpstreamServiceError, fetch_json, paginate


# Helper function to validate and encode path segments for API requests.
def _path_segment(value: str, name: str) -> str:
    if not value.strip() or value in {".", ".."}:
        raise ToolError(f"{name} must be a non-empty name, not '.' or '..'.")
    return quote(value, safe="")


def _is_us_gov_web_domain(value: str) -> bool:
    """Return whether value is a syntactically valid DNS web domain."""

    if len(value) > 253 or not value.lower().startswith("www.") or not value.lower().endswith(".gov"):
        return False
    label = r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?"
    return re.fullmatch(rf"{label}(?:\.{label})+", value) is not None

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
    """Register the get_domain_analytic_reports tool with the MCP server."""

    @mcp.tool(
            name="get_domain_analytic_reports",
            annotations={
                "title": "Get Analytic Reports for a US Government Web Domain",
                "readOnlyHint": True,
                "destructiveHint": False,
                "idempotentHint": True,
                "openWorldHint": True,
            },
    )
    async def get_domain_analytic_reports(
        domain: str,
        report: str,
        limit: int = 1000,
        page: int = 1,
        after: str | None = None,
        before: str | None = None,
    ) -> list[dict[str, Any]]:
        """Get analytic reports filtered by a government web domain.

        Args:
            domain: Name of the domain to filter by. Must be a valid US agency domain (required).
            report: Name of the report to retrieve (required).
            limit: Number of data points per page, from 1 to 10000. Defaults to 1000.
            page: Result page, starting at 1.
            after: Include dates on or after this YYYY-MM-DD date.
            before: Include dates on or before this YYYY-MM-DD date.
        """
        # Strip leading and trailing whitespace
        domain = domain.strip()
        # hhtp:// or https:// should not be included in the domain name so strip them if present
        domain = re.sub(r"^https?://", "", domain, flags=re.IGNORECASE)
        
        if not _is_us_gov_web_domain(domain):
            raise ToolError(
                f"Invalid domain '{domain}'. "
                "Please provide a valid US agency domain name."
            )
        domain = _path_segment(domain, "domain")


        report_path = _path_segment(report, "report")
        report = parameters_values.validate_report(report_path)
        if not report:
            raise ToolError(
                f"Invalid report '{report_path}'. "
                "Please provide a valid report name."
            )
    
        params = _query_params(limit, page, after, before)
        try:
            payload = await fetch_json(
                f"domains/{domain}/reports/{report}/data",
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

