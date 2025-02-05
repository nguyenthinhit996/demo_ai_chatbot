from fastapi import FastAPI
from psycopg_pool import AsyncConnectionPool
from app.core import config
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from app.chatbot.core.graph import ChatBotGraph

# Create a settings instance
settings = config.Settings()

# Define connection pool settings
connection_kwargs = {
    "autocommit": True,
    "prepare_threshold": 0,
}

def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application with controlled initialization and shutdown.
    """
    app = FastAPI(title="Controlled Lifecycle App", version="1.0.0")
    
    @app.on_event("startup")
    async def startup():
        print("Starting application.")
        try:
            # Initialize the connection pool
            app.state.pool = AsyncConnectionPool(
                conninfo=settings.database_url_normal,
                max_size=20,
                kwargs=connection_kwargs,
            )
            
            # Initialize the checkpointer and graph
            app.state.checkpointer = AsyncPostgresSaver(app.state.pool)
            app.state.graph = ChatBotGraph(app.state.checkpointer).graph

            mock_requests = [
                {"request_id": "1", "name": "Alice", "date": "2025-01-04", "status": "Pending"},
                {"request_id": "2", "name": "Bob", "date": "2025-01-03", "status": "Completed"},
                {"request_id": "3", "name": "Charlie", "date": "2025-01-02", "status": "In Progress"},
                {"request_id": "4", "name": "Alice", "date": "2025-01-01", "status": "Pending"},
                {"request_id": "5", "name": "Bob", "date": "2024-12-31", "status": "Completed"},
            ]

            mock_templates = [
                {
                    "id": "1",
                    "title": "Pet Application",
                    "description": "Useful For residents to submit when they get a new pet."
                },
                {
                    "id": "2",
                    "title": "Home Maintenance",
                    "description": "Useful For residents to request repairs when something is broken at home."
                },
                {
                    "id": "3",
                    "title": "Planting New Trees",
                    "description": "Useful For residents to request planting new trees."
                },
                {
                    "id": "4",
                    "title": "Public Area Maintenance",
                    "description": "Useful For residents to request maintenance of public facilities."
                }
            ]

            mock_template_details = [
                {
                    "id": "1",
                    "title": "Pet Application",
                    "description": "Useful for residents to submit when they get a new pet.",
                    "currentFormVersion": {
                        "items": [
                            {
                                "id": "d58a63e8-58ce-4c3e-9121-8e03b91cb274",
                                "index": 0,
                                "type": "SHORT_TEXT",
                                "title": "Summary"
                            },
                            {
                                "id": "f1b2d3a4-12e3-45f6-a789-123456789abc",
                                "index": 1,
                                "type": "SHORT_TEXT",
                                "title": "Name",
                                "description": "Enter the pet's name.",
                                "require": "true"
                            },
                            {
                                "id": "a2b3c4d5-e6f7-8901-2345-67890abcdef",
                                "index": 2,
                                "type": "DATE",
                                "title": "Date of Adoption",
                                "description": "Provide the adoption date.",
                                "require": "true"
                            },
                            {
                                "id": "9f8e7d6c-5b4a-3c21-d098-7654321fedcb",
                                "index": 3,
                                "type": "LONG_TEXT",
                                "title": "Additional Details",
                                "description": "Include any extra information about the pet."
                            }
                        ]
                    }
                },
                {
                    "id": "2",
                    "title": "Home Maintenance",
                    "description": "Useful for residents to request repairs when something is broken at home.",
                    "currentFormVersion": {
                        "items": [
                            {
                                "id": "abc12345-6789-0abc-def1-234567890abc",
                                "index": 0,
                                "type": "SHORT_TEXT",
                                "title": "Issue Summary"
                            },
                            {
                                "id": "def67890-1234-5678-9abc-abcdef123456",
                                "index": 1,
                                "type": "LONG_TEXT",
                                "title": "Description of Problem",
                                "description": "Explain the issue in detail.",
                            },
                            {
                                "id": "12345abc-6789-def0-1234-56789abcdef0",
                                "index": 2,
                                "type": "MULTIPLE_CHOICE",
                                "title": "Type of Maintenance",
                                "options": ["Plumbing", "Electrical", "Carpentry", "Other"]
                            },
                            {
                                "id": "0fedcba9-8765-4321-0abc-9876543210ab",
                                "index": 3,
                                "type": "DATE",
                                "title": "Preferred Maintenance Date",
                                "description": "Select the date you prefer the repair to happen.",
                                "require": "true"
                            }
                        ]
                    }
                },
                {
                    "id": "3",
                    "title": "Planting New Trees",
                    "description": "Useful for residents to request planting new trees.",
                    "currentFormVersion": {
                        "items": [
                            {
                                "id": "aaa11111-2222-3333-4444-555555555555",
                                "index": 0,
                                "type": "SHORT_TEXT",
                                "title": "Tree Species",
                                "description": "Enter the name of the tree species."
                            },
                            {
                                "id": "bbb22222-3333-4444-5555-666666666666",
                                "index": 1,
                                "type": "NUMBER",
                                "title": "Number of Trees",
                                "description": "Specify how many trees you want to plant.",
                                 "require": "true"
                            },
                            {
                                "id": "ccc33333-4444-5555-6666-777777777777",
                                "index": 2,
                                "type": "LOCATION",
                                "title": "Planting Location",
                                "description": "Provide the location for planting.",
                                 "require": "true"
                            },
                            {
                                "id": "ddd44444-5555-6666-7777-888888888888",
                                "index": 3,
                                "type": "LONG_TEXT",
                                "title": "Additional Notes",
                                "description": "Any other details or requests."
                            }
                        ]
                    }
                },
                {
                    "id": "4",
                    "title": "Public Area Maintenance",
                    "description": "Useful for residents to request maintenance of public facilities.",
                    "currentFormVersion": {
                        "items": [
                            {
                                "id": "eee55555-6666-7777-8888-999999999999",
                                "index": 0,
                                "type": "SHORT_TEXT",
                                "title": "Facility Name",
                                "require": "true"
                            },
                            {
                                "id": "fff66666-7777-8888-9999-000000000000",
                                "index": 1,
                                "type": "LONG_TEXT",
                                "title": "Issue Description",
                                "description": "Describe the problem with the facility."
                            },
                            {
                                "id": "ggg77777-8888-9999-0000-111111111111",
                                "index": 2,
                                "type": "FILE_UPLOAD",
                                "title": "Attach Photos",
                                "description": "Upload photos of the issue (optional)."
                            },
                            {
                                "id": "hhh88888-9999-0000-1111-222222222222",
                                "index": 3,
                                "type": "DATE",
                                "title": "Date of Observation",
                                "description": "Specify when you noticed the issue.",
                                "require": "true"
                            }
                        ]
                    }
                }
            ]



            app.state.mock_requests = mock_requests
            app.state.mock_templates = mock_templates
            app.state.mock_template_details = mock_template_details

            # Setup the checkpointer
            await app.state.checkpointer.setup()
            print("ChatBotGraph initialized successfully.")
        except Exception as e:
            print(f"Error during startup: {e}")
            raise
    
    @app.on_event("shutdown")
    async def shutdown():
        print("Shutting down application.")
        try:
            # Close checkpointer and pool
            if hasattr(app.state, "checkpointer") and app.state.checkpointer:
                await app.state.checkpointer.close()
            if hasattr(app.state, "pool") and app.state.pool:
                await app.state.pool.close()
            print("Resources cleaned up successfully.")
        except Exception as e:
            print(f"Error during shutdown: {e}")
            raise

    return app
