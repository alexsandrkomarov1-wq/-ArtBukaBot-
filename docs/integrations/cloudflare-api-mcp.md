# Cloudflare API MCP integration

Status: configured for compatible MCP clients; OAuth authorization is still required.

## Endpoint

- Server: `https://mcp.cloudflare.com/mcp`
- Transport: Streamable HTTP
- Authentication: Cloudflare OAuth, initiated by the MCP client
- Credentials: no API token, client secret, or refresh token is stored in this repository.

## Repository client configuration

The root `.mcp.json` registers the official Cloudflare API MCP server for MCP-compatible development clients. A client that supports remote Streamable HTTP MCP should initiate OAuth when connecting.

The MCP server exposes Cloudflare API discovery/execution and documentation tools. Account actions are limited by the permissions approved in Cloudflare's OAuth consent screen.

## Important boundaries

1. This configuration does not install Cloudflare as a native ChatGPT tool. ChatGPT must independently support and authorize custom remote MCP connections.
2. GitHub Pages is static hosting and must never hold Cloudflare OAuth tokens or API secrets.
3. KOMAROVA_CORE application code must not call the Cloudflare management API directly from browser JavaScript.
4. Do not create or enable paid Cloudflare products, Workers Paid plans, subscriptions, or billing methods as part of connecting this MCP server.
5. Use read-only or least-privilege Cloudflare permissions where available. Request write access only for a specific approved deployment or configuration task.
6. Keep Cloudflare account administration separate from the Supabase private family archive. Never expose family archive data through Cloudflare MCP tools.

## Connect

Open the Cloudflare MCP endpoint from an MCP-compatible client. The client should redirect to Cloudflare OAuth so the account owner can review and approve access. If the client does not support remote Streamable HTTP MCP or OAuth, this configuration remains inert and no connection is claimed.

## Official references

- Cloudflare API MCP: https://mcp.cloudflare.com/mcp
- Cloudflare documentation: https://developers.cloudflare.com/agents/model-context-protocol/cloudflare/servers-for-cloudflare/
- Cloudflare MCP source: https://github.com/cloudflare/mcp
