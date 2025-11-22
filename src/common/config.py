from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    LOG_LEVEL: str = "INFO"
    PYTHON_ENV: str = "PROD"
    POSTGRES_URL: str
    SUPABASE_PUBLISHABLE_KEY: str
    SUPABASE_PROJECT_URL: str
    SUPABASE_PROJECT_REF: str
    SUPABASE_JWT_AUDIENCE: str
    SUPABASE_SERVICE_ROLE_KEY: str
    S3_REGION: str
    S3_ACCESS_KEY_ID: str
    S3_SECRET_ACCESS_KEY_ID: str
    S3_ENDPOINT: str
    SUPABASE_DEV_USERNAME: str
    SUPABASE_DEV_PASSWORD: str
    GOOGLE_PLACES_API_KEY: str
    RESEND_API_KEY: str
    RESEND_FROM_EMAIL: str = "admin@monkeybun.co"
    RESEND_FROM_NAME: str = "Monkeybun"
    RESEND_ENABLED: bool = True

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)


settings = AppSettings()
