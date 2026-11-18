"""Parameters resource — 
   use this file to define parameter values that can be used by the MCP tools.

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
    """Register the paramter resource(s) with the MCP server."""

    @mcp.resource("parameters://agencies")
    def agencies() -> str:
        """Return a list of U.S. federal agencies.
        
        This is a static list of U.S. federal agencies that can be used as parameter values
        for MCP tools.

        """
        agencies_list = [
            "agency-international-development",
            "american-battle-monuments-commission",
            "commodity-futures-trading-commission",
            "consumer-financial-protection-bureau",
            "consumer-product-safety-commission",
            "corporation-national-community-service",
            "defense-nuclear-facilities-safety-board",
            "denali-commission",
            "agriculture",
            "commerce",
            "defense",
            "education",
            "energy",
            "health-human-services",
            "homeland-security",
            "housing-urban-development",
            "interior",
            "justice",
            "labor",
            "state",
            "transportation",
            "treasury",
            "veterans-affairs",
            "environmental-protection-agency",
            "equal-employment-opportunity-commission",
            "executive-office-president",
            "farm-credit-administration",
            "federal-bureau-investigation",
            "federal-deposit-insurance-corporation",
            "federal-election-commission",
            "federal-energy-regulatory-commission",
            "federal-housing-finance-agency",
            "federal-maritime-commission",
            "federal-mine-safety-health-review-commission",
            "federal-retirement-thrift-investment-board",
            "federal-trade-commission",
            "general-services-administration",
            "inter-american-foundation",
            "international-development-finance-corporation",
            "merit-systems-protection-board",
            "millennium-challenge-corporation",
            "national-aeronautics-space-administration",
            "national-archives-records-administration",
            "national-capital-planning-commission",
            "national-council-disability",
            "national-credit-union-administration",
            "national-education-association",
            "national-endowment-humanities",
            "national-labor-relations-board",
            "national-mediation-board",
            "national-oceanic-atmospheric-administration",
            "national-park-service",
            "national-reconnaissance-office",
            "national-science-foundation",
            "national-transportation-safety-board",
            "nuclear-regulatory-commission",
            "nuclear-waste-technical-review-board",
            "office-director-national-intelligence",
            "office-government-ethics",
            "office-navajo-hopi-indian-relocation",
            "office-personnel-management",
            "peace-corps",
            "pension-benefit-guaranty-corporation",
            "postal-regulatory-commission",
            "privacy-civil-liberties-oversight-board",
            "public-buildings-reform-board",
            "securities-exchange-commission",
            "small-business-administration",
            "social-security-administration",
            "special-inspector-general-afghanistan-restoration",
            "surface-transportation-board",
            "tennessee-valley-authority",
            "udall-foundation",
            "access-board",
            "agency-global-media",
            "commission-civil-rights",
            "us-courts",
            "international-trade-commission",
            "postal-inspection-service",
            "postal-service",
            "railroad-retirement-board",
            "trade-development-agency",

        ]
        return json.dumps(agencies_list, indent=2)
