# Platform Sale Intelligence
By Group 4

To Run:
1. Clone the repository to your machine.
2. Create and activate a virtual environment(optional, but recommended).<br>
    2.1.1:<br>
    ```Windows: python -m venv venv```<br>
    2.1.2:<br>
    ```Mac/Linux: python3 -m venv venv```<br>
        2.2.1.<br>
        ```Windows: venv\Scripts\activate```<br>
        2.2.2.<br>
        ```Mac/Linux: venv/bin/activate```<br>
3. Use "pip install requirements.txt" to install dependencies
4. Run the FastAPI server with "uvicorn backend.main:app --reload"


# Recent Backend Updates - KL

```FR15 - Added backend API support for reporting system issues. Users can submit an issue using the POST /issues endpoint, and all issues are stored in the SQLite database. The development team can retrieve submitted issues using GET /issues. Endpoints are documented through FastAPI OpenAPI.```<br>

FR14 - Added backend support for updating user account information. Implemented the PUT /users/{user_id} endpoint to allow users to update their email address with validation to ensure the user exists and the email format is valid.<br>

```FR5 - Added backend support for the unified dashboard display. Implemented a Listing data model and a GET /listings/{user_id} endpoint that returns all active listings for a user in a frontend-ready JSON format. Added a temporary development route, GET /test/add-listing, to seed test listing data for dashboard development.```
