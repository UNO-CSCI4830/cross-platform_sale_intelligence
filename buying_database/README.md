# Buying Database

This folder contains the PostgreSQL schema for the comps pricing engine.

## Tables

### search_query
Stores user search terms used for marketplace comps.

### listing_snapshot
Stores listing data returned from the eBay Browse API.

---

## Local Database Setup

### 1. Install PostgreSQL

Download PostgreSQL (latest version):

https://www.postgresql.org/download/

Choose your operating system and follow the installer.

During installation:
- Keep the default port (5432)
- Set a password for the `postgres` user
- Leave other settings as default

---

### 2. Open pgAdmin

pgAdmin installs automatically with PostgreSQL.

To open:
- Press Windows key
- Search for **pgAdmin 4**
- Open the application

On first launch:
- Enter the password you set during installation

---

### 3. Create the Database

In pgAdmin:

1. Right-click **Databases**
2. Click **Create → Database**
3. Name it: comps_db

Click Save.

---

### 4. Apply the Schema

1. Select the `comps_db` database
2. Click **Query Tool**
3. Open `schema.sql` from this folder
4. Execute the script

This will create:
- search_query table
- listing_snapshot table
- required indexes

---

### 5. Running Queries


This folder also includes a queries.sql file containing commonly used SQL queries for exploring the database and generating pricing analytics.

To run the queries:
1. Select the comps_db database
2. Click Query Tool
3. Open queries.sql from this folder
4. Execute the script

These queries allow you to:
- View stored search queries
- View listing data returned from the eBay API
- Calculate average market prices
- Generate suggested listing prices
- Estimate shipping weight using USPS guidelines
- Calculate total cost including shipping

---

### 6. Pricing Table


The main analytics query generates a pricing table for each listing.

The table calculates:

current_price — listing price returned from eBay

avg_price — average market price for that search term

suggested_listing_price — average price plus a 15% markup

estimated_weight_lbs — estimated shipping weight

estimated_usps_shipping — estimated shipping cost

total_cost_with_shipping — listing price plus estimated shipping

The table output includes the following fields:
- keywords
- title
- current_price
- avg_price
- suggested_listing_price
- estimated_weight_lbs
- estimated_usps_shipping
- total_cost_with_shipping
- condition
- seller_username
- item_url
