from fastapi import FastAPI

from app.apis import router
from app.database import initialize_indexes, create_admin

app = FastAPI(title="UF MANA API")

app.include_router(router)


@app.on_event("startup")
def on_startup():
    initialize_indexes()
    create_admin()


@app.get("/")
async def root():
    return {"message": "UF MANA is running"}


@app.get("/healthcheck")
async def healthcheck():
    return {"status": "not exploded"}
