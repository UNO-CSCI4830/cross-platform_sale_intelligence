from datetime import datetime, timedelta
from fastapi import HTTPException
from backend.core.security import encrypt_token, decrypt_token
import httpx
import xml.etree.ElementTree as ET
import os
import requests
from fastapi.concurrency import run_in_threadpool

from backend.db.models import LinkedAccount, ListingSnapshot

PLATFORM_CONFIGS = {
    "ebay": {
        "auth_url": "https://auth.sandbox.ebay.com/oauth2/authorize", #User's browser goes here to login
        "token_url": "https://api.sandbox.ebay.com/identity/v1/oauth2/token", #Backend server goes here 
        "client_id": os.getenv("EBAY_CLIENT_ID"),
        "scope": "https://api.ebay.com/oauth/api_scope/sell.inventory", #Tells ebay we want to access listings
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

async def fetch_and_save_listings(user_id: int, platform: str, db):
    """
    Fetches seller's listings from the platform and saves to listing_snapshot.
    Called on first account link and on manual refresh.
    """
    # get a valid decrypted token for this user
    token = await get_valid_token(user_id, platform, db)

    if platform == "ebay":
        await _mock_ebay_listings(user_id, token, db) #should be _fetch_ebay_listings(), but we're gonna hardcode listings for now

async def _mock_ebay_listings(user_id: int, token, db):
    """Temporary mock listings for prototype demo - replace with real eBay fetch after presentation"""
    mock_listings = [
        {
            "platform_listing_id": "mock_001",
            "title": "Nike Air Max 90 - Size 10",
            "price": 120.00,
            "quantity": 1,
            "condition": "Used",
            "status": "active",
            "item_url": "https://www.ebay.com/itm/mock_001",
            "image_url": None
        },
        {
            "platform_listing_id": "mock_002",
            "title": "Vintage Denim Jacket - Medium",
            "price": 45.00,
            "quantity": 1,
            "condition": "Good",
            "status": "active",
            "item_url": "https://www.ebay.com/itm/mock_002",
            "image_url": None
        },
        {
            "platform_listing_id": "mock_003",
            "title": "iPhone 12 Case",
            "price": 12.99,
            "quantity": 3,
            "condition": "New",
            "status": "active",
            "item_url": "https://www.ebay.com/itm/mock_003",
            "image_url": None
        }
    ]

    for listing in mock_listings: #uses platform_listing_id to ensure duplicates aren't made when we refresh
        existing = db.query(ListingSnapshot).filter_by(
            user_id=user_id,
            platform="ebay",
            platform_listing_id=listing["platform_listing_id"]
        ).first()

        if not existing: #create a new row if listing is new (not really relevant here since its hardcoded)
            existing = ListingSnapshot(
                user_id=user_id,
                platform="ebay",
                platform_listing_id=listing["platform_listing_id"]
            )

        existing.title = listing["title"]
        existing.price = listing["price"]
        existing.quantity = listing["quantity"]
        existing.condition = listing["condition"]
        existing.status = listing["status"]
        existing.item_url = listing["item_url"]
        existing.image_url = listing["image_url"]
        existing.captured_at = datetime.utcnow()

        db.add(existing)

    db.commit()
    print(f"SAVED {len(mock_listings)} mock listings to DB")
'''
async def _fetch_ebay_listings(user_id: int, token: str, db):
    url = "https://api.sandbox.ebay.com/ws/api.dll"
    headers = {
        "X-EBAY-API-COMPATIBILITY-LEVEL": "1207",
        "X-EBAY-API-CALL-NAME": "GetMyeBaySelling",
        "X-EBAY-API-SITEID": "0",
        "Content-Type": "text/xml"
    }
    xml_request = """<?xml version="1.0" encoding="utf-8"?>
<GetMyeBaySellingRequest xmlns="urn:ebay:apis:eBLBaseComponents">
    <RequesterCredentials>
        <eBayAuthToken>{token}</eBayAuthToken>
    </RequesterCredentials>
    <ActiveList>
        <Include>true</Include>
        <Pagination>
            <EntriesPerPage>100</EntriesPerPage>
            <PageNumber>1</PageNumber>
        </Pagination>
    </ActiveList>
</GetMyeBaySellingRequest>""".format(token=token)

    # run synchronous requests in thread pool to avoid blocking async
    def make_request():
        return requests.post(url, data=xml_request, headers=headers)
    
    response = await run_in_threadpool(make_request)
    print(f"STATUS: {response.status_code}")
    print(f"RESPONSE: {response.text}")

    root = ET.fromstring(response.text)
    ns = {"ns": "urn:ebay:apis:eBLBaseComponents"}
    items = root.findall(".//ns:ActiveList/ns:ItemArray/ns:Item", ns)
    print(f"ITEMS FOUND: {len(items)}")

    for item in items:
        def get(tag):
            el = item.find(f"ns:{tag}", ns)
            return el.text if el is not None else None

        item_id = get("ItemID")
        title = get("Title")
        price = get("BuyItNowPrice") or get("StartPrice")
        quantity = get("Quantity")
        condition = get("ConditionDisplayName")
        image_url = item.find(".//ns:GalleryURL", ns)
        image_url = image_url.text if image_url is not None else None
        item_url = f"https://www.sandbox.ebay.com/itm/{item_id}"

        existing = db.query(ListingSnapshot).filter_by(
            user_id=user_id,
            platform="ebay",
            platform_listing_id=item_id
        ).first()

        if not existing:
            existing = ListingSnapshot(
                user_id=user_id,
                platform="ebay",
                platform_listing_id=item_id
            )

        existing.title = title
        existing.price = float(price) if price else None
        existing.quantity = int(quantity) if quantity else None
        existing.condition = condition
        existing.image_url = image_url
        existing.item_url = item_url
        existing.status = "active"
        existing.captured_at = datetime.utcnow()

        db.add(existing)

    db.commit()
    print(f"SAVED {len(items)} listings to DB")
    '''
'''
This code works but Ebay's API refuses to return anything:
STATUS: 200
RESPONSE: <?xml version='1.0' encoding='UTF-8'?><GetMyeBaySellingResponse xmlns="urn:ebay:apis:eBLBaseComponents"><Timestamp>2026-04-05T17:37:55.694Z</Timestamp><Ack>Success</Ack><Version>1271</Version></GetMyeBaySellingResponse>
ITEMS FOUND: 0
SAVED 0 listings to DB
'''

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