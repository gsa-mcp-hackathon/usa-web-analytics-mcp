# USA Web Analytics MCP

An MCP server developed by the National Library of Medicine (NLM) for the GSA 2026 MCP Server Hackathon. It provides read-only access to United States government website analytics through tools backed by the GSA Digital Analytics Program (DAP).

The server uses [FastMCP](https://github.com/jlowin/fastmcp) and [uv](https://docs.astral.sh/uv/). It can run locally over stdio or remotely over streamable HTTP.

## Features

- Retrieve analytics reports across all participating US government agencies.
- Filter analytics reports by agency or US government web domain.
- Retrieve the most recent 30 minutes of top pages for a selected agency.
- Use inclusive `YYYY-MM-DD` date filters and paginated report requests.
- Read agency, report, and parameter information through MCP resources.
- Start report analysis through a reusable MCP prompt.

## Available tools

| Tool | Description |
|---|---|
| `get_analytic_reports` | Retrieve an analytics report across all agencies. |
| `get_agency_analytic_reports` | Retrieve a report filtered by agency. |
| `get_domain_analytic_reports` | Retrieve a report filtered by a US government web domain. |
| `get_top_pages_realtime` | Retrieve the latest 30 minutes of top pages for an agency. |

All tools are read-only and return structured data.

## Prerequisites

- Python 3.11 or newer
- [uv](https://docs.astral.sh/uv/)

## Install and run locally

```bash
cp .env.example .env
uv sync
uv run analytics-server
```

The default transport is stdio, so the server communicates through standard input and output as a local MCP client subprocess.

To run the HTTP transport locally:

```powershell
$env:MCP_TRANSPORT = "streamable-http"
uv run analytics-server
```

The HTTP server listens on `0.0.0.0:8000` by default. Its MCP endpoint is `/mcp`, and it provides `/health` and `/version` status routes.

Example client configuration:

```json
{
  "mcpServers": {
    "analytics-mcp": {
      "command": "uv",
      "args": ["run", "analytics-server"],
      "cwd": "/absolute/path/to/mcp-hackathon-template"
    }
  }
}
```

## Configuration

Configuration is loaded from environment variables or a local `.env` file.

| Variable | Default | Purpose |
|---|---|---|
| `MCP_TRANSPORT` | `stdio` | Use `stdio` locally or `streamable-http` remotely. |
| `MCP_HOST` | `0.0.0.0` | HTTP bind address. |
| `MCP_PORT` | `8000` | HTTP port. |
| `ANALYTICS_API_KEY` | `DEMO_KEY` | API key sent to the GSA Analytics API. |
| `ANALYTICS_API_BASE_URL` | GSA DAP API v2 URL | Override the upstream API origin. |

Do not commit `.env` or API credentials. Use an environment secret store for deployed instances.

## Project structure

```text
src/analytics_server/
├── app.py           # FastMCP setup and transport selection
├── config.py        # Environment-based settings
├── models.py        # Pydantic inputs and shared types
├── utils.py         # Outbound HTTP, validation, and pagination
├── routes.py        # /health and /version routes
├── tools/           # One MCP tool per module
├── prompts/         # Reusable report-analysis prompt
└── resources/       # Analytics and parameter resources
tests/               # Import, registration, and security tests
deploy/              # Platform deployment examples
eval/                # Evaluation guidance
```

## Verification

```bash
uv sync --group dev
uv run pytest tests/ -v
uv run ruff check .
```

The test suite includes MCP registration checks and outbound HTTP security coverage, including validation of relative paths and sanitization of upstream failures.

## Security

The MCP endpoint is unauthenticated by default. This is appropriate for the public-data hackathon posture but is not sufficient for a production deployment. Databricks Apps and other platforms may add authentication at the platform layer, but per-tool authorization and agency-specific ATO controls should be reviewed before production use.

The outbound HTTP helper:

- Uses an operator-controlled GSA API origin.
- Rejects absolute URLs, traversal paths, queries, fragments, and encoded escapes.
- Disables redirects and environment proxy inheritance.
- Applies a 30-second timeout and a five-megabyte response limit.
- Sanitizes upstream errors so response bodies and sensitive values are not returned or logged.

Treat tool arguments, upstream content, and MCP messages as untrusted. Keep credentials out of source control and structured logs. See [SECURITY.md](SECURITY.md) for vulnerability reporting and additional guidance.

## Deployment status

Deployment examples are included for cloud.gov, IBM watsonx Orchestrate/Code Engine, and Databricks Apps:

- [cloud.gov deployment manifest](manifest.yaml)
- [IBM deployment kits](deploy/ibm/)
- [Databricks deployment kit](deploy/databricks/)

**IBM and Databricks deployments have not been tested for this project.** Use the supplied kits as deployment templates and validate authentication, networking, secrets, health checks, and tool behavior in your target environment before use.

## Evaluation

This repository does not yet include a complete evaluation harness. See [eval/README.md](eval/README.md) for the evaluation approach and setup guidance.

## License

[MIT](LICENSE). The project is subject to the GSA vulnerability disclosure policy described in [SECURITY.md](SECURITY.md).
