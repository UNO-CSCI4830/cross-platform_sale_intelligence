from fastapi import FastAPI

app = FastAPI()

@app.get("/") # This is a decorator for HTML GET. Just "/" is the base page
def root():
    return {"Hello": "World"}

#@app.post("/users") #another decorator for HTML POST. This is for users page, can change as frontend is developed
