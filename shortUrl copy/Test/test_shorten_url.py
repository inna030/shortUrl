import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
from app.service.shorten_url import shorten_url, get_original_url, list_urls, update_url

class TestURLShortener(unittest.TestCase):

    @patch('app.models.database.dynamodb.Table')
    def test_shorten_url(self, mock_table):
        mock_table_instance = mock_table.return_value
        mock_table_instance.query.return_value = {"Items": []}

        original_url = 'https://example.com'
        short_url = shorten_url(original_url)

        self.assertTrue(len(short_url) > 0)
        mock_table_instance.put_item.assert_called_once()

    @patch('app.models.database.dynamodb.Table')
    def test_custom_short_url(self, mock_table):
        mock_table_instance = mock_table.return_value
        mock_table_instance.query.return_value = {"Items": []}

        original_url = 'https://example.com'
        custom_short_url = 'custom1'
        short_url = shorten_url(original_url, custom_short_url)

        self.assertEqual(short_url, custom_short_url)
        mock_table_instance.put_item.assert_called_once()

    @patch('app.models.database.dynamodb.Table')
    def test_shorten_url_with_expire_date(self, mock_table):
        mock_table_instance = mock_table.return_value
        mock_table_instance.query.return_value = {"Items": []}

        original_url = 'https://example.com'
        expire_date = datetime.now().strftime('%Y-%m-%d')
        short_url = shorten_url(original_url, expire_date=expire_date)

        self.assertTrue(len(short_url) > 0)
        mock_table_instance.put_item.assert_called_once()
        args, kwargs = mock_table_instance.put_item.call_args
        self.assertEqual(kwargs['Item']['expire_date'], int(datetime.strptime(expire_date, '%Y-%m-%d').replace(hour=0, minute=0, second=0).timestamp()))

    @patch('app.models.database.dynamodb.Table')
    def test_get_original_url(self, mock_table):
        mock_table_instance = mock_table.return_value

        original_url = 'https://example.com'
        short_url = 'custom1'
        mock_table_instance.query.return_value = {"Items": [{"original_url": original_url}]}

        fetched_url = get_original_url(short_url)
        self.assertEqual(fetched_url, original_url)

    @patch('app.models.database.dynamodb.Table')
    def test_update_url(self, mock_table):
        mock_table_instance = mock_table.return_value

        original_url = 'https://example.com'
        new_original_url = 'https://newexample.com'
        short_url = 'custom1'
        mock_table_instance.query.return_value = {"Items": [{"original_url": original_url}]}

        updated_short_url, updated_new_original_url = update_url(short_url, new_original_url)
        self.assertEqual(updated_new_original_url, new_original_url)
        mock_table_instance.put_item.assert_called_once()

    @patch('app.models.database.dynamodb.Table')
    def test_list_urls(self, mock_table):
        mock_table_instance = mock_table.return_value

        urls = [{"short_url": "short1", "original_url": "https://example.com"}]
        mock_table_instance.scan.return_value = {"Items": urls}

        result = list_urls()
        self.assertEqual(result, urls)

if __name__ == '__main__':
    unittest.main()
