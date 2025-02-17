from smolagents import Tool, tool
from typing import List, Dict, Any, Union, Optional, Tuple, Type
from pathlib import Path

@tool
def initialize_tavily_client(tavily_api_key: str) -> Any:
    """
    Initializes the Tavily API client.

    This function attempts to initialize the TavilyClient using the provided API key.
    It handles potential import errors and returns the Tavily client object if successful.

    Args:
        tavily_api_key: The API key for Tavily.

    Returns:
        The TavilyClient object if initialization is successful, otherwise returns an error message string.
    """
    try:
        from tavily import TavilyClient
    except ImportError:
        return "Error: Failed to import TavilyClient from tavily. Please make sure it is installed. You can install it with `pip install tavily-python`."

    try:
        tavily_client = TavilyClient(api_key=tavily_api_key) # Use the provided API key
        return tavily_client
    except Exception as e:
        return f"Error: Failed to initialize Tavily client. Reason: {e}"


@tool
def get_tavily_search_results(query: str) -> str:
    """
    Searches Tavily for the given query and returns the search results.

    This function uses the Tavily API to perform a search based on the provided query.
    It initializes the Tavily client internally using a hardcoded API key (replace with your actual API key for real use).

    Args:
        query: The search query string.

    Returns:
        The search results from Tavily as a string, or an error message string if the search fails.
    """
    try:
        tavily_client = initialize_tavily_client("tvly-YOUR_API_KEY") # You should ideally pass the API key as argument or environment variable for better security
        if isinstance(tavily_client, str) and tavily_client.startswith("Error:"): # Check if initialization failed and returned an error string
            return tavily_client # Return the error message from initialization
        search_results = tavily_client.search(query)
        return f"Successfully retrieved Tavily search results for query '{query}'. Results: {search_results}"
    except Exception as e:
        return f"Error: Failed to get Tavily search results for query '{query}'. Reason: {e}"


@tool
def extract_url_tavily(url: str) -> str:
    """
    Extracts information from a given URL using Tavily.

    This function uses the Tavily API to extract content from the provided URL.
    It initializes the Tavily client internally using a hardcoded API key (replace with your actual API key for real use).

    Args:
        url: The URL to extract information from.

    Returns:
        The extracted information from the URL as a string, or an error message string if extraction fails.
    """
    try:
        tavily_client = initialize_tavily_client("tvly-YOUR_API_KEY") # You should ideally pass the API key as argument or environment variable for better security
        if isinstance(tavily_client, str) and tavily_client.startswith("Error:"): # Check if initialization failed and returned an error string
            return tavily_client # Return the error message from initialization
        extracted_info = tavily_client.extract(url=url) # Pass url as keyword argument
        return f"Successfully extracted information from URL '{url}' using Tavily. Extracted Info: {extracted_info}"
    except Exception as e:
        return f"Error: Failed to extract information from URL '{url}' using Tavily. Reason: {e}"
    

