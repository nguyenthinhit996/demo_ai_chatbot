import logging
import httpx

async def graphql_request(query: str, variables: dict = None) -> dict:
    """
    Makes a GraphQL API request.

    :param endpoint: The URL of the GraphQL server.
    :param query: The GraphQL query or mutation string.
    :param variables: A dictionary of variables for the query, defaults to None.
    :param headers: A dictionary of headers for the request, defaults to None.
    :return: A dictionary containing the response JSON.
    """
    endpoint = "http://localhost:4000/admin"
    headers = {
        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IjYzMDZiOThhMCJ9.eyJhdWQiOiJjYjc3YjNhYS05YjM4LTRmYzYtODYyNi03NTZkMjJjMTVmNmMiLCJleHAiOjE3MzkzMzM3OTksImlhdCI6MTczODcyODk5OSwiaXNzIjoiYWNtZS5jb20iLCJzdWIiOiIzNzgwYzBlOS0zYzdkLTQxNjMtYWRjYi1jMGI5NzY0NGM3NmYiLCJqdGkiOiI5ZWRkMzE4Ny1lMTM4LTQ4ODEtOTliYy02Zjg3NWRlYmZkYzAiLCJhdXRoZW50aWNhdGlvblR5cGUiOiJQQVNTV09SRCIsImFwcGxpY2F0aW9uSWQiOiJjYjc3YjNhYS05YjM4LTRmYzYtODYyNi03NTZkMjJjMTVmNmMiLCJyb2xlcyI6W10sImF1dGhfdGltZSI6MTczODcyODk5OSwidGlkIjoiNDA3YjNkYmQtZDVlNS00ZDZlLTkzNGQtYzEwMzdlMTMxOTQ2In0.xwATa6XOifC_9lULakeXxJ6gQWxwANXaB3p0QmCRPa8",
        "Content-Type": "application/json",
        "origin" : "localhost"
    }
    logging.debug(f"headers status code: {headers}")
    payload = {
        "query": query,
        "variables": variables or {}
    }
    timeout = 20.0  # Define a timeout value in seconds

    # try:
    #     response = httpx.post(endpoint, json=payload, headers=headers)
    #     response.raise_for_status()  # Raise exception for HTTP errors
    #     data = response.json()
    #     if "errors" in data:
    #         raise Exception(f"GraphQL errors: {data['errors']}")
    #     return data["data"]
    # except httpx.HTTPError as http_err:
    #     print(f"HTTP error occurred: {http_err}")
    # except Exception as err:
    #     print(f"Other error occurred: {err}")
    # return None
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
