# Mobi MCP Server
This is a Model Context Protocol server that will allow agentic interfacing with a given instance of 
[Mobi](https://mobi.solutions/) ([GitHub](https://github.com/inovexcorp/mobi)).

<img src="logo.png" alt="mobi-mcp-logo" style="width: 100px;" \>

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

This also assumes that you are running an instance of Mobi as well. If you want to try and run one locally,
see instructions [HERE](https://inovexcorp.github.io/mobi-docs/latest/index.html#installing_the_docker_image).

## Configuration

The MCP server requires the following environment variables:

- `MOBI_BASE_URL`: The base URL of your Mobi instance (e.g., `https://localhost:8443`)
- `MOBI_USERNAME`: Username for Mobi authentication
- `MOBI_PASSWORD`: Password for Mobi authentication
- `MOBI_IGNORE_CERT`: Set to `"true"` to ignore SSL certificate verification (useful for self-signed certificates)

## Repository Structure
The repository is organized to maintain a clean separation between the Mobi API interaction layer and the MCP protocol
implementation:

- **`src/mobi.py`** - Contains the core Mobi API client functionality, handling authentication, API calls, and data processing
- **`src/mobi-mcp.py`** - The main MCP server implementation that bridges Mobi functionality with the Model Context Protocol
- **`Dockerfile`** - Enables containerized deployment of the MCP server
- **`Makefile`** - Provides convenient commands for environment setup and container management
- **`requirements.txt`** - Lists all Python package dependencies needed for the project



## Current Tools
The Mobi MCP Server exposes the following tools for interacting with your Mobi instance:

### Search and Discovery Tools

#### `record_search`
Search the Mobi catalog for records matching specified criteria.
- **Parameters:**
  - `offset` (int): Starting index for pagination
  - `limit` (int): Maximum number of records to retrieve
  - `search_text` (str, optional): Text to search for in records
  - `keywords` (list[str], optional): Keywords to match against records
  - `types` (list[str], optional): Record types to filter by. Valid types:
    - `http://mobi.com/ontologies/ontology-editor#OntologyRecord` (Ontology/Vocabulary)
    - `http://mobi.com/ontologies/shapes-graph-editor#ShapesGraphRecord` (SHACL)
    - `http://mobi.com/ontologies/delimited#MappingRecord` (Mappings)
    - `http://mobi.com/ontologies/dataset#DatasetRecord` (Datasets)

#### `entity_search`
Search the Mobi catalog for records whose metadata contain a specified string.
- **Parameters:**
  - `search_for` (str): Substring to search for within entities' metadata
  - `offset` (int): Starting point within the result set
  - `limit` (int): Maximum number of entities to return
  - `types` (list[str], optional): Entity types to filter by
  - `keywords` (list[str], optional): Keywords to filter by

### Data Retrieval Tools

#### `fetch_ontology_data`
Fetch ontology data for a given ontology record IRI.
- **Parameters:**
  - `ontology_iri` (str): The IRI of the record containing the ontology data (not the ontology IRI itself)
- **Note:** Use the record IRI from search results, typically in the format `https://mobi.com/records#<uuid>`

#### `get_shapes_graph`
Retrieve the shapes graph for a specified record.
- **Parameters:**
  - `record_id` (str): Unique identifier for the record
  - `branch_id` (str, optional): Branch identifier within the record
  - `commit_id` (str, optional): Commit identifier to target

### Content Creation Tools

#### `create_ontology_record`
Create a new ontology record from RDF data and metadata.
- **Parameters:**
  - `rdf_string` (str): The RDF data as a string
  - `rdf_format` (str): Format of the RDF data (e.g., "xml", "turtle")
  - `title` (str): Title of the ontology
  - `description` (str): Textual description of the ontology
  - `markdown_description` (str, optional): Markdown version of the description
  - `keywords` (list[str], optional): Keywords associated with the ontology
- **Note:** Confirmation with the user is recommended before creating new records

### Version Control Tools

#### `create_branch_on_record`
Create a new branch on an existing record.
- **Parameters:**
  - `record_iri` (str): IRI of the record
  - `title` (str): Title of the new branch
  - `description` (str): Description of the new branch
  - `commit_iri` (str): IRI of the commit to use as reference

### Usage Notes
- All tools interact with Mobi's git-inspired versioning system
- Record IRIs are typically returned from search operations
- The server follows semantic versioning practices similar to git repositories
- Always verify record and branch IRIs before performing write operations
