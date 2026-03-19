from fastapi import FastAPI
import os

app = FastAPI(title="UF MANA API")


@app.get("/")
async def root():
    return {"message": "UF MANA is running"}
@app.get("/healthcheck")
async def healthcheck():
    return {"status": "not exploded"}
