"""Parameters resource — 
   use this file to define parameter values that can be used by the MCP tools.

Resource URI conventions:
  - Use a consistent scheme per service, e.g. "census://", "example://".
  - Static resources (no parameters):  @mcp.resource("scheme://path")
  - Parameterized resources:           @mcp.resource("scheme://path/{param}")
"""

from __future__ import annotations

import json
from textwrap import indent
from urllib.request import urlopen

from fastmcp import FastMCP
import json

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

agency_acronyms = {
        "USAID": "agency-international-development",
        "ABMC": "american-battle-monuments-commission",
        "CFTC": "commodity-futures-trading-commission",
        "CFPB": "consumer-financial-protection-bureau",
        "CPSC": "consumer-product-safety-commission",
        "CNCS": "corporation-national-community-service",
        "DNFSB": "defense-nuclear-facilities-safety-board",
        "Denali": "denali-commission",
        "USDA": "agriculture",
        "DOC": "commerce",
        "DOD": "defense",
        "ED": "education",
        "DOE": "energy",
        "HHS": "health-human-services",
        "DHS": "homeland-security",
        "HUD": "housing-urban-development",
        "DOI": "interior",
        "DOJ": "justice",
        "DOL": "labor",
        "DOS": "state",
        "DOT": "transportation",
        "TREAS": "treasury",
        "VA": "veterans-affairs",
        "EPA": "environmental-protection-agency",
        "EEOC": "equal-employment-opportunity-commission",
        "EOP": "executive-office-president",
        "FCA": "farm-credit-administration",
        "FBI": "federal-bureau-investigation",
        "FDIC": "federal-deposit-insurance-corporation",
        "FEC": "federal-election-commission",
        "FERC": "federal-energy-regulatory-commission",
        "FHFA": "federal-housing-finance-agency",
        "FMC": "federal-maritime-commission",
        "FMSHRC": "federal-mine-safety-health-review-commission",
        "FRTIB": "federal-retirement-thrift-investment-board",
        "FTC": "federal-trade-commission",
        "GSA": "general-services-administration",
        "IAF": "inter-american-foundation",
        "DFC": "international-development-finance-corporation",
        "MSPB": "merit-systems-protection-board",
        "MCC": "millennium-challenge-corporation",
        "NASA": "national-aeronautics-space-administration",
        "NARA": "national-archives-records-administration",
        "NCPC": "national-capital-planning-commission",
        "NCD": "national-council-disability",
        "NCUA": "national-credit-union-administration",
        "NEA": "national-education-association",
        "NEH": "national-endowment-humanities",
        "NLRB": "national-labor-relations-board",
        "NMB": "national-mediation-board",
        "NOAA": "national-oceanic-atmospheric-administration",
        "NPS": "national-park-service",
        "NRO": "national-reconnaissance-office",
        "NSF": "national-science-foundation",
        "NTSB": "national-transportation-safety-board",
        "NRC": "nuclear-regulatory-commission",
        "NWTRB": "nuclear-waste-technical-review-board",
        "ODNI": "office-director-national-intelligence",
        "OGE": "office-government-ethics",
        "ONHIR": "office-navajo-hopi-indian-relocation",
        "OPM": "office-personnel-management",
        "PC": "peace-corps",
        "PBGC": "pension-benefit-guaranty-corporation",
        "PRC": "postal-regulatory-commission",
        "PCLOB": "privacy-civil-liberties-oversight-board",
        "PBRB": "public-buildings-reform-board",
        "SEC": "securities-exchange-commission",
        "SBA": "small-business-administration",
        "SSA": "social-security-administration",
        "SIGAR": "special-inspector-general-afghanistan-restoration",
        "STB": "surface-transportation-board",
        "TVA": "tennessee-valley-authority",
        "USU": "udall-foundation",
        "USAB": "access-board",
        "USAGM": "agency-global-media",
        "USCCR": "commission-civil-rights",
        "USCOURTS": "us-courts",
        "USITC": "international-trade-commission",
        "USPIS": "postal-inspection-service",
        "USPS": "postal-service",
        "RRB": "railroad-retirement-board",
        "USTDA": "trade-development-agency",
}

def validate_agency(agency: str) -> str:
    """Validate if the given agency is in the list of valid agencies."""
    if agency.lower() in agencies_list:
        return agency.lower()
    elif agency.upper() in agency_acronyms.keys():
        """Check if the agency is an acronym that exists in the keys of agency_acronyms
           and return the corresponding full agency name if it exists."""
        return agency_acronyms[agency.upper()]
    else:
        return ""



report_names = {
    "download": "The count of download events for each downloaded file",
    "traffic-source": "The count of visitors for each traffic source",
    "device-model": "The count of visitors for each device model",
    "domain": "The count of visitors for each domain",
    "site": "The count of visitors for each hostname",
    "second-level-domain": "The count of visitors to participating second-level-domains",
    "language": "The count of visitors for each browser language code",
    "os-browser": "The count of visitors broken down by browser and operating system",
    "windows-browser": "The count of visitors broken down by Windows versions and browser",
    "browser": "The count of visitors for each browser",
    "windows-ie": "The count of visitors broken down by Windows version and Internet Explorer versions (this report is only in API version 1.1)",
    "os": "The count of visitors for each operating system",
    "windows": "The count of visitors for each Windows version",
    "ie": "The count of users for each Internet Explorer version (this report is only in API version 1.1)",
    "device": "The count of users for each device type (desktop/mobile/tablet)",
}

def validate_report(report: str) -> str:
    """Validate if the given report name is in the list of valid report names."""
    if report.lower() in report_names.keys():
        return report.lower()
    else:
        return ""


def register(mcp: FastMCP) -> None:
    """Register the agency paramater resource(s) with the MCP server."""

    @mcp.resource("parameters://agencies")
    def agencies() -> str:
        """Return a list of U.S. federal agencies.
        
        This is a static list of U.S. federal agencies that can be used as parameter values
        for the analytic MCP tools.

        """        
        return json.dumps(agencies_list, indent=2)
 
    @mcp.resource("parameters://agency_acronyms")
    def agency_acronyms_resource() -> str:
        """Return a mapping of agency acronyms to full agency names.
        
        This is a static mapping that can be used as parameter values
        for the analytic MCP tools. The mapping keys are agency acronyms and the values are the corresponding full agency names.

        """        
        return json.dumps(agency_acronyms, indent=2)
       
    @mcp.resource("parameters://reports")
    def reports() -> str:
        """Return a list of analytic report names.
        
        This is a static list of  report names that can be used as parameter values
        for the analytic MCP tools.

        """        
        return json.dumps(list(report_names.keys()), indent=2)

    @mcp.resource("parameters://reports_definitions")
    def reports() -> str:
        """Return a list of analytic report names and their definitions.

        """        
        return json.dumps(report_names, indent=2)
