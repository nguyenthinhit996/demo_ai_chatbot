from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://myuser:mypassword@localhost:5432/chatbot"
    database_url_normal: str = "postgresql://myuser:mypassword@localhost:5432/chatbot?sslmode=disable"
    secret_key: str = "your-secret-key"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    openai_api_key: str
    langchain_api_key: str
    langchain_tracing_v2: bool
    langchain_endpoint: str
    langchain_project: str
    remaining_last_message: int = 6
    length_of_messages_to_summarize: int = 10
    external_api_endpoint: str
    postgres_db: str
    postgres_user: str
    postgres_password: str
    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()