from authlib.integrations.starlette_client import OAuth
from starlette.requests import Request

from app.core.config import settings


oauth = OAuth()

oauth.register(
    name="google",
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={
        "scope": "openid email profile",
        "prompt": "select_account",
    },
)


async def get_google_oauth_client():
    return oauth.google


async def redirect_to_google(request: Request) -> str:
    redirect_uri = settings.GOOGLE_REDIRECT_URI
    return await oauth.google.authorize_redirect(request, redirect_uri)


async def handle_google_callback(request: Request) -> dict:
    token = await oauth.google.authorize_access_token(request)
    user_info = await oauth.google.parse_id_token(request, token)
    return user_info


def get_google_user_info(user_info: dict) -> dict:
    return {
        "email": user_info.get("email"),
        "google_id": user_info.get("sub"),
        "name": user_info.get("name"),
        "picture": user_info.get("picture"),
        "email_verified": user_info.get("email_verified", False),
    }