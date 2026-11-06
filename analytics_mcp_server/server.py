"""Expose the first two Analytics API endpoints as FastMCP tools."""

import os
from datetime import date
from typing import Any
from urllib.parse import quote

import requests
from fastmcp import FastMCP
from fastmcp.exceptions import ToolError

mcp = FastMCP("Analytics Server")

# Hardcoding these for now, replace with environment variables in production.
DEFAULT_API_BASE_URL = "https://api.gsa.gov/analytics/dap/v2"
DEFAULT_API_KEY = "DEMO_KEY"

# Helper function to validate and encode path segments for API requests.
def _path_segment(value: str, name: str) -> str:
    if not value.strip() or value in {".", ".."}:
        raise ToolError(f"{name} must be a non-empty name, not '.' or '..'.")
    return quote(value, safe="")

# Helper function to validate and construct query parameters for API requests.
def _query_params(
    limit: int, page: int, after: str | None, before: str | None
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

# Helper function to make GET requests to the Analytics API and return report data.
def _get_reports(path: str, params: dict[str, int | str]) -> list[dict[str, Any]]:
    api_key = DEFAULT_API_KEY
    # api_key = os.environ.get("ANALYTICS_API_KEY")
    # if not api_key or not api_key.strip():
    #     raise ToolError("Set ANALYTICS_API_KEY before requesting reports.")

    base_url = DEFAULT_API_BASE_URL
    # base_url = os.environ.get("ANALYTICS_API_BASE_URL", DEFAULT_API_BASE_URL).rstrip("/")
    # if not base_url:
    #     raise ToolError("ANALYTICS_API_BASE_URL must not be empty.")
    try:
        response = requests.get(
            f"{base_url}{path}",
            params=params,
            headers={"X-API-KEY": api_key, "Accept": "application/json"},
            timeout=10,
        )
        response.raise_for_status()
    except requests.HTTPError as exc:
        status = exc.response.status_code if exc.response is not None else "unknown"
        raise ToolError(f"Analytics API returned HTTP {status}.") from exc
    except requests.RequestException as exc:
        raise ToolError("Could not reach the Analytics API; check the URL and connection.") from exc
    try:
        data = response.json()
    except ValueError as exc:
        raise ToolError("Analytics API returned invalid JSON.") from exc
    if not isinstance(data, list) or any(not isinstance(item, dict) for item in data):
        raise ToolError("Analytics API must return a JSON array of report objects.")
    return data


@mcp.tool
def get_analytic_reports(
    report_name: str,
    limit: int = 1000,
    page: int = 1,
    after: str | None = None,
    before: str | None = None,
) -> list[dict[str, Any]]:
    """Get analytic reports across government agencies.

    Args:
        report_name: Name of the report to retrieve.
        limit: Number of data points per page, from 1 to 10000. Defaults to 1000.
        page: Result page, starting at 1.
        after: Include dates on or after this YYYY-MM-DD date.
        before: Include dates on or before this YYYY-MM-DD date.
    """
    report = _path_segment(report_name, "report_name")
    params = _query_params(limit, page, after, before)
    return _get_reports(f"/reports/{report}/data", params)


@mcp.tool
def get_agency_analytic_reports(
    agency_name: str,
    report_name: str,
    limit: int = 1000,
    page: int = 1,
    after: str | None = None,
    before: str | None = None,
) -> list[dict[str, Any]]:
    """Get analytic reports filtered by a government agency.

    Args:
        agency_name: Name of the agency to filter by.
        report_name: Name of the report to retrieve.
        limit: Number of data points per page, from 1 to 10000. Defaults to 1000.
        page: Result page, starting at 1.
        after: Include dates on or after this YYYY-MM-DD date.
        before: Include dates on or before this YYYY-MM-DD date.
    """
    agency = _path_segment(agency_name, "agency_name")
    report = _path_segment(report_name, "report_name")
    params = _query_params(limit, page, after, before)
    return _get_reports(f"/agencies/{agency}/reports/{report}/data", params)


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


if __name__ == "__main__":
    mcp.run()
