from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "API do Pantufo Bot no telegram"}