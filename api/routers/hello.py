# hello.py

from fastapi import APIRouter

router = APIRouter()

@router.get("/hello/{name}", tags=["hello"])
async def hello_name(name: str):
    return {"message": f"Hello {name}"}

@router.get("/hello", tags=["hello"])
async def hello(name: str = ""):
    return {"message": f"Hello {name}"}
