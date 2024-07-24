from fastapi import APIRouter, HTTPException
from app.service.shorten_url import shorten_url, get_original_url, list_urls, update_url
from app.models.model import URL

router = APIRouter()

@router.post("/shorten_url")
def shorten_url_endpoint(request: URL):
    try:
        short_url = shorten_url(request.original_url, request.custom_short_url, request.expire_date)
        return {"short_url": short_url, "original_url": request.original_url}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/list_urls")
def list_urls_endpoint():
    try:
        urls = list_urls()
        return urls
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/redirect/{short_url}")
def redirect_url_endpoint(short_url: str):
    try:
        original_url = get_original_url(short_url)
        return {"original_url": original_url}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/update_url")
def update_url_endpoint(short_url: str, new_original_url: str):
    try:
        short_url, new_original_url = update_url(short_url, new_original_url)
        return {"short_url": short_url, "new_original_url": new_original_url}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
