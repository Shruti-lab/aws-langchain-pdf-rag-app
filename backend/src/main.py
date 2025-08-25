import uvicorn
from fastapi import FastAPI

app = FastAPI()

PORT = 8080

@app.get("/")
async def root():
    return {"message": "Hello, World!"}

def start():
    """Launched with `poetry run start` at root level"""
    uvicorn.run(app, host="0.0.0.0", port=PORT, reload=True)