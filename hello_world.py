# Imports
from fastapi import FastAPI

# Create a FastAPI Instance
app = FastAPI()

# Decorator - Path, Route, Endpoint: HTTP Methods
@app.get("/")
async def root():
    return {"message": "Hello World"}