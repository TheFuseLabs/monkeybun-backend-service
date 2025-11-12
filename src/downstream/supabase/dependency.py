from src.downstream.supabase.supabase_admin_client import SupabaseAdminClient

supabase_admin_client = SupabaseAdminClient()


def get_supabase_admin_client() -> SupabaseAdminClient:
    return supabase_admin_client
