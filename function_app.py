import azure.functions as func 
from fastapi import FastAPI
from api.routers import hello

# http://localhost:7071/ or http://localhost:7071/docs

fast_app = FastAPI() 
fast_app.include_router(hello.router)

@fast_app.get("/")
async def root():
    return {"message":"Hello world"}

app = func.AsgiFunctionApp(app=fast_app, http_auth_level=func.AuthLevel.ANONYMOUS)
