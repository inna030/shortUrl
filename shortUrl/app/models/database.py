import boto3
import logging

logging.basicConfig(level=logging.INFO)

dynamodb = boto3.resource('dynamodb', region_name='us-west-2')

def initialize_db():
    table_definition = {
        'TableName': 'urls',
        'KeySchema': [
            {'AttributeName': 'id', 'KeyType': 'HASH'}
        ],
        'AttributeDefinitions': [
            {'AttributeName': 'id', 'AttributeType': 'S'},
            {'AttributeName': 'short_url', 'AttributeType': 'S'},
            {'AttributeName': 'original_url', 'AttributeType': 'S'},
            {'AttributeName': 'expire_date', 'AttributeType': 'N'},
            {'AttributeName': 'timestamp', 'AttributeType': 'S'},
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
        table = dynamodb.create_table(**table_definition)
        table.meta.client.get_waiter('table_exists').wait(TableName='urls')
        logging.info("Table created successfully.")

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

if __name__ == '__main__':
    initialize_db()
