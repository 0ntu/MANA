from fastapi import FastAPI
import os

app = FastAPI(title="")


@app.get("/")
async def root():
    return {"message": "UF MANA is running"}
@app.get("/healthcheck")
async def healthcheck():
    return {"status": "not exploded"}
