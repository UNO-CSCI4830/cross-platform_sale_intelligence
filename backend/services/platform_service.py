from datetime import datetime, timedelta
from fastapi import HTTPException
from core.security import encrypt_token, decrypt_token
import httpx
import os

from db.models import LinkedAccount

PLATFORM_CONFIGS = {
    "ebay": {
        "auth_url": "https://auth.ebay.com/oauth2/authorize", #User's browser goes here to login
        "token_url": "https://api.ebay.com/identity/v1/oauth2/token", #Backend server goes here 
        "client_id": os.getenv("EBAY_CLIENT_ID"),
        "client_secret": os.getenv("EBAY_CLIENT_SECRET"),
    }
    # we'll add depop later once ebay is ready to go
}

async def get_valid_token(user_id: int, platform: str, db) -> str:
    """Get a valid access token for a user's linked platform, refreshing if needed."""
    account = db.query(LinkedAccount).filter_by(user_id=user_id, platform=platform).first()

    if not account: #If no account linked yet
        raise HTTPException(status_code=404, detail=f"No linked {platform} account found")
    # Refresh if token expires within 5 minutes
    if account.token_expiry and account.token_expiry < datetime.utcnow() + timedelta(minutes=5):
        #token expring, get a new one
        new_tokens = await _refresh_token(platform, decrypt_token(account.refresh_token))
        #store new access token, already encrypted by _refresh_token
        account.access_token = new_tokens["access_token"]
        # only update if we get a new refresh token (ebay only), also kind of irrelevant since a refresh token lasts around 18 months
        if new_tokens["refresh_token"]:
            account.refresh_token = new_tokens["refresh_token"]
        account.token_expiry = new_tokens["token_expiry"]
        # write all changes to db
        db.commit()
    return decrypt_token(account.access_token)


async def save_linked_account(user_id: int, platform: str, tokens: dict, db):
    """Create or update a linked account after OAuth callback."""
    account = db.query(LinkedAccount).filter_by(user_id=user_id, platform=platform).first()

    if not account: # If no account found, make one
        account = LinkedAccount(user_id=user_id, platform=platform)

    account.access_token = encrypt_token(tokens["access_token"])
    account.refresh_token = encrypt_token(tokens.get("refresh_token"))
    account.token_expiry = tokens.get("expiry")
    db.add(account)
    db.commit()


async def _refresh_token(platform: str, refresh_token: str) -> str:
    """If token is about to expire, get a new one"""
    config = PLATFORM_CONFIGS.get(platform)
    if not config:
        #if platform is not in PLATFORM_CONFIG we don't support it yet (i.e. Depop)
        raise HTTPException(status_code=400, detail=f"Unsupported platform: {platform}")

    async with httpx.AsyncClient() as client: # Create a connection to eBay API to get a new token
        response = await client.post(
            config["token_url"], #Ebay's token endpoint
            data={
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
            },
            #our authentication to eBay (the app not the user)
            auth=(config["client_id"], config["client_secret"]) #configs pulled from platform_configs
        )
        #raise an execption if ebay returns an error
        response.raise_for_status()
        data = response.json()
        return {
            #encrypt before returning and storing
            "access_token": encrypt_token(data["access_token"]),
            #eBay decides when/if we get a new refresh token
            "refresh_token": encrypt_token(data["refresh_token"]) if data.get("refresh_token") else None,
            #token lasts 2 hours before needing a new one
            "token_expiry": datetime.utcnow() + timedelta(seconds=data.get("expires_in", 7200))
        }