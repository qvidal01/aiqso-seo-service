#!/usr/bin/env node
/**
 * SerpBear MCP Server
 *
 * Provides SERP tracking tools for Claude via the Model Context Protocol.
 *
 * Tools:
 * - serp_add_keyword: Add a keyword to track
 * - serp_check_rankings: Get current rankings for a domain
 * - serp_history: Get ranking history for a keyword
 * - serp_add_domain: Add a new domain to track
 * - serp_list_domains: List all tracked domains
 * - serp_list_keywords: List keywords for a domain
 * - serp_refresh: Trigger a manual refresh of rankings
 */

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  Tool,
} from "@modelcontextprotocol/sdk/types.js";
import axios, { AxiosInstance } from "axios";

// Configuration from environment
const SERPBEAR_URL = process.env.SERPBEAR_URL || "http://localhost:3000";
const SERPBEAR_API_KEY = process.env.SERPBEAR_API_KEY || "";

// SerpBear API client
class SerpBearClient {
  private client: AxiosInstance;

  constructor(baseUrl: string, apiKey: string) {
    this.client = axios.create({
      baseURL: baseUrl,
      headers: {
        Authorization: `Bearer ${apiKey}`,
        "Content-Type": "application/json",
      },
    });
  }

  async getDomains(): Promise<any[]> {
    const response = await this.client.get("/api/domains");
    return response.data?.domains || [];
  }

  async addDomain(domain: string): Promise<any> {
    const response = await this.client.post("/api/domains", { domain });
    return response.data;
  }

  async getKeywords(domainId: number): Promise<any[]> {
    const response = await this.client.get(`/api/keywords?domain=${domainId}`);
    return response.data?.keywords || [];
  }

  async addKeyword(
    domainId: number,
    keyword: string,
    device: string = "desktop",
    country: string = "US"
  ): Promise<any> {
    const response = await this.client.post("/api/keywords", {
      domain: domainId,
      keywords: keyword,
      device,
      country,
    });
    return response.data;
  }

  async getKeywordHistory(keywordId: number, days: number = 30): Promise<any> {
    const response = await this.client.get(
      `/api/keywords/${keywordId}/history?days=${days}`
    );
    return response.data;
  }

  async refreshDomain(domainId: number): Promise<any> {
    const response = await this.client.post("/api/refresh", {
      domain: domainId,
    });
    return response.data;
  }

  async getInsights(domainId: number): Promise<any> {
    const response = await this.client.get(`/api/insight?domain=${domainId}`);
    return response.data;
  }
}

// Initialize the MCP server
const server = new Server(
  {
    name: "serpbear-mcp",
    version: "1.0.0",
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// Initialize SerpBear client
const serpbear = new SerpBearClient(SERPBEAR_URL, SERPBEAR_API_KEY);

// Define available tools
const tools: Tool[] = [
  {
    name: "serp_list_domains",
    description: "List all domains being tracked in SerpBear",
    inputSchema: {
      type: "object",
      properties: {},
      required: [],
    },
  },
  {
    name: "serp_add_domain",
    description: "Add a new domain to track in SerpBear",
    inputSchema: {
      type: "object",
      properties: {
        domain: {
          type: "string",
          description: "The domain to track (e.g., example.com)",
        },
      },
      required: ["domain"],
    },
  },
  {
    name: "serp_list_keywords",
    description: "List all keywords being tracked for a domain",
    inputSchema: {
      type: "object",
      properties: {
        domain: {
          type: "string",
          description: "The domain name to list keywords for",
        },
      },
      required: ["domain"],
    },
  },
  {
    name: "serp_add_keyword",
    description: "Add a keyword to track for a domain",
    inputSchema: {
      type: "object",
      properties: {
        domain: {
          type: "string",
          description: "The domain to track the keyword for",
        },
        keyword: {
          type: "string",
          description: "The keyword/search term to track",
        },
        device: {
          type: "string",
          enum: ["desktop", "mobile"],
          description: "Device type to track (default: desktop)",
        },
        country: {
          type: "string",
          description: "Country code for tracking (default: US)",
        },
      },
      required: ["domain", "keyword"],
    },
  },
  {
    name: "serp_check_rankings",
    description:
      "Get current keyword rankings for a domain with position changes",
    inputSchema: {
      type: "object",
      properties: {
        domain: {
          type: "string",
          description: "The domain to check rankings for",
        },
      },
      required: ["domain"],
    },
  },
  {
    name: "serp_keyword_history",
    description: "Get ranking history for a specific keyword over time",
    inputSchema: {
      type: "object",
      properties: {
        domain: {
          type: "string",
          description: "The domain the keyword belongs to",
        },
        keyword: {
          type: "string",
          description: "The keyword to get history for",
        },
        days: {
          type: "number",
          description: "Number of days of history (default: 30)",
        },
      },
      required: ["domain", "keyword"],
    },
  },
  {
    name: "serp_refresh",
    description: "Trigger a manual refresh of rankings for a domain",
    inputSchema: {
      type: "object",
      properties: {
        domain: {
          type: "string",
          description: "The domain to refresh rankings for",
        },
      },
      required: ["domain"],
    },
  },
  {
    name: "serp_insights",
    description:
      "Get SEO insights and analytics for a domain (avg position, trends)",
    inputSchema: {
      type: "object",
      properties: {
        domain: {
          type: "string",
          description: "The domain to get insights for",
        },
      },
      required: ["domain"],
    },
  },
];

// Handle list tools request
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return { tools };
});

