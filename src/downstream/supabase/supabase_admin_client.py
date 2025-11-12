from uuid import UUID

from supabase import Client, create_client

from src.common.config import settings
from src.common.logger import logger


class SupabaseAdminClient:
    def __init__(self):
        self.client: Client = create_client(
            settings.SUPABASE_PROJECT_URL,
            settings.SUPABASE_SERVICE_ROLE_KEY,
        )

    def get_user(self, user_id: UUID):
        try:
            response = self.client.auth.admin.get_user_by_id(str(user_id))
            if response.user:
                return response.user
            return None
        except Exception as e:
            logger.error(f"Failed to get user for {user_id}: {e}")
            return None
