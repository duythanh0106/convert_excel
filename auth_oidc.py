# app/auth.py

from fastapi import HTTPException, Request, Depends
from fastapi.responses import RedirectResponse, HTMLResponse
from authlib.integrations.starlette_client import OAuth
from starlette.middleware.sessions import SessionMiddleware
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

OIDC_CLIENT_ID = os.getenv("OIDC_CLIENT_ID")
OIDC_CLIENT_SECRET = os.getenv("OIDC_CLIENT_SECRET")
OIDC_DISCOVERY_URL = os.getenv("OIDC_DISCOVERY_URL")
SECRET_KEY = os.getenv("SECRET_KEY", "change-this-secret")

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

oauth = OAuth()

if GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET:
    oauth.register(
        name="google",
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={"scope": "openid email profile"},
    )


# ---------- Helpers ----------

def get_current_user(request: Request):
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401)
    return user


# ---------- Pages ----------
TEMPLATES_DIR = BASE_DIR / "templates"

async def login_page(request: Request):
    login_file = TEMPLATES_DIR / "login.html"
    return HTMLResponse(login_file.read_text(encoding="utf-8"))


# ---------- Auth flows ----------

async def login_google(request: Request):
    if not GOOGLE_CLIENT_ID:
        raise HTTPException(400, "Google OAuth not configured")

    redirect_uri = str(request.url_for("auth_callback_google"))
    return await oauth.google.authorize_redirect(request, redirect_uri)


async def auth_callback_google(request: Request):
    try:
        token = await oauth.google.authorize_access_token(request)
        user_info = token.get("userinfo") or await oauth.google.parse_id_token(request, token)

        request.session["user"] = {
            "sub": user_info["sub"],
            "email": user_info.get("email"),
            "name": user_info.get("name"),
            "picture": user_info.get("picture"),
            "access_token": token["access_token"],
            "id_token": token.get("id_token"),
        }

        return RedirectResponse(url="/")

    except Exception:
        return RedirectResponse(url="/login?error=auth_failed")


async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login")
