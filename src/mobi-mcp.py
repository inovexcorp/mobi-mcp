import argparse
from os import getenv

from mcp.server import FastMCP

from mobi import MobiClient


def init_mobi_client() -> MobiClient:
    """
    Initializes and returns an instance of the MobiClient class.

    This function retrieves the required credentials and base URL from
    environment variables and uses them to initialize a MobiClient object.
    It ensures secure configuration by fetching the necessary details
    dynamically.

    :raises KeyError: If any of the required environment variables
        (MOBI_BASE_URL, MOBI_USERNAME, MOBI_PASSWORD) are missing.
    :return: An instance of MobiClient initialized with the base URL and
        credentials.
    :rtype: MobiClient
    """
    base_url = getenv("MOBI_BASE_URL")
    username = getenv("MOBI_USERNAME")
    password = getenv("MOBI_PASSWORD")
    return MobiClient(base_url, username, password)


def parse_arguments():
    """
    Parses command-line arguments to configure and run the Mobi MCP Server.

    This function sets up an argument parser to handle command-line arguments
    for starting the Mobi MCP server. It allows specifying options such as
    enabling the SSE transport mechanism.

    :returns: Parsed arguments as a namespace object.
    :rtype: argparse.Namespace
    """
    parser = argparse.ArgumentParser(description="Mobi MCP Server")
    parser.add_argument("--sse", action="store_true", help="Start the MCP server with SSE transport")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    mcp: FastMCP = FastMCP('Mobi MCP Server')
    mobi: MobiClient = init_mobi_client()


    @mcp.tool(name="search_mobi_catalog",
              description="Search the mobi catalog for records whose metadata contain the provided string")
    def search_mobi_catalog_for_entities(search_for: str, offset: int, limit: int, types: list[str] | None = None,
                                         keywords: list[str] | None = None):
        """
        Search the Mobi catalog for entities matching the provided metadata criteria.

        This method performs a search in the Mobi catalog based on the given string and
        returns a list of entities that match the provided string in their metadata.
        Additional filtering is available through entity types and keywords.

        :param search_for: The substring to search for within the entities' metadata.
        :param offset: The starting point within the total result set to return.
        :param limit: The maximum number of entities to return.
        :param types: A list of entity types to filter the search results, or None for no filtering.
        :param keywords: A list of keywords to filter the search results, or None for no filtering.
        :return: Any
        """
        return mobi.entity_search(search_for, offset=offset, limit=limit, sort="entityName", ascending=True)


    @mcp.tool(name="fetch_ontology_data",
              description="Fetch ontology data for a given ontology record IRI (not the ontology IRI itself, "
                          "but the IRI of the 'record' containing the ontology data)")
    def fetch_ontology_data(ontology_iri: str):
        """
        Fetches ontology data for a given ontology record IRI.

        This function retrieves the ontology details associated with the provided
        IRI (Internationalized Resource Identifier) from the ontology data service.
        If the process is unsuccessful or the IRI is invalid, it may return None. The IRI of the record is what
        we're looking for here, not necessarily the IRI of the ontology itself:

        ```"record": {
                "iri": "https://mobi.com/records#6a535eff-2beb-4749-8549-6bf7de956a4e",
                ...
            }
        ```

        :param ontology_iri: The IRI of the record containing the ontology data which needs to be fetched.
        :type ontology_iri: str
        :return: A dictionary containing ontology data if successful, or None otherwise.
        :rtype: Optional[Dict[Any, Any]]
        """
        return mobi.get_ontology_data(ontology_iri)


    # Start MCP server
    if args.sse:
        mcp.run(transport="sse")
    else:
        mcp.run(transport="stdio")
