from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware( 
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
#Allows front end and backend to host locally, will be changed later when we find where we are hostings.

@app.get("/") # This is a decorator for HTML GET. Just "/" is the base page
def root():
    return {"Hello": "World"}

#@app.post("/users") #another decorator for HTML POST. This is for users page, can change as frontend is developed
