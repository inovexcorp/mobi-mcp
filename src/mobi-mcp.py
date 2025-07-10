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
    ignore_cert = getenv("MOBI_IGNORE_CERT", "false").lower() == "true"
    return MobiClient(base_url, username, password, ignore_cert=ignore_cert)


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


    @mcp.tool(name="record_search",
              description="Search the mobi catalog for records matching the provided criteria.")
    def search_mobi_catalog_for_records(offset: int, limit: int, search_text: str | None = None,
                                        keywords: list[str] | None = None,
                                        types: list[str] | None = None):
        """
        Searches the mobi catalog for records based on the given criteria.

        This function allows filtering of records by providing criteria such as
        offset for pagination, limit on the number of results, search text to be
        matched against records, specific keywords, and types of records. This
        is designed to interact with the mobi catalog and return a list of
        relevant records that match the provided criteria.  Value types are:

        :param offset: The starting index for the records to fetch (pagination offset).
        :type offset: int
        :param limit: The maximum number of records to retrieve.
        :type limit: int
        :param search_text: Optionally, text to search for in the records. If None, the
            search text filter will not be applied.
        :type search_text: str | None
        :param keywords: Optionally, a list of keywords to match against records. If
            None, no keyword filtering is applied.
        :type keywords: list[str] | None
        :param types: Optionally, a list of types to filter records by. If None, records
            of all types will be included in the search results.  Valid types to specify are:
            http://mobi.com/ontologies/ontology-editor#OntologyRecord (Ontology/Vocabulary),
            http://mobi.com/ontologies/shapes-graph-editor#ShapesGraphRecord (SHACL),
            http://mobi.com/ontologies/delimited#MappingRecord (Mappings),
            http://mobi.com/ontologies/dataset#DatasetRecord (Datasets).
        :type types: list[str] | None
        :return: A list of records matching the provided criteria.
        :rtype: list
        """
        return mobi.list_records(offset=offset, limit=limit, keywords=keywords, search_text=search_text, types=types)


    @mcp.tool(name="entity_search",
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


    @mcp.tool(name="get_shapes_graph", description="Get the shapes graph for a given record.")
    def get_shapes_graph(record_id: str, branch_id: str | None = None, commit_id: str | None = None):
        """
        Fetches the shapes graph for a specified record, branch, and commit.

        This function retrieves the shapes graph associated with the provided
        record ID. Optionally, it can also target a specific branch ID or
        commit ID within the record. This is useful for obtaining graph-related
        properties and structures stored in the system.

        :param record_id: The unique identifier for the record whose shapes
            graph is to be fetched.
        :param branch_id: The identifier for the branch within the record.
            This is optional and can be `None` if not specifying a branch.
        :param commit_id: The identifier for the commit within the record to
            target. This is optional and can be `None` if not specifying a
            commit.
        :return: The shapes graph retrieved for the specified record, branch,
            and commit.
        """
        return mobi.get_shapes_graph(record_id, branch_id, commit_id)


    @mcp.tool(name="create_ontology_record",
              description="Create an ontology record with the specified metadata and JSON-LD content."
                          "The metadata includes title, description, optional markdown description,"
                          "and keywords. The JSON-LD content is the ontology itself.")
    def create_ontology_record(jsonld: str, title: str, description: str, markdown_description: str | None = None,
                               keywords: list[str] | None = None):
        """
        Creates an ontology record with the specified metadata and JSON-LD content.

        This function processes the input parameters to create an ontology record in
        a structured format. The ontology is generated using the provided JSON-LD
        content and metadata parameters such as title, description, optional markdown
        description, and keywords.

        :param jsonld: A string containing the JSON-LD content for the ontology record.
        :param title: The title of the ontology, provided as a string.
        :param description: A brief description of the ontology, specified as a string.
        :param markdown_description: An optional markdown-formatted description for
            the ontology. If not provided, defaults to None.
        :param keywords: An optional list of keywords associated with the ontology.
            Each keyword should be provided as a string within the list. Defaults to None.
        :return: The created ontology record as processed by the `mobi.create_ontology`
            function.
        """
        return mobi.create_ontology(jsonld, title, description, markdown_description, keywords)


    # Start MCP server
    if args.sse:
        mcp.run(transport="sse")
    else:
        mcp.run(transport="stdio")