// Handle tool calls
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    switch (name) {
      case "serp_list_domains": {
        const domains = await serpbear.getDomains();

        if (domains.length === 0) {
          return {
            content: [
              {
                type: "text",
                text: "No domains are currently being tracked. Use serp_add_domain to add one.",
              },
            ],
          };
        }

        const lines = ["## Tracked Domains", ""];
        lines.push("| Domain | Keywords | Last Updated |");
        lines.push("|--------|----------|--------------|");

        for (const domain of domains) {
          lines.push(
            `| ${domain.domain} | ${domain.keywordCount || 0} | ${domain.lastUpdated || "Never"} |`
          );
        }

        return {
          content: [{ type: "text", text: lines.join("\n") }],
        };
      }

      case "serp_add_domain": {
        const domain = (args as { domain: string }).domain;
        const result = await serpbear.addDomain(domain);

        return {
          content: [
            {
              type: "text",
              text: `Domain **${domain}** has been added for tracking.\n\nUse \`serp_add_keyword\` to add keywords to track for this domain.`,
            },
          ],
        };
      }

      case "serp_list_keywords": {
        const domain = (args as { domain: string }).domain;
        const domains = await serpbear.getDomains();
        const domainObj = domains.find((d: any) => d.domain === domain);

        if (!domainObj) {
          return {
            content: [
              {
                type: "text",
                text: `Domain "${domain}" not found. Use serp_list_domains to see tracked domains.`,
              },
            ],
          };
        }

        const keywords = await serpbear.getKeywords(domainObj.ID);

        if (keywords.length === 0) {
          return {
            content: [
              {
                type: "text",
                text: `No keywords tracked for ${domain}. Use serp_add_keyword to add keywords.`,
              },
            ],
          };
        }

        const lines = [`## Keywords for ${domain}`, ""];
        lines.push("| Keyword | Position | Change | Device | Country |");
        lines.push("|---------|----------|--------|--------|---------|");

        for (const kw of keywords) {
          const change =
            kw.position_change > 0
              ? `+${kw.position_change}`
              : kw.position_change.toString();
          const changeEmoji =
            kw.position_change > 0 ? "📈" : kw.position_change < 0 ? "📉" : "➖";
          lines.push(
            `| ${kw.keyword} | ${kw.position || "N/A"} | ${changeEmoji} ${change} | ${kw.device} | ${kw.country} |`
          );
        }

        return {
          content: [{ type: "text", text: lines.join("\n") }],
        };
      }

      case "serp_add_keyword": {
        const {
          domain,
          keyword,
          device = "desktop",
          country = "US",
        } = args as {
          domain: string;
          keyword: string;
          device?: string;
          country?: string;
        };

        const domains = await serpbear.getDomains();
        const domainObj = domains.find((d: any) => d.domain === domain);

        if (!domainObj) {
          return {
            content: [
              {
                type: "text",
                text: `Domain "${domain}" not found. Add it first with serp_add_domain.`,
              },
            ],
          };
        }

        await serpbear.addKeyword(domainObj.ID, keyword, device, country);

        return {
          content: [
            {
              type: "text",
              text: `Keyword "**${keyword}**" added for ${domain}\n- Device: ${device}\n- Country: ${country}\n\nRankings will be checked on the next scheduled refresh or use serp_refresh to check now.`,
            },
          ],
        };
      }

      case "serp_check_rankings": {
        const domain = (args as { domain: string }).domain;
        const domains = await serpbear.getDomains();
        const domainObj = domains.find((d: any) => d.domain === domain);

        if (!domainObj) {
          return {
            content: [
              {
                type: "text",
                text: `Domain "${domain}" not found.`,
              },
            ],
          };
        }

        const keywords = await serpbear.getKeywords(domainObj.ID);

        if (keywords.length === 0) {
          return {
            content: [
              {
                type: "text",
                text: `No keywords tracked for ${domain}.`,
              },
            ],
          };
        }

        // Calculate summary stats
        const positions = keywords
          .filter((k: any) => k.position)
          .map((k: any) => k.position);
        const avgPosition =
          positions.length > 0
            ? (
                positions.reduce((a: number, b: number) => a + b, 0) /
                positions.length
              ).toFixed(1)
            : "N/A";
        const top10 = positions.filter((p: number) => p <= 10).length;
        const top3 = positions.filter((p: number) => p <= 3).length;

        const lines = [`## Rankings for ${domain}`, ""];
        lines.push(`**Summary:**`);
        lines.push(`- Total Keywords: ${keywords.length}`);
        lines.push(`- Average Position: ${avgPosition}`);
        lines.push(`- Top 3: ${top3} keywords`);
        lines.push(`- Top 10: ${top10} keywords`);
        lines.push("");
        lines.push("### Keyword Rankings");
        lines.push("| Keyword | Position | Change | URL |");
        lines.push("|---------|----------|--------|-----|");

        for (const kw of keywords) {
          const pos = kw.position || "N/A";
          const change =
            kw.position_change > 0
              ? `+${kw.position_change}`
              : kw.position_change?.toString() || "0";
          const emoji =
            kw.position_change > 0
              ? "📈"
              : kw.position_change < 0
                ? "📉"
                : "➖";
          const url = kw.url ? kw.url.substring(0, 40) + "..." : "N/A";
          lines.push(`| ${kw.keyword} | ${pos} | ${emoji} ${change} | ${url} |`);
        }

        return {
          content: [{ type: "text", text: lines.join("\n") }],
        };
      }

      case "serp_keyword_history": {
        const { domain, keyword, days = 30 } = args as {
          domain: string;
          keyword: string;
          days?: number;
        };

        const domains = await serpbear.getDomains();
        const domainObj = domains.find((d: any) => d.domain === domain);

        if (!domainObj) {
          return {
            content: [{ type: "text", text: `Domain "${domain}" not found.` }],
          };
        }

        const keywords = await serpbear.getKeywords(domainObj.ID);
        const keywordObj = keywords.find(
          (k: any) => k.keyword.toLowerCase() === keyword.toLowerCase()
        );

        if (!keywordObj) {
          return {
            content: [
              {
                type: "text",
                text: `Keyword "${keyword}" not found for ${domain}.`,
              },
            ],
          };
        }

        const history = await serpbear.getKeywordHistory(keywordObj.ID, days);

        const lines = [
          `## Ranking History: "${keyword}" on ${domain}`,
          "",
          `**Current Position:** ${keywordObj.position || "N/A"}`,
          `**Period:** Last ${days} days`,
          "",
          "### Position History",
          "| Date | Position | Change |",
          "|------|----------|--------|",
        ];

        // Add history rows (limit to 20 most recent)
        const historyData = history?.history || [];
        const recentHistory = historyData.slice(0, 20);

        for (const entry of recentHistory) {
          const date = new Date(entry.date).toLocaleDateString();
          const pos = entry.position || "N/A";
          const change = entry.change
            ? entry.change > 0
              ? `+${entry.change}`
              : entry.change.toString()
            : "0";
          lines.push(`| ${date} | ${pos} | ${change} |`);
        }

        return {
          content: [{ type: "text", text: lines.join("\n") }],
        };
      }

      case "serp_refresh": {
        const domain = (args as { domain: string }).domain;
        const domains = await serpbear.getDomains();
        const domainObj = domains.find((d: any) => d.domain === domain);

        if (!domainObj) {
          return {
            content: [{ type: "text", text: `Domain "${domain}" not found.` }],
          };
        }

        await serpbear.refreshDomain(domainObj.ID);

        return {
          content: [
            {
              type: "text",
              text: `Refresh triggered for **${domain}**.\n\nRankings are being updated in the background. Check back in a few minutes for updated positions.`,
            },
          ],
        };
      }

      case "serp_insights": {
        const domain = (args as { domain: string }).domain;
        const domains = await serpbear.getDomains();
        const domainObj = domains.find((d: any) => d.domain === domain);

        if (!domainObj) {
          return {
            content: [{ type: "text", text: `Domain "${domain}" not found.` }],
          };
        }

        const insights = await serpbear.getInsights(domainObj.ID);
        const keywords = await serpbear.getKeywords(domainObj.ID);

        // Calculate stats
        const positions = keywords
          .filter((k: any) => k.position)
          .map((k: any) => k.position);
        const avgPos =
          positions.length > 0
            ? (
                positions.reduce((a: number, b: number) => a + b, 0) /
                positions.length
              ).toFixed(1)
            : "N/A";

        const improving = keywords.filter(
          (k: any) => k.position_change > 0
        ).length;
        const declining = keywords.filter(
          (k: any) => k.position_change < 0
        ).length;
        const stable = keywords.filter(
          (k: any) => k.position_change === 0
        ).length;

        const lines = [
          `## SEO Insights: ${domain}`,
          "",
          "### Overview",
          `- **Total Keywords:** ${keywords.length}`,
          `- **Average Position:** ${avgPos}`,
          `- **Top 3 Rankings:** ${positions.filter((p: number) => p <= 3).length}`,
          `- **Top 10 Rankings:** ${positions.filter((p: number) => p <= 10).length}`,
          `- **Page 2+ Rankings:** ${positions.filter((p: number) => p > 10).length}`,
          "",
          "### Movement",
          `- 📈 Improving: ${improving} keywords`,
          `- 📉 Declining: ${declining} keywords`,
          `- ➖ Stable: ${stable} keywords`,
          "",
        ];

        // Top improving keywords
        const topImproving = keywords
          .filter((k: any) => k.position_change > 0)
          .sort((a: any, b: any) => b.position_change - a.position_change)
          .slice(0, 5);

        if (topImproving.length > 0) {
          lines.push("### Top Improving Keywords");
          for (const kw of topImproving) {
            lines.push(`- **${kw.keyword}**: +${kw.position_change} positions`);
          }
          lines.push("");
        }

        // Top declining keywords
        const topDeclining = keywords
          .filter((k: any) => k.position_change < 0)
          .sort((a: any, b: any) => a.position_change - b.position_change)
          .slice(0, 5);

        if (topDeclining.length > 0) {
          lines.push("### Top Declining Keywords");
          for (const kw of topDeclining) {
            lines.push(`- **${kw.keyword}**: ${kw.position_change} positions`);
          }
          lines.push("");
        }

        return {
          content: [{ type: "text", text: lines.join("\n") }],
        };
      }

      default:
        return {
          content: [{ type: "text", text: `Unknown tool: ${name}` }],
          isError: true,
        };
    }
  } catch (error: any) {
    return {
      content: [
        {
          type: "text",
          text: `Error: ${error.message || "Unknown error occurred"}`,
        },
      ],
      isError: true,
    };
  }
});

// Start the server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("SerpBear MCP server running on stdio");
}

main().catch(console.error);
