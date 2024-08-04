import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
import os
import logging
from moto import mock_aws
from app.service.shorten_url import shorten_url, get_original_url, list_urls, update_url

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestURLShortener(unittest.TestCase):

    def setUp(self):
        self.check_aws_env_vars()
        self.dynamodb = None

    def check_aws_env_vars(self):
        aws_vars = [
            'AWS_ACCESS_KEY_ID',
            'AWS_SECRET_ACCESS_KEY',
            'AWS_SESSION_TOKEN',
            'AWS_DEFAULT_REGION'
        ]

        for var in aws_vars:
            value = os.environ.get(var)
            if value:
                print(f"{var}: {value}")
            else:
                print(f"{var} is not set")

    def setUpMockDynamoDB(self):
        from boto3 import resource

        self.dynamodb = resource('dynamodb', region_name='us-west-2')

        # Correct the table definition
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

        # Create the mock table
        table = self.dynamodb.create_table(**table_definition)
        table.meta.client.get_waiter('table_exists').wait(TableName='urls')
        logger.info("Table created successfully.")


        self.dynamodb.meta.client.update_time_to_live(
            TableName='urls',
            TimeToLiveSpecification={
                'Enabled': True,
                'AttributeName': 'expire_date'
            }
        )
        logger.info("TTL attribute set successfully.")

    @mock_aws
    def test_shorten_url(self):
        self.setUpMockDynamoDB()

        original_url = 'https://example.com'
        short_url = shorten_url(original_url)

        self.assertTrue(len(short_url) > 0)

    @mock_aws
    def test_custom_short_url(self):
        self.setUpMockDynamoDB()

        original_url = 'https://example.com'
        custom_short_url = 'custom1'
        short_url = shorten_url(original_url, custom_short_url)

        self.assertEqual(short_url, custom_short_url)

    @mock_aws
    def test_shorten_url_with_expire_date(self):
        self.setUpMockDynamoDB()

        original_url = 'https://example.com'
        expire_date = datetime.now().strftime('%Y-%m-%d')
        short_url = shorten_url(original_url, expire_date=expire_date)

        self.assertTrue(len(short_url) > 0)

    @mock_aws
    def test_get_original_url(self):
        self.setUpMockDynamoDB()

        original_url = 'https://example.com'
        short_url = 'custom1'
        table = self.dynamodb.Table('urls')
        table.put_item(Item={
            'id': '1',
            'short_url': short_url,
            'original_url': original_url
        })

        fetched_url = get_original_url(short_url)
        self.assertEqual(fetched_url, original_url)

    @mock_aws
    def test_update_url(self):
        self.setUpMockDynamoDB()

        original_url = 'https://example.com'
        new_original_url = 'https://newexample.com'
        short_url = 'custom1'
        table = self.dynamodb.Table('urls')
        table.put_item(Item={
            'id': '1',
            'short_url': short_url,
            'original_url': original_url
        })

        updated_short_url, updated_new_original_url = update_url(short_url, new_original_url)
        self.assertEqual(updated_new_original_url, new_original_url)

    @mock_aws
    def test_list_urls(self):
        self.setUpMockDynamoDB()

        table = self.dynamodb.Table('urls')
        urls = [
            {"id": "1", "short_url": "short1", "original_url": "https://example.com"},
            {"id": "2", "short_url": "short2", "original_url": "https://example2.com"}
        ]
        for url in urls:
            table.put_item(Item=url)

        result = list_urls()

        expected_result = [
            {"id": "1", "short_url": "short1", "original_url": "https://example.com"},
            {"id": "2", "short_url": "short2", "original_url": "https://example2.com"}
        ]
        self.assertEqual(result, expected_result)

if __name__ == '__main__':
    unittest.main()
