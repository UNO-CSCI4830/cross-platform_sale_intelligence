from backend.main import app, ListingResponse
import pytest
from pydantic import ValidationError

# Set of valid field values
VALID_DATA = {
    "id": 1,
    "title": "Navy Hoodie",
    "price": 19.99,
    "condition": "Good",
    "platform": "Ebay",
    "status": "active",
    "category": "Clothing",
    "platform_listing_id": "ABC123",
    "image_url": "https://example.com/img.jpg",
    "item_url": "https://example.com/listing",
    "quantity": 1,
}


# Test 1: Valid listing information should work
def test_listing_response_valid():
    listing = ListingResponse(**VALID_DATA)
 
    assert listing.id == 1
    assert listing.title == "Navy Hoodie"
    assert listing.price == 19.99
    assert listing.condition == "Good"
    assert listing.platform == "Ebay"
    assert listing.status == "active"


# Test 2: Price change from string to float should work
def test_listing_response_price_change():
    data = {**VALID_DATA, "price": "29.99"}
    listing = ListingResponse(**data)
 
    assert listing.price == 29.99
    assert isinstance(listing.price, float)


# Test 3: Check for missing a field
def test_listing_response_missing_field():
    data = {k: v for k, v in VALID_DATA.items() if k != "title"}
    with pytest.raises(ValidationError):
        ListingResponse(**data)
 
 
# Test 4: Check for a non-numeric price
def test_listing_response_invalid_price():
    data = {**VALID_DATA, "price": "not_a_number"}
    with pytest.raises(ValidationError):
        ListingResponse(**data)
 
