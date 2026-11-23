"""End-to-end check of the analytics MCP server over stdio.

Launches the server exactly as `uv run analytics-server` does, then exercises
the protocol surface (tools, resources, prompts), happy paths, and error cases.

Run from the repo root:
    uv run python tests/e2e_stdio_check.py
    uv run python tests/e2e_stdio_check.py --offline   # skip tests that need internet/API

Exit code is non-zero if any check fails. A JSON report is written to
tests/e2e_report.json.
"""

from __future__ import annotations

import asyncio
import json
import sys
import time
from pathlib import Path

from fastmcp import Client
from fastmcp.client.transports import StdioTransport
from fastmcp.exceptions import ToolError

ROOT = Path(__file__).resolve().parent.parent
OFFLINE = "--offline" in sys.argv
results: list[dict] = []


def record(name: str, ok: bool, detail: str = "") -> None:
    results.append({"name": name, "ok": ok, "detail": detail})
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" -- {detail}" if detail else ""))


async def expect_error(client: Client, name: str, tool: str, args: dict, needle: str = ""):
    """The call must fail with a ToolError (not crash the server)."""
    try:
        await client.call_tool(tool, args)
        record(name, False, "expected ToolError, call succeeded")
    except ToolError as exc:
        ok = needle.lower() in str(exc).lower()
        record(name, ok, str(exc)[:150])
    except Exception as exc:  # noqa: BLE001
        record(name, False, f"{type(exc).__name__}: {str(exc)[:150]}")


async def expect_ok(client: Client, name: str, tool: str, args: dict):
    try:
        res = await client.call_tool(tool, args)
        data = res.data if res.data is not None else res.content
        size = len(data) if hasattr(data, "__len__") else "n/a"
        record(name, True, f"returned {size} items")
    except Exception as exc:  # noqa: BLE001
        record(name, False, f"{type(exc).__name__}: {str(exc)[:200]}")


async def main() -> int:
    transport = StdioTransport(command="uv", args=["run", "analytics-server"], cwd=str(ROOT))
    t0 = time.time()
    async with Client(transport) as client:
        record("initialize handshake", True, f"{time.time() - t0:.1f}s")
        # await client.ping()
        # record("ping", True)

        # ---- discovery -------------------------------------------------
        tools = await client.list_tools()
        names = {t.name for t in tools}
        expected = {
            "get_analytic_reports",
            "get_agency_analytic_reports",
            "get_domain_analytic_reports",
            "get_top_pages_realtime",
        }
        record("expected tools present", expected <= names, f"missing={expected - names}")
        for t in tools:
            record(f"tool '{t.name}' has description", bool(t.description and t.description.strip()))
            record(f"tool '{t.name}' has object inputSchema", t.inputSchema.get("type") == "object")
            ann = t.annotations
            record(f"tool '{t.name}' readOnlyHint", bool(ann and ann.readOnlyHint))

        resources = await client.list_resources()
        templates = await client.list_resource_templates()
        record("resources listed", len(resources) > 0, ", ".join(str(r.uri) for r in resources))
        for r in resources:
            try:
                content = await client.read_resource(r.uri)
                text = content[0].text if content else ""
                record(f"read resource {r.uri}", bool(text.strip()), f"{len(text)} chars")
            except Exception as exc:  # noqa: BLE001
                record(f"read resource {r.uri}", False, str(exc)[:150])
        record("resource templates listed", True, ", ".join(t.uriTemplate for t in templates))

        prompts = await client.list_prompts()
        record("prompts listed", len(prompts) > 0, ", ".join(p.name for p in prompts))

        # ---- input validation (no network needed) ----------------------
        await expect_error(client, "invalid report name", "get_analytic_reports", {"report": "nope"}, "invalid report")
        await expect_error(client, "empty report name", "get_analytic_reports", {"report": "  "}, "non-empty")
        await expect_error(client, "path traversal report", "get_analytic_reports", {"report": ".."}, "non-empty")
        await expect_error(client, "report with slash", "get_analytic_reports", {"report": "../x"}, "invalid report")
        await expect_error(client, "limit too large", "get_analytic_reports", {"report": "browser", "limit": 10001}, "limit")
        await expect_error(client, "limit zero", "get_analytic_reports", {"report": "browser", "limit": 0}, "limit")
        await expect_error(client, "page zero", "get_analytic_reports", {"report": "browser", "page": 0}, "page")
        await expect_error(client, "bad date format", "get_analytic_reports", {"report": "browser", "after": "01/02/2024"}, "YYYY-MM-DD")
        await expect_error(client, "impossible date", "get_analytic_reports", {"report": "browser", "after": "2024-02-30"}, "YYYY-MM-DD")
        await expect_error(client, "after > before", "get_analytic_reports", {"report": "browser", "after": "2024-05-01", "before": "2024-01-01"}, "on or before")
        await expect_error(client, "missing required arg", "get_analytic_reports", {})
        await expect_error(client, "wrong type for limit", "get_analytic_reports", {"report": "browser", "limit": "abc"})
        await expect_error(client, "unknown tool", "does_not_exist", {})
        await expect_error(client, "invalid agency (agency report)", "get_agency_analytic_reports", {"agency": "not-an-agency", "report": "browser"}, "invalid")
        await expect_error(client, "invalid report (agency report)", "get_agency_analytic_reports", {"agency": "nasa", "report": "nope"}, "invalid")
        await expect_error(client, "invalid agency (realtime)", "get_top_pages_realtime", {"agency": "not-an-agency"}, "invalid agency")
        await expect_error(client, "agency path traversal (realtime)", "get_top_pages_realtime", {"agency": "../../etc"}, "invalid agency")
        await expect_error(client, "invalid domain", "get_domain_analytic_reports", {"domain": "", "report": "browser"})

        # ---- live calls (need internet + API key) ----------------------
        if OFFLINE:
            print("(offline: skipping live API calls)")
        else:
            await expect_ok(client, "live: all-agency browser report", "get_analytic_reports", {"report": "browser", "limit": 5})
            await expect_ok(client, "live: pagination page 2", "get_analytic_reports", {"report": "browser", "limit": 5, "page": 2})
            await expect_ok(client, "live: date filter", "get_analytic_reports", {"report": "browser", "limit": 5, "after": "2024-01-01", "before": "2024-01-31"})
            await expect_ok(client, "live: agency report (acronym)", "get_agency_analytic_reports", {"agency": "NASA", "report": "device", "limit": 5})
            await expect_ok(client, "live: realtime top pages", "get_top_pages_realtime", {"agency": "health-human-services"})
            await expect_ok(client, "live: realtime via acronym", "get_top_pages_realtime", {"agency": "NASA"})

    passed = sum(r["ok"] for r in results)
    print(f"\n{passed}/{len(results)} checks passed")
    (ROOT / "tests" / "e2e_report.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
