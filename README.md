# Mobi MCP Server
This is a Model Context Protocol server that will allow agentic interfacing with a given instance of Mobi.

## Prerequisites
- Python 3.10 or higher (required for MCP package)
- A running Mobi instance

Model Context Protocol (MCP) is a standardized communication protocol that enables AI models to interact with external
tools and services. When integrated with Mobi, MCP provides several key benefits:

- Seamless interaction between AI models and Mobi's functionality
- Structured data exchange and command execution
- Real-time updates and bidirectional communication
- Enhanced automation capabilities through standardized interfaces
- Platform-agnostic integration with various AI models and services

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd mobi-mcp
   ```

2. **Create a Python virtual environment:**
   ```bash
   python3.12 -m venv .venv
   ```
   
   Note: If you don't have Python 3.10+, install it first:
   - macOS: `brew install python@3.12`

3. **Activate the virtual environment:**
   - macOS/Linux: `source .venv/bin/activate`

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Leveraging the MCP Server
The easiest way to quickly try this is to hook the MCP server into [Claude Desktop](https://claude.ai/download) and then
configure the application to use your MCP server by modifying the 
`~/Library/Application\ Support/Claude/claude_desktop_config.json` file with a JSON snippet like this:

```json
{
  "mcpServers": {
    "mobi": {
      "command": "/Users/{username}/git/mobi-mcp/.venv/bin/python",
      "args": ["/Users/{username}/git/mobi-mcp/src/mobi-mcp.py"],
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
**-- Note: You'll have to adjust the paths as absolute paths are required :)**

Claude Desktop leverages the stdio MCP transport, but this server also supports SSE as well (you can run the `mobi-mcp`
python script with the argument `--sse`).

## Configuration

The MCP server requires the following environment variables:

- `MOBI_BASE_URL`: The base URL of your Mobi instance (e.g., `https://localhost:8443`)
- `MOBI_USERNAME`: Username for Mobi authentication
- `MOBI_PASSWORD`: Password for Mobi authentication
- `MOBI_IGNORE_CERT`: Set to `"true"` to ignore SSL certificate verification (useful for self-signed certificates)

  





