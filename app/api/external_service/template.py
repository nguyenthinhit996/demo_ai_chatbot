from app.api.external_service import graphql_request
 
 
async def get_all_templates(token: str, origin: str):
    query = """
         query NewRequestDialog_TemplateList($filterOptions: FormFilterOptions!) {
            getForms(paginationOptions: {limit: 1000, pageNum: 0}, filterOptions: $filterOptions) {
                records {
                    id
                    title
                    description
                }
            }
        }
    """
    variables = {
        "filterOptions": {
            "status": "ACTIVE"
        }
    }
 
    response = await graphql_request(query, variables, token, origin)
    print(f"get_all_templates: {response}")
    get_forms = response.get("getForms")  # Access 'getForms' key
    if get_forms:
        records = get_forms.get("records")  # Access 'edges' inside 'getForms'
        return records
    return None
 
async def get_detail_template(idForm : str, token: str, origin: str):
    query = """
        query NewRequest_GetForm($id: ID!) {
        getForm(id: $id) {
            id
            currentFormVersion {
            id
            ...FormItems
            }
        }
        }
 
        fragment FormShortTextItem on ShortText {
        id
        index
        type
        title
        description
        isHidedFromSiteRequest
        showAsSummary
        validators {
            isRequired
           
        }
       
        }
 
        fragment FormLongTextItem on LongText {
        id
        index
        type
        title
        description
        isHidedFromSiteRequest
        validators {
            isRequired
           
        }
       
        }
 
        fragment FormNumberItem on Number {
        id
        index
        type
        title
        description
        isHidedFromSiteRequest
        validators {
            minNumber
            maxNumber
            isRequired
           
        }
       
        }
 
        fragment FormSectionHeadingItem on SectionHeading {
        id
        index
        type
        title
        description
       
        }
 
        fragment FormImageUploadItem on ImageUpload {
        id
        index
        type
        title
        description
        isHidedFromSiteRequest
        validators {
            isRequired
           
        }
       
        }
 
        fragment FormFileUploadItem on FileUpload {
        id
        index
        type
        title
        description
        isHidedFromSiteRequest
        validators {
            isRequired
           
        }
       
        }
 
        fragment FormSingleSelectItem on SingleSelect {
        id
        index
        type
        title
        description
        isHidedFromSiteRequest
        options {
            title
            index
            id
           
        }
        validators {
            isRequired
           
        }
       
        }
 
        fragment FormMultiSelectItem on MultiSelect {
        id
        index
        type
        title
        description
        isHidedFromSiteRequest
        options {
            title
            index
            id
           
        }
        validators {
            isRequired
           
        }
       
        }
 
        fragment FormCheckboxItem on CheckBox {
        id
        index
        type
        title
        description
        isHidedFromSiteRequest
        validators {
            isRequiredTrue
           
        }
       
        }
 
        fragment FormDateItem on DateItem {
        id
        index
        type
        title
        description
        isHidedFromSiteRequest
        validators {
            isRequired
           
        }
       
        }
 
        fragment FormSummaryItem on Summary {
        id
        index
        type
        title
        isVisibleFromSite
       
        }
 
        fragment FormItems on FormVersion {
        items {
            ...FormShortTextItem
            ...FormLongTextItem
            ...FormNumberItem
            ...FormSectionHeadingItem
            ...FormImageUploadItem
            ...FormFileUploadItem
            ...FormSingleSelectItem
            ...FormMultiSelectItem
            ...FormCheckboxItem
            ...FormDateItem
            ...FormSummaryItem
           
        }
       
        }
    """
    variables = {
        "id": idForm
    }
 
    response = await graphql_request(query, variables, token, origin)
    print(f"get_detail_template: {response}")
    getForm = response.get("getForm")  # Access 'getForms' key
    if getForm:
        currentFormVersion = getForm.get("currentFormVersion")  # Access 'edges' inside 'getForms'
        return currentFormVersion
    return None