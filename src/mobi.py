import json
import urllib.parse
from os import getenv
from typing import Optional, Dict, Any

import dotenv
import requests
from requests import RequestException

default_catalogs: str = "http://mobi.com/catalog-local"
rest_context: str = "mobirest"

record_types: list[str] = [
    "http://mobi.com/ontologies/ontology-editor#OntologyRecord",
    "http://mobi.com/ontologies/shapes-graph-editor#ShapesGraphRecord",
    "http://mobi.com/ontologies/delimited#MappingRecord",
    "http://mobi.com/ontologies/dataset#DatasetRecord",
]


class MobiClient:
    """
    Represents a client for accessing and interacting with a Mobi API. This class facilitates
    operations such as retrieving records, fetching ontology data, performing entity searches,
    and executing HTTP requests with proper authorization and optional certificate verification.

    Designed to interface with the REST API, this client provides methods that simplify common
    use cases while automatically handling authentication, URL construction, and request execution.
    It can be used to support various catalog-based and ontology-driven workflows.

    :ivar base_url: The base URL for the API endpoint.
    :type base_url: str
    :ivar username: Username for authentication.
    :type username: str
    :ivar password: Password for authentication.
    :type password: str
    :ivar ignore_cert: Whether to ignore SSL certificate verification.
    :type ignore_cert: bool
    """

    def __init__(self, base_url: str, username: str, password: str, ignore_cert: bool = False):
        """
        Initializes the instance with the provided parameters.

        :param base_url: The base URL of the API or system to connect to.
        :param username: The username to authenticate the connection.
        :param password: The password associated with the username for authentication.
        :param ignore_cert: Whether or not to ignore SSL certificate validation. Defaults to False.
        """
        self.base_url: str = base_url
        self.username: str = username
        self.password: str = password
        self.ignore_cert: bool = ignore_cert

    def get_record(self, record_id: str, catalog_id: str = default_catalogs) -> Optional[Dict[Any, Any]]:
        """
        Retrieves a record from the catalog by its identifier.

        Constructs a URL based on the provided `record_id` and `catalog_id` to make
        a GET request to the REST API to fetch the record. The method returns the
        retrieved record as a dictionary or `None` if no record is found.

        :param record_id: The unique identifier of the record to retrieve.
        :type record_id: str
        :param catalog_id: The unique identifier of the catalog to search within.
                           If not provided, defaults to `default_catalogs`.
        :type catalog_id: str
        :return: A dictionary containing the record data if found, otherwise None.
        :rtype: Optional[Dict[Any, Any]]
        """
        url = (f"{self.base_url}/{rest_context}/catalogs/{urllib.parse.quote(catalog_id, safe='')}"
               f"/records/{urllib.parse.quote(record_id, safe='')}")
        return self._make_request(url, "GET")

    def get_ontology_data(self, record_id: str) -> Optional[Dict[Any, Any]]:
        """
        Fetches ontology data for a specific record.

        This method constructs a URL to request ontology data corresponding to
        the provided record ID. It sends a GET request to the URL using the
        internal `_make_request` method and returns the response data if the
        request is successful.

        :param record_id: ID of the ontology record to fetch.
        :type record_id: str
        :return: Ontology data as a dictionary if the request is successful,
            otherwise None.
        :rtype: Optional[Dict[Any, Any]]
        """
        url = f"{self.base_url}/{rest_context}/ontologies/{urllib.parse.quote(record_id, safe='')}"
        return self._make_request(url, "GET")

    def entity_search(self, query: str, catalog_id: str = default_catalogs,
                      offset: int = 0, limit: int = 100, sort: str = "entityName",
                      ascending: bool = True, types: list[str] | None = None,
                      keywords: list[str] | None = None) -> dict:
        """
        Perform a search operation for entities within the specified catalog. This method
        allows filtering through entities using various criteria such as keywords, types,
        and sorting options. It sends a GET request to the appropriate URL and constructs
        the request parameters dynamically based on the provided arguments.

        :param query: Search text or query string for finding entities.
        :type query: str
        :param catalog_id: ID of the catalog to perform the search in. Uses `default_catalogs`
                           if not specified.
        :type catalog_id: str, optional
        :param offset: Offset index for paginated search results. Defaults to 0.
        :type offset: int, optional
        :param limit: Maximum number of entities to return in the search results. Defaults
                      to 100.
        :type limit: int, optional
        :param sort: Field by which to sort the entities. Defaults to "entityName".
        :type sort: str, optional
        :param ascending: Whether to sort in ascending order. Defaults to True.
        :type ascending: bool, optional
        :param types: List of entity types to filter the search. If None, includes all types by
                      default.
        :type types: list[str], optional
        :param keywords: List of keywords to further filter the entities in the search. If None,
                         includes all entities matching the query regardless of keywords.
        :type keywords: list[str], optional
        :return: A dictionary containing the search results for entities that match the
                 search criteria.
        :rtype: dict
        """
        url = f"{self.base_url}/{rest_context}/catalogs/{urllib.parse.quote(catalog_id, safe='')}/entities"
        params = {
            "offset": offset,
            "limit": limit,
            "searchText": query,
            "sort": sort,
            "ascending": ascending,
        }
        if types:
            params["type"] = ",".join(types)
        if keywords:
            params["keywords"] = ",".join(keywords)
        # make the request with the constructed parameters
        return self._make_request(url, "GET", params)

    def list_records(self, catalog_id: str = default_catalogs, offset: int = 0, limit: int = 100,
                     keywords: list[str] | None = None, search_text: str | None = None,
                     types: list[str] | None = None) -> dict:
        """
        List records from the specified catalog. This method retrieves a list of
        records based on the provided filter criteria such as pagination offset,
        limit, keywords, search text, or record types. It raises an error if the
        specified record types are invalid.

        :param catalog_id: The identifier of the catalog from which records will
                           be retrieved. Defaults to `default_catalogs`.
        :param offset: The starting point from which records are retrieved
                       (for pagination purposes). Defaults to 0.
        :param limit: The maximum number of records to be fetched. Defaults to 100.
        :param keywords: A list of keywords to filter records by. Defaults to None.
        :param search_text: Text to perform a full-text search on records.
                            Defaults to None.
        :param types: A list of record types to filter the results. If provided,
                      it must contain valid types. Defaults to None.
        :return: A dictionary containing the retrieved records, filtered
                 according to the specified criteria.
        :rtype: dict
        :raises ValueError: If the provided `types` are not among the expected
                            valid record types.
        """
        url = f"{self.base_url}/{rest_context}/catalogs/{urllib.parse.quote(catalog_id, safe='')}/records"
        params: dict = {
            "offset": offset,
            "limit": limit,
        }
        if keywords:
            params["keywords"] = ",".join(keywords)
        if search_text:
            params["searchText"] = search_text
        if types:
            params["type"] = ",".join(types)
        return self._make_request(url, "GET", params)

    def get_shapes_graph(self, record_id: str, branch_id: str | None = None, commit_id: str | None = None,
                         rdf_format: str = "turtle"):
        """
        Fetches the shapes graph associated with the specified record.

        This method communicates with a REST service to retrieve the shapes graph
        for a specific record. Optionally, it allows filtering by branch ID, commit ID,
        and specifying the preferred RDF format for the response data.

        :param record_id: The unique identifier of the record for which the shapes
            graph is being fetched.
        :type record_id: str
        :param branch_id: The identifier of the specific branch to fetch the shapes
            graph from. Defaults to None.
        :type branch_id: str | None
        :param commit_id: The commit ID for which the shapes graph should be fetched.
            Defaults to None.
        :type commit_id: str | None
        :param rdf_format: The format in which the RDF data should be returned.
            Defaults to "turtle".
        :type rdf_format: str
        :return: The response of the HTTP GET request, typically containing the shapes
            graph data in the specified format.
        :rtype: Any
        """
        url = f"{self.base_url}/{rest_context}/shapes-graphs/{urllib.parse.quote(record_id, safe='')}"
        params: dict = {}
        if branch_id:
            params["branchId"] = branch_id
        if commit_id:
            params["commitId"] = commit_id
        if rdf_format:
            params["rdfFormat"] = rdf_format
        return self._make_request(url, "GET", params)

    def create_ontology(self, jsonld: str, title: str, description: str, markdown_description: str | None = None,
                        keywords: list[str] | None = None):
        """
        Creates an ontology by sending a POST request to the specified endpoint with the provided
        details including title, description, markdown description, and keywords. The request data
        is constructed and sent via the `_make_request` method while maintaining the relevant API standards.

        :param jsonld: A JSON-LD string payload that contains the ontology data.
        :param title: The title for the ontology.
        :param description: A brief description of the ontology.
        :param markdown_description: Optional; a rich-text description of the ontology in markdown format.
        :param keywords: Optional; a list of keywords associated with the ontology.
        :return: The response object from the `_make_request`, containing the server's response
            to the request.
        """
        url: str = f"{self.base_url}/{rest_context}/ontologies"
        params: dict = {
            "title": title,
            "description": description
        }
        if markdown_description:
            params["markdown"] = markdown_description
        if keywords:
            params["keywords"] = ",".join(keywords)
        return self._make_request(url, "POST", params)

    def _make_request(self, url: str, method: str, params: dict = None) -> Optional[Dict[Any, Any]]:
        """
        Sends an HTTP request and processes the response.

        This method performs an HTTP request using the given URL and HTTP method. It can
        accept optional parameters to include as part of the request. The request uses
        basic authentication credentials and may optionally skip certificate verification
        based on the session configuration. It handles various response scenarios, including
        HTTP errors, empty responses, and unexpected or invalid response formats. If the
        response is JSON, it attempts to parse and return it.

        :param url:
            The target URL for the HTTP request.
        :param method:
            The HTTP method to use (e.g., 'GET', 'POST', etc.).
        :param params:
            Optional dictionary of query parameters to be included in the request. Defaults to None.
        :return:
            A dictionary containing the parsed JSON response, or None if the request failed
            or the response was not a valid JSON.
        """
        try:
            response = requests.request(method, url,
                                        params=params,
                                        auth=(self.username, self.password),
                                        verify=not self.ignore_cert)
            # Check if request was successful
            if not response.ok:
                print(f"HTTP Error {response.status_code}: {response.reason}")
                print(f"Response content: {response.text[:500]}...")
                return None

            # Check if response has content
            if not response.text.strip():
                print("Warning: Empty response received")
                return {}

            # Check if response is JSON
            content_type = response.headers.get('content-type', '').lower()
            if 'application/json' not in content_type:
                print(f"Warning: Response is not JSON. Content-Type: {content_type}")
                print(f"Response content: {response.text[:500]}...")
                return None
            else:
                # Parse JSON
                try:
                    return response.json()
                except json.JSONDecodeError as e:
                    print(f"JSON decode error: {e}")
                    print(f"Response content: {response.text[:500]}...")
                    return None

        except RequestException as e:
            print(f"Request failed: {e}")
            return None
