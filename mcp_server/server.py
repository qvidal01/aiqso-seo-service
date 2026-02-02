#!/usr/bin/env python3
"""
AIQSO SEO MCP Server

Provides SEO audit tools for Claude via the Model Context Protocol.

Tools:
- seo_audit_url: Audit a single URL for SEO issues
- seo_check_meta: Check meta tags only (quick)
- seo_check_performance: Check performance only (quick)
- seo_score: Get overall SEO score for a URL
- seo_compare: Compare SEO scores between two URLs
- seo_tiers: List available service tiers
"""

import asyncio
import json
import sys
from typing import Any, Sequence
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
    CallToolResult,
)

from src.core.auditor import SEOAuditor, AuditResult
from src.core.tiers import get_tier_manager

# Initialize MCP server
mcp_server = Server("aiqso-seo")


def format_audit_result(result: AuditResult) -> str:
    """Format an audit result for MCP response."""
    lines = []
    lines.append(f"## SEO Audit Results: {result.url}")
    lines.append("")
    lines.append(f"**Overall Score:** {result.overall_score}/100")
    lines.append("")
    lines.append("### Category Scores")
    lines.append(f"- Configuration: {result.configuration_score}/100")
    lines.append(f"- Meta Tags: {result.meta_score}/100")
    lines.append(f"- Content: {result.content_score}/100")
    lines.append(f"- Performance: {result.performance_score}/100")
    lines.append("")
    lines.append(f"**Issues Found:** {result.issues_found}")
    lines.append(f"**Warnings:** {result.warnings_found}")
    lines.append(f"**Duration:** {result.duration_seconds:.2f}s")
    lines.append("")

    # Failed checks
    failed = [c for c in result.checks if not c.passed]
    if failed:
        lines.append("### Issues to Fix")
        for check in failed:
            severity = check.severity.upper()
            lines.append(f"- **[{severity}]** {check.title}: {check.current_value or 'N/A'}")
            if check.recommendation:
                lines.append(f"  - Recommendation: {check.recommendation}")
        lines.append("")

    # Passed checks
    passed = [c for c in result.checks if c.passed]
    if passed:
        lines.append("### Passed Checks")
        for check in passed:
            lines.append(f"- {check.title}: {check.current_value or 'OK'}")
        lines.append("")

    # AI Summary
    if result.ai_summary:
        lines.append("### AI Insights")
        lines.append(result.ai_summary)
        lines.append("")

    return "\n".join(lines)


@mcp_server.list_tools()
async def list_tools() -> list[Tool]:
    """List available SEO tools."""
    return [
        Tool(
            name="seo_audit_url",
            description="Perform a comprehensive SEO audit on a URL. Checks configuration, meta tags, content quality, and performance.",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The URL to audit (e.g., https://example.com)"
                    },
                    "include_ai": {
                        "type": "boolean",
                        "description": "Include AI-powered insights (requires ANTHROPIC_API_KEY)",
                        "default": False
                    }
                },
                "required": ["url"]
            }
        ),
        Tool(
            name="seo_check_meta",
            description="Quick check of meta tags only (title, description, OG tags, Twitter cards, etc.)",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The URL to check"
                    }
                },
                "required": ["url"]
            }
        ),
        Tool(
            name="seo_check_performance",
            description="Quick check of performance metrics only (TTFB, page size, compression)",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The URL to check"
                    }
                },
                "required": ["url"]
            }
        ),
        Tool(
            name="seo_score",
            description="Get just the SEO score for a URL without full details",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The URL to score"
                    }
                },
                "required": ["url"]
            }
        ),
        Tool(
            name="seo_compare",
            description="Compare SEO scores between two URLs (e.g., your site vs competitor)",
            inputSchema={
                "type": "object",
                "properties": {
                    "url1": {
                        "type": "string",
                        "description": "First URL to compare"
                    },
                    "url2": {
                        "type": "string",
                        "description": "Second URL to compare"
                    }
                },
                "required": ["url1", "url2"]
            }
        ),
        Tool(
            name="seo_tiers",
            description="List available service tiers and their features/limits",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
    ]


