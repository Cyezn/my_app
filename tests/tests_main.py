
# tests/test_main.py
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_health():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        r = await ac.get("/healthz")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}

@pytest.mark.asyncio
async def test_get_item():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        r = await ac.get("/items/1")
    assert r.status_code == 200
    assert r.json()["name"] == "apple"

@pytest.mark.asyncio
async def test_create_item():
    new_item = {"id": 10, "name": "pear", "price": 1.1}
    async with AsyncClient(app=app, base_url="http://test") as ac:
        r = await ac.post("/items", json=new_item)
    assert r.status_code == 201
    assert r.json()["id"] == 10
