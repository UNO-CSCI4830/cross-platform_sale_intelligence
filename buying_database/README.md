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

The database is now ready for ingestion logic.

