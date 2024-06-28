import uuid
import boto3
from datetime import datetime
from boto3.dynamodb.conditions import Key
from app.models.database import dynamodb

table = dynamodb.Table('urls')

def generate_short_url():
    return str(uuid.uuid4())

def shorten_url(original_url, custom_short_url=None, expire_date=None):
    unique_id = generate_short_url()
    if custom_short_url:
        response = table.query(
            IndexName='ShortUrlIndex',
            KeyConditionExpression=Key('short_url').eq(custom_short_url)
        )

        if response['Items']:
            raise ValueError("Short URL already exists.")

        short_url = custom_short_url
    else:
        while True:
            short_url = unique_id[:8]
            response = table.query(
                IndexName='ShortUrlIndex',
                KeyConditionExpression=Key('short_url').eq(short_url)
            )

            if not response['Items']:
                break
            unique_id = generate_short_url()


    if expire_date:
        expire_date = int(datetime.strptime(expire_date, '%Y-%m-%d').replace(hour=0, minute=0, second=0).timestamp())

    item = {
        'id': unique_id,
        'short_url': short_url,
        'original_url': original_url,
        'expire_date': expire_date,
        'timestamp': str(uuid.uuid4()),
    }
    table.put_item(Item=item)

    return short_url

def get_original_url(short_url):
    response = table.query(
        IndexName='ShortUrlIndex',
        KeyConditionExpression=Key('short_url').eq(short_url)
    )
    if response['Items']:
        return response['Items'][0]['original_url']
    else:
        raise ValueError("Short URL not found.")

def list_urls():
    response = table.scan()
    return response['Items']

def update_url(short_url, new_original_url):
    response = table.query(
        IndexName='ShortUrlIndex',
        KeyConditionExpression=Key('short_url').eq(short_url)
    )
    if not response['Items']:
        raise ValueError("Short URL not found.")

    item = response['Items'][0]
    item['original_url'] = new_original_url
    table.put_item(Item=item)

    return short_url, new_original_url
