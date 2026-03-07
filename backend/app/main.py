from fastapi import FastAPI
import os


app = FastAPI(title="Mana calc API")
frontend

@app.get("/")
async def root():
    return {"message": "UF MANA running."}
    
@app.get("/healthcheck")
async def health_check():
    return {"status": "Not exploded."}
    
