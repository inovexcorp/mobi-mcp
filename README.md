# Mobi MCP Server
This is a Model Context Protocol server that will allow agentic interfacing with a given instance of Mobi.

Model Context Protocol (MCP) is a standardized communication protocol that enables AI models to interact with external
tools and services. When integrated with Mobi, MCP provides several key benefits:

- Seamless interaction between AI models and Mobi's functionality
- Structured data exchange and command execution
- Real-time updates and bidirectional communication
- Enhanced automation capabilities through standardized interfaces
- Platform-agnostic integration with various AI models and services

## Leveraging the MCP Server
The easiest way to quickly try this is to hook the MCP server into [Claude Desktop](https://claude.ai/download) and then
configure the application to use your MCP server by modifying the 
`~/Library/Application\ Support/Claude/claude_desktop_config.json` file with a JSON snippet like this:

```json
{
  "mcpServers": {
    "mobi": {
      "command": "/Users/ben.gould/git/mobi-mcp/.venv/bin/python",
      "args": ["/Users/ben.gould/git/mobi-mcp/src/mobi-mcp.py"],
      "env": {
        "MOBI_BASE_URL": "https://localhost:8443",
        "MOBI_USERNAME": "admin",
        "MOBI_PASSWORD": "admin",
        "MOBI_IGNORE_CERT": "true"
      }
    }
  }
}
```

Claude Desktop leverages the stdio MCP transport, but this server also supports SSE as well (you can run the `mobi-mcp`
python script with the argument `--sse`).  





