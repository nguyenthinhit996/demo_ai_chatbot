import logging
import httpx

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

EXTERNAL_API_ENDPOINT = os.getenv("EXTERNAL_API_ENDPOINT")

print(f"API EXTERNAL_API_ENDPOINT: {EXTERNAL_API_ENDPOINT}")

async def graphql_request(query: str, variables: dict = None, token: str = None, origin: str = None) -> dict:
    """
    Makes a GraphQL API request.

    :param endpoint: The URL of the GraphQL server.
    :param query: The GraphQL query or mutation string.
    :param variables: A dictionary of variables for the query, defaults to None.
    :param headers: A dictionary of headers for the request, defaults to None.
    :return: A dictionary containing the response JSON.
    """
    endpoint = EXTERNAL_API_ENDPOINT
    headers = {
        "token": token,
        "Content-Type": "application/json",
        "origin" : origin
    }
    logging.debug(f"headers status code: {headers}")
    payload = {
        "query": query,
        "variables": variables or {}
    }
    timeout = 20.0  # Define a timeout value in seconds
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(endpoint, json=payload, headers=headers, timeout=timeout)
            logging.debug(f"Response status code: {response}")
            response.raise_for_status()
            data = response.json()
            if "errors" in data:
                logging.error(f"GraphQL errors: {data['errors']}")
                raise Exception(f"GraphQL errors: {data['errors']}")
            return data["data"]
        except httpx.RequestError as req_err:
            logging.error(f"Request error: {req_err}")
        except httpx.HTTPStatusError as http_err:
            logging.error(f"HTTP error: {http_err.response.status_code} - {http_err.response.text}")
        except Exception as err:
            logging.error(f"Unexpected error: {err}")
        return None