@mcp_server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> Sequence[TextContent]:
    """Handle tool calls."""

    if name == "seo_audit_url":
        url = arguments.get("url", "")
        include_ai = arguments.get("include_ai", False)

        if not url:
            return [TextContent(type="text", text="Error: URL is required")]

        # Ensure URL has protocol
        if not url.startswith(("http://", "https://")):
            url = f"https://{url}"

        async with SEOAuditor() as auditor:
            result = await auditor.audit_url(url, include_ai=include_ai)

        return [TextContent(type="text", text=format_audit_result(result))]

    elif name == "seo_check_meta":
        url = arguments.get("url", "")

        if not url:
            return [TextContent(type="text", text="Error: URL is required")]

        if not url.startswith(("http://", "https://")):
            url = f"https://{url}"

        async with SEOAuditor() as auditor:
            result = await auditor.audit_url(url)

        # Filter to meta checks only
        meta_checks = [c for c in result.checks if c.category == "meta"]
        lines = [f"## Meta Tag Check: {url}", ""]
        lines.append(f"**Meta Score:** {result.meta_score}/100")
        lines.append("")

        for check in meta_checks:
            status = "PASS" if check.passed else check.severity.upper()
            lines.append(f"- **[{status}]** {check.title}: {check.current_value or 'N/A'}")
            if not check.passed and check.recommendation:
                lines.append(f"  - {check.recommendation}")

        return [TextContent(type="text", text="\n".join(lines))]

    elif name == "seo_check_performance":
        url = arguments.get("url", "")

        if not url:
            return [TextContent(type="text", text="Error: URL is required")]

        if not url.startswith(("http://", "https://")):
            url = f"https://{url}"

        async with SEOAuditor() as auditor:
            result = await auditor.audit_url(url)

        # Filter to performance checks only
        perf_checks = [c for c in result.checks if c.category == "performance"]
        lines = [f"## Performance Check: {url}", ""]
        lines.append(f"**Performance Score:** {result.performance_score}/100")
        lines.append("")

        for check in perf_checks:
            status = "PASS" if check.passed else check.severity.upper()
            lines.append(f"- **[{status}]** {check.title}: {check.current_value or 'N/A'}")

        return [TextContent(type="text", text="\n".join(lines))]

    elif name == "seo_score":
        url = arguments.get("url", "")

        if not url:
            return [TextContent(type="text", text="Error: URL is required")]

        if not url.startswith(("http://", "https://")):
            url = f"https://{url}"

        async with SEOAuditor() as auditor:
            result = await auditor.audit_url(url)

        text = f"""## SEO Score: {url}

**Overall:** {result.overall_score}/100

| Category | Score |
|----------|-------|
| Configuration | {result.configuration_score}/100 |
| Meta Tags | {result.meta_score}/100 |
| Content | {result.content_score}/100 |
| Performance | {result.performance_score}/100 |

Issues: {result.issues_found} | Warnings: {result.warnings_found}
"""
        return [TextContent(type="text", text=text)]

    elif name == "seo_compare":
        url1 = arguments.get("url1", "")
        url2 = arguments.get("url2", "")

        if not url1 or not url2:
            return [TextContent(type="text", text="Error: Both url1 and url2 are required")]

        if not url1.startswith(("http://", "https://")):
            url1 = f"https://{url1}"
        if not url2.startswith(("http://", "https://")):
            url2 = f"https://{url2}"

        async with SEOAuditor() as auditor:
            result1 = await auditor.audit_url(url1)
            result2 = await auditor.audit_url(url2)

        def diff_str(v1: int, v2: int) -> str:
            diff = v1 - v2
            if diff > 0:
                return f"+{diff}"
            return str(diff)

        text = f"""## SEO Comparison

| Metric | {url1[:30]}... | {url2[:30]}... | Diff |
|--------|-------------|-------------|------|
| **Overall** | {result1.overall_score} | {result2.overall_score} | {diff_str(result1.overall_score, result2.overall_score)} |
| Configuration | {result1.configuration_score} | {result2.configuration_score} | {diff_str(result1.configuration_score, result2.configuration_score)} |
| Meta Tags | {result1.meta_score} | {result2.meta_score} | {diff_str(result1.meta_score, result2.meta_score)} |
| Content | {result1.content_score} | {result2.content_score} | {diff_str(result1.content_score, result2.content_score)} |
| Performance | {result1.performance_score} | {result2.performance_score} | {diff_str(result1.performance_score, result2.performance_score)} |
| Issues | {result1.issues_found} | {result2.issues_found} | {diff_str(result1.issues_found, result2.issues_found)} |

**Winner:** {"URL 1" if result1.overall_score > result2.overall_score else "URL 2" if result2.overall_score > result1.overall_score else "Tie"}
"""
        return [TextContent(type="text", text=text)]

    elif name == "seo_tiers":
        manager = get_tier_manager()
        all_tiers = manager.get_all_tiers()

        lines = ["## AIQSO SEO Service Tiers", ""]

        for name, tier in sorted(all_tiers.items(), key=lambda x: x[1].price_monthly or 0):
            price = f"${tier.price_monthly}/mo" if tier.price_monthly else "Free"
            lines.append(f"### {tier.display_name} ({price})")
            lines.append(f"_{tier.description}_")
            lines.append("")
            lines.append("**Features:**")
            lines.append(f"- AI Insights: {'Yes' if tier.features.ai_insights else 'No'}")
            lines.append(f"- Lighthouse: {'Yes' if tier.features.lighthouse_integration else 'No'}")
            lines.append(f"- Full Site Crawl: {'Yes' if tier.features.full_site_crawl else 'No'}")
            lines.append(f"- API Access: {'Yes' if tier.features.api_access else 'No'}")
            lines.append(f"- White Label: {'Yes' if tier.features.white_label else 'No'}")
            lines.append("")
            lines.append("**Limits:**")
            lines.append(f"- Audits/Day: {tier.rate_limits.audits_per_day or 'Unlimited'}")
            lines.append(f"- Keywords: {tier.rate_limits.keywords_tracked or 'N/A'}")
            lines.append(f"- Websites: {tier.rate_limits.websites or 'Unlimited'}")
            lines.append("")
            lines.append("---")
            lines.append("")

        return [TextContent(type="text", text="\n".join(lines))]

    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await mcp_server.run(
            read_stream,
            write_stream,
            mcp_server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
