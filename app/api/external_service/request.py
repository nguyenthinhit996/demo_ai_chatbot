from app.api.external_service import graphql_request

async def create_request(itemsValue, residentAppUserId, formVersionId, siteId, token, origin):
    query = """
        mutation CreateSubmissionNew($input: SubmissionInput!) {
            createSubmission(input: $input) {
                id
            }
        }
    """
    dataItemsValue = [item.dict() for item in itemsValue]
    variables = {
        "input": {
            "itemsValue": dataItemsValue,
            "requestorId": residentAppUserId,
            "requestorType": "siteResident",
            "formVersionId": formVersionId,
            "siteId": siteId,
            "isFromScratch": False,
            "isInsuranceClaim": False,
            "isVisibleToCommunity": False,
            "shareToCommittee": False
        }
    }

    try:
        # Send the GraphQL request
        response = await graphql_request(query, variables, token, origin)
        
        # Log the full response for debugging
        print(f"create_request: {response}")
        
        # Safely extract the 'createSubmission' field
        createSubmission = response.get("createSubmission")
        
        if createSubmission:
            # Extract the 'id' field from 'createSubmission'
            id = createSubmission.get("id")
            
            # Check if 'id' exists
            if id:
                print(f"return id: {id}")
                return id
            else:
                print("Error: 'id' not found in 'createSubmission'")
        else:
            print("Error: 'createSubmission' not found in response")
        
        # Return None if id or createSubmission is missing
        print(f" return id: return None ")
        return None
    except Exception as e:
        # Handle unexpected exceptions
        print(f"An error occurred: {e}")
        return None