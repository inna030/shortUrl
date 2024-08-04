import uuid
import boto3
import logging
from datetime import datetime
from boto3.dynamodb.conditions import Key
from app.models.database import dynamodb
import whois
from bs4 import BeautifulSoup
import requests

from app.service.anomaly_detection import detect_anomaly

logging.basicConfig(level=logging.INFO)
table = dynamodb.Table('urls')

def generate_short_url():
    return str(uuid.uuid4())

def shorten_url(original_url, custom_short_url=None, expire_date=None):
    unique_id = generate_short_url()
    domain=".shorten"
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
            short_url = unique_id[25:]+domain
            response = table.query(
                IndexName='ShortUrlIndex',
                KeyConditionExpression=Key('short_url').eq(short_url)
            )

            if not response['Items']:
                break
            unique_id = generate_short_url()

    if expire_date:
        expire_date = int(datetime.strptime(expire_date, '%Y-%m-%d').replace(hour=0, minute=0, second=0).timestamp())
        # Calculate URL length and number of special characters
    url_length = get_url_length(original_url)
    num_special_chars = get_num_special_chars(original_url)

    # Extract domain age and content features
    domain_age = get_domain_age(original_url)
    word_count, num_special_chars_content = extract_content_features(original_url)

    # Check for anomalies using the extracted features
    features = [url_length, num_special_chars, domain_age, word_count]
    if detect_anomaly(features):
        raise ValueError("Malicious URL detected")
    item = {
            'id': unique_id,
            'short_url': short_url,
            'original_url': original_url,
            'expire_date': expire_date,
            'timestamp': str(uuid.uuid4()),
            'url_length': url_length,
            'num_special_chars': num_special_chars,
            'domain_age': domain_age,
            'word_count': word_count,
            'num_special_chars_content': num_special_chars_content,
        }
    table.put_item(Item=item)

    return short_url

def get_original_url(short_url):
    logging.info(f"Querying for short_url: {short_url}")
    response = table.query(
        IndexName='ShortUrlIndex',
        KeyConditionExpression=Key('short_url').eq(short_url)
    )
    logging.info(f"Query response: {response}")

    if response['Items']:
        original_url = response['Items'][0]['original_url']
        logging.info(f"Found original URL: {original_url}")
        return original_url
    else:
        logging.error(f"Short URL '{short_url}' not found.")
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
def list_urls_for_user(username: str):
    try:
        response = table.query(
            IndexName='UsernameIndex',  # Use the appropriate index name
            KeyConditionExpression=Key('username').eq(username)
        )
        return response['Items']
    except Exception as e:
        logging.error(f"An error occurred while querying URLs for user '{username}': {e}")
        raise ValueError(f"An error occurred while querying URLs for user '{username}': {e}")
def get_domain_age(domain_name):
    try:
        domain_info = whois.whois(domain_name)
        creation_date = domain_info.creation_date
        if isinstance(creation_date, list):
            creation_date = creation_date[0]
        domain_age_days = (datetime.now() - creation_date).days
        return domain_age_days
    except Exception as e:
        logging.error(f"Error getting domain age: {e}")
        return None

def extract_content_features(url):
    try:
        response = requests.get(url)
        content = response.text
        soup = BeautifulSoup(content, 'html.parser')
        word_count = len(soup.get_text().split())
        num_special_chars = sum(not c.isalnum() for c in soup.get_text())
        # Additional content features can be added here
        return word_count, num_special_chars
    except Exception as e:
        logging.error(f"Error extracting content features: {e}")
        return None, None

def get_url_length(url):
    return len(url)

def get_num_special_chars(url):
    return sum(not c.isalnum() for c in url)

