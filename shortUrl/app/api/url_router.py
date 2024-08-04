from fastapi import APIRouter, Depends
from app.service.shorten_url import *
from app.models.model import *
from app.service.user_management import *

from app.service.ad_recommendation import recommend_ads, train_ad_recommendation_model, record_interaction
from fastapi.responses import RedirectResponse
from passlib.context import CryptContext

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/create_user")
def create_user(request: CreateUserRequest):
    hashed_password = pwd_context.hash(request.password)
    save_user_to_db(request.username, hashed_password, default_url_limit=20)
    return {"message": f"User '{request.username}' created successfully."}

@router.get("/list_urls")
def list_urls_endpoint(current_user: User = Depends(get_current_admin_user)):
    try:
        urls = list_urls()
        return urls
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list_my_urls")
def list_my_urls_endpoint(current_user: User = Depends(get_current_user)):
    try:
        urls = list_urls_for_user(current_user.username)  # Implement list_urls_for_user
        return urls
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/create_url")
def create_url(request: URL, current_user: User = Depends(get_current_user)):
    if current_user.created_urls >= current_user.url_limit:
        raise HTTPException(status_code=403, detail="URL creation limit reached.")

    try:
        short_url = shorten_url(request.original_url, request.custom_short_url, request.expire_date)
        current_user.created_urls += 1
        update_user_created_urls_count(current_user.username, current_user.created_urls)
        return {"short_url": short_url, "original_url": request.original_url}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))



@router.post("/update_url")
def update_url_endpoint(short_url: str, new_original_url: str, current_user: User = Depends(get_current_user)):
    try:
        short_url, new_original_url = update_url(short_url, new_original_url)
        return {"short_url": short_url, "new_original_url": new_original_url}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/redirect/{short_url}")
def redirect_url_endpoint(short_url: str):
    try:
        original_url = get_original_url(short_url)
        return RedirectResponse(url=original_url)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/change_password")
def change_password(request: ChangePasswordRequest, current_user: User = Depends(get_current_user)):
    # Verify the old password
    if not pwd_context.verify(request.old_password, current_user.password):
        raise HTTPException(status_code=403, detail="Old password is incorrect.")

    # Hash the new password
    new_hashed_password = pwd_context.hash(request.new_password)

    # Update the user's password in the database
    try:
        update_user_password(current_user.username, new_hashed_password)
        return {"message": "Password changed successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating password: {str(e)}")

@router.post("/update_url_limit")
def update_url_limit_endpoint(request: UpdateURLLimitRequest, current_user: User = Depends(get_current_admin_user)):
    try:
        update_url_limit_for_user(request.username, request.new_limit)
        return {"message": f"Limit updated successfully for '{request.username}'."}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/validate_url")
def validate_url_endpoint(url_data: dict):
    features = [url_data['url_length'], url_data['num_special_chars'], url_data['domain_age'], url_data['content_features']]
    if validate_url(features) == 1:
        raise HTTPException(status_code=403, detail="Malicious URL detected")
    return {"message": "URL is safe"}

@router.post("/record_interaction")
def record_interaction_endpoint(user_id: str, ad_id: str, interaction_type: str):
    try:
        record_interaction(user_id, ad_id, interaction_type)
        return {"message": "Interaction recorded successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/train_ad_recommendation")
def train_ad_recommendation_endpoint():
    try:
        train_ad_recommendation_model()
        return {"message": "Ad recommendation model trained successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/recommend_ads")
def recommend_ads_endpoint(user_id: str, ad_ids: list):
    try:
        recommendations = recommend_ads(user_id, ad_ids)
        return {"recommendations": recommendations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))