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
