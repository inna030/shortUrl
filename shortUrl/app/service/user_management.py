from passlib.context import CryptContext
from fastapi import HTTPException
from app.models.model import User
from app.models.database import dynamodb
from boto3.dynamodb.conditions import Key

table = dynamodb.Table('users')
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_current_user() -> User:
    # Placeholder implementation
    return User(username="testuser", is_admin=False)

def get_current_admin_user() -> User:
    user = get_current_user()
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized as admin")
    return user

def save_user_to_db(username: str, password: str, default_url_limit: int = 20):
    hashed_password = pwd_context.hash(password)
    item = {
        'username': username,
        'password': hashed_password,
        'url_limit': default_url_limit,
        'created_urls': 0,
        'is_admin': False
    }
    try:
        table.put_item(Item=item)
        print(f"User {username} saved to the database.")
    except Exception as e:
        print(f"Error saving user: {e}")

def update_user_password(username: str, new_password: str):
    hashed_password = pwd_context.hash(new_password)
    try:
        table.update_item(
            Key={'username': username},
            UpdateExpression='SET password = :val1',
            ExpressionAttributeValues={':val1': hashed_password}
        )
        print(f"Password for user {username} updated.")
    except Exception as e:
        print(f"Error updating password: {e}")

def update_user_created_urls_count(username: str, new_count: int):
    try:
        table.update_item(
            Key={'username': username},
            UpdateExpression='SET created_urls = :val1',
            ExpressionAttributeValues={':val1': new_count}
        )
        print(f"Created URLs count for user {username} updated to {new_count}.")
    except Exception as e:
        print(f"Error updating created URLs count: {e}")

def update_url_limit_for_user(username: str, new_limit: int):
    try:
        table.update_item(
            Key={'username': username},
            UpdateExpression='SET url_limit = :val1',
            ExpressionAttributeValues={':val1': new_limit}
        )
        print(f"URL limit for user {username} updated to {new_limit}.")
    except Exception as e:
        print(f"Error updating URL limit: {e}")