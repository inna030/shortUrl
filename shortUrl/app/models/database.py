import boto3
import logging
import os
from boto3.dynamodb.conditions import Key
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.api import url_router
import uvicorn

from dotenv import load_dotenv
env_path = Path('/Users/innalu/PycharmProjects/shortUrl/.env')
load_dotenv(dotenv_path=env_path)

# Fetch AWS credentials and region from environment variables
aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
region = os.getenv('AWS_REGION')

if not aws_access_key_id or not aws_secret_access_key:
    raise EnvironmentError("AWS credentials are not set in the environment variables.")

# Initialize boto3 session
session = boto3.Session(
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name=region
)



load_dotenv(dotenv_path=env_path)

# Load environment variables from .env file





# Initialize boto3 session

print(f"AWS_ACCESS_KEY_ID: {aws_access_key_id}")
print(f"AWS_SECRET_ACCESS_KEY: {aws_secret_access_key}")
print(f"AWS_REGION: {region}")
if not aws_access_key_id or not aws_secret_access_key:
    raise EnvironmentError("AWS credentials are not set in the environment variables.")

# Initialize DynamoDB resource
dynamodb = session.resource('dynamodb')

# Log credentials for debugging (do not log secrets in production)
credentials = session.get_credentials()
current_credentials = credentials.get_frozen_credentials()
logging.info(f"AWS Access Key ID: {current_credentials.access_key}")
logging.info(f"AWS Region: {session.region_name}")

def query_table():
    """Query the 'urls' table to find items with a specific 'id'."""
    table = dynamodb.Table('urls')
    try:
        response = table.query(
            KeyConditionExpression=Key('id').eq('some-id')
        )
        return response['Items']
    except dynamodb.meta.client.exceptions.ResourceNotFoundException as e:
        logging.error(f"Resource not found: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")

def initialize_db():
    """Create the 'urls' table with specific key schema and indexes."""
    table_definition = {
        'TableName': 'urls',
        'KeySchema': [
            {'AttributeName': 'id', 'KeyType': 'HASH'}
        ],
        'AttributeDefinitions': [
            {'AttributeName': 'id', 'AttributeType': 'S'},
            {'AttributeName': 'short_url', 'AttributeType': 'S'}
        ],
        'GlobalSecondaryIndexes': [
            {
                'IndexName': 'ShortUrlIndex',
                'KeySchema': [
                    {'AttributeName': 'short_url', 'KeyType': 'HASH'}
                ],
                'Projection': {
                    'ProjectionType': 'ALL'
                },
                'ProvisionedThroughput': {
                    'ReadCapacityUnits': 5,
                    'WriteCapacityUnits': 5
                }
            }
        ],
        'ProvisionedThroughput': {
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    }
    try:
        # Create the table
        table = dynamodb.create_table(**table_definition)
        table.meta.client.get_waiter('table_exists').wait(TableName='urls')
        logging.info("Table created successfully.")

        # Enable TTL on the 'expire_date' attribute
        dynamodb.meta.client.update_time_to_live(
            TableName='urls',
            TimeToLiveSpecification={
                'Enabled': True,
                'AttributeName': 'expire_date'
            }
        )
        logging.info("TTL attribute set successfully.")

    except dynamodb.meta.client.exceptions.ResourceInUseException:
        logging.info("Table already exists.")
    except Exception as e:
        logging.error(f"An unexpected error occurred while creating the table: {e}")

def initialize_user_table():
    """Create the 'users' table with specific key schema and indexes."""
    table_definition = {
        'TableName': 'users',
        'KeySchema': [
            {'AttributeName': 'username', 'KeyType': 'HASH'}
        ],
        'AttributeDefinitions': [
            {'AttributeName': 'username', 'AttributeType': 'S'},
            {'AttributeName': 'is_admin', 'AttributeType': 'BOOL'},
            {'AttributeName': 'url_limit', 'AttributeType': 'N'}
        ],
        'ProvisionedThroughput': {
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    }
    try:
        # Create the table
        table = dynamodb.create_table(**table_definition)
        table.meta.client.get_waiter('table_exists').wait(TableName='users')
        logging.info("User table created successfully.")
    except dynamodb.meta.client.exceptions.ResourceInUseException:
        logging.info("User table already exists.")
    except Exception as e:
        logging.error(f"An unexpected error occurred while creating the user table: {e}")

# User-related functions


if __name__ == '__main__':
    initialize_db()
    items = query_table()
    if items:
        print(items)



def update_urls_table():
    """Update the 'urls' table to include additional fields if necessary."""
    table_definition = {
        'TableName': 'urls',
        'AttributeDefinitions': [
            {'AttributeName': 'url_length', 'AttributeType': 'N'},
            {'AttributeName': 'num_special_chars', 'AttributeType': 'N'},
            {'AttributeName': 'domain_age', 'AttributeType': 'N'},
            {'AttributeName': 'content_features', 'AttributeType': 'N'}
        ],
        'GlobalSecondaryIndexes': [
            {
                'IndexName': 'ShortUrlIndex',
                'KeySchema': [
                    {'AttributeName': 'short_url', 'KeyType': 'HASH'}
                ],
                'Projection': {
                    'ProjectionType': 'ALL'
                },
                'ProvisionedThroughput': {
                    'ReadCapacityUnits': 5,
                    'WriteCapacityUnits': 5
                }
            }
        ]
    }
    try:
        dynamodb = session.resource('dynamodb')
        table = dynamodb.Table('urls')
        table.update(**table_definition)
        logging.info("Table updated successfully.")
    except Exception as e:
        logging.error(f"An error occurred while updating the table: {e}")

update_urls_table()
# Create the user_interactions table
def create_user_interactions_table():
    table = dynamodb.create_table(
        TableName='user_interactions',
        KeySchema=[
            {'AttributeName': 'user_id', 'KeyType': 'HASH'},
            {'AttributeName': 'ad_id', 'KeyType': 'RANGE'}
        ],
        AttributeDefinitions=[
            {'AttributeName': 'user_id', 'AttributeType': 'S'},
            {'AttributeName': 'ad_id', 'AttributeType': 'S'}
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    )
    table.meta.client.get_waiter('table_exists').wait(TableName='user_interactions')
    print("Table created successfully.")

create_user_interactions_table()
def calculate_rating(interaction_type):
    interaction_points = {
        'view': 1,
        'click': 3,
        'purchase': 5
    }
    return interaction_points.get(interaction_type, 0)

# Function to record interaction
def record_interaction(user_id, ad_id, interaction_type):
    rating = calculate_rating(interaction_type)

    try:
        response = table.update_item(
            Key={'user_id': user_id, 'ad_id': ad_id},
            UpdateExpression='SET rating = rating + :val',
            ExpressionAttributeValues={':val': rating},
            ReturnValues='UPDATED_NEW'
        )
        logging.info(f"Interaction recorded: {response}")
    except Exception as e:
        logging.error(f"An error occurred while recording interaction: {e}")

# Example usage
record_interaction('user1', 'ad1', 'click')
record_interaction('user1', 'ad1', 'purchase')
